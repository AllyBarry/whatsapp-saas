# AWS Deployment Guide

Target architecture: **static frontend on Cloudflare Pages**, **backend on
Lambda behind API Gateway**, **PostgreSQL on RDS**. The frontend deploys via
GitHub Actions ([`.github/workflows/deploy-frontend.yml`](.github/workflows/deploy-frontend.yml));
the AWS backend is a recommendation — no infrastructure code is committed yet.
This document describes the architecture, the backend changes required, a
step-by-step rollout, and a Terraform layout to implement it.

---

## 1. Architecture overview

```
                  ┌──────────────────────┐
   Browser ──────▶│  Cloudflare Pages    │   static SPA (React build)
        │         │  app.yourdomain.com  │   deployed by GitHub Actions
        │         └──────────────────────┘
        │  XHR /api/*  (CORS)
        ▼
   ┌─────────────────────┐
   │  API Gateway        │   api.yourdomain.com
   │  (HTTP API)         │
   └──────────┬──────────┘
              ▼
   ┌─────────────────────┐
   │  Lambda (FastAPI via│◀── webhook ── Meta
   │  Mangum, container) │
   └──────────┬──────────┘
              │ VPC (private subnets)
   ┌──────────┼───────────────────────────┐
   ▼          ▼                           ▼
 RDS        Secrets Manager           NAT Gateway
 PostgreSQL (DB creds, JWT,           (egress to
 via Proxy   ENCRYPTION_KEY)          graph.facebook.com)
```

The frontend lives entirely on **Cloudflare Pages** (separate from AWS) and
calls the API Gateway domain directly over XHR. Because the SPA and the API are
on different origins, **CORS must be configured** on the backend — see §2.6.

| Concern              | Service                                                |
|----------------------|--------------------------------------------------------|
| Frontend hosting     | Cloudflare Pages (static SPA, deployed via GitHub Actions) |
| Backend compute      | Lambda (container image from ECR)                      |
| HTTP routing         | API Gateway HTTP API (`$default` stage)                |
| Database             | RDS PostgreSQL (`db.t4g.small`, Multi-AZ in prod)      |
| DB connection pooling| RDS Proxy                                              |
| Secrets              | AWS Secrets Manager                                    |
| Outbound to Meta     | NAT Gateway in a public subnet                         |
| Schema migrations    | One-off "migration" Lambda (same image, alt handler)   |
| Async webhook work   | SQS queue (when the queue worker lands)                |
| Logs / metrics       | CloudWatch Logs + Lambda metrics                       |
| Frontend TLS / domain| Cloudflare (automatic TLS + DNS for the Pages domain)  |
| API TLS / domain     | ACM certificate on an API Gateway custom domain        |

---

## 2. Backend changes required for Lambda

The FastAPI app runs unchanged behind an ASGI-to-Lambda adapter. Required
additions (small, non-breaking):

### 2.1 Add the Lambda adapter

`requirements.txt`:

```
mangum==0.19.0
```

New file `backend/app/lambda_handler.py`:

```python
"""AWS Lambda entrypoint — wraps the ASGI app for API Gateway."""
from mangum import Mangum
from app.main import app

# API Gateway HTTP API payload v2.0. Mangum base64-decodes binary bodies,
# so request.body() in the webhook route still yields the exact raw bytes
# needed for X-Hub-Signature-256 verification.
handler = Mangum(app, lifespan="off")
```

`lifespan="off"` is important: the `@app.on_event("startup")` hook does not run
meaningfully per-invocation on Lambda, and lifespan events can hang the adapter.

### 2.2 Lambda container Dockerfile

Lambda has a 250 MB unzipped limit for zip packages; `cryptography` + `psycopg`
binaries make a container image the simpler choice. Add
`backend/Dockerfile.lambda`:

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . ${LAMBDA_TASK_ROOT}/

# CMD is the "module.function" handler; overridden by the migration function.
CMD ["app.lambda_handler.handler"]
```

### 2.3 Do NOT run migrations on cold start

The current `docker-compose` Dockerfile runs `alembic upgrade head` in `CMD` —
correct for local, **wrong for Lambda** (runs on every cold start, races across
concurrent inits). Instead, deploy a second Lambda function from the *same
image* with the handler overridden to a migration entrypoint:

`backend/app/migrate_handler.py`:

```python
"""One-off migration handler — invoke manually or from CI after deploy."""
from alembic import command
from alembic.config import Config

def handler(event, context):
    command.upgrade(Config("alembic.ini"), "head")
    return {"status": "migrated"}
```

Invoke it once per deploy (`aws lambda invoke`) as a CI step, before shifting
traffic.

### 2.4 Database connections on Lambda

Lambda concurrency multiplies DB connections — 100 concurrent executions each
opening a pool will exhaust a small RDS instance. Mitigations:

1. **Use RDS Proxy** (recommended). Lambda connects to the proxy endpoint; the
   proxy multiplexes a small pool of real connections. `DATABASE_URL` points at
   the proxy.
2. Keep the SQLAlchemy engine at **module scope** (it already is in
   `app/db/session.py`) so warm invocations reuse it.
3. Set a tiny pool in `session.py` for the Lambda path:
   `create_engine(url, pool_size=1, max_overflow=1, pool_pre_ping=True)`.

### 2.5 Configuration via environment + Secrets Manager

`Settings` already reads env vars (`app/core/config.py`). On Lambda:

- Non-secret values (`META_GRAPH_VERSION`, `ENVIRONMENT`, `CORS_ORIGINS`) →
  Lambda environment variables.
- Secrets (`JWT_SECRET`, `ENCRYPTION_KEY`, DB password) → **Secrets Manager**.
  Either inject them as env vars at deploy time, or fetch at cold start. The
  `ENCRYPTION_KEY` must be **stable forever** — rotating it makes every stored
  WhatsApp credential undecryptable. Treat it as a permanent secret.

### 2.6 CORS

The SPA (Cloudflare Pages) and the API (API Gateway) are on **different
origins**, so CORS is required. Set the Lambda environment variable
`CORS_ORIGINS` to the Cloudflare Pages production URL — and any custom domain
and `*.pages.dev` preview URLs you want to allow:

```
CORS_ORIGINS=https://app.yourdomain.com,https://whatsapp-saas-frontend.pages.dev
```

The app already wires `CORSMiddleware` from this value (`app/main.py` +
`app/core/config.py`); no code change is needed. Credentialed requests require
explicit origins (no `*`), which the current configuration satisfies.

---

## 3. Networking

| Subnet tier      | Contents                          | Routing                         |
|------------------|-----------------------------------|---------------------------------|
| Public (2 AZs)   | NAT Gateway                       | → Internet Gateway              |
| Private (2 AZs)  | Lambda ENIs, RDS, RDS Proxy       | → NAT Gateway for egress        |

- **Lambda runs in the private subnets** so it can reach RDS. VPC-attached
  Lambda has no public IP, so outbound calls to `graph.facebook.com`
  (number/template sync, sending) route through the **NAT Gateway**.
- Add **VPC endpoints** for Secrets Manager and CloudWatch Logs to keep that
  traffic off the NAT and reduce cost.
- **Security groups:**
  - Lambda SG → outbound 443 (Meta) + 5432 to the RDS Proxy SG.
  - RDS Proxy SG / RDS SG → inbound 5432 only from the Lambda SG.
  - RDS is **not publicly accessible**.

> NAT Gateway is ~$32/mo plus data processing. It is the simplest reliable way
> to give the backend outbound internet. One NAT (single AZ) is fine for
> non-prod; use one per AZ for production HA.

---

## 4. Frontend deployment (Cloudflare Pages via GitHub Actions)

The frontend is built and deployed by
[`.github/workflows/deploy-frontend.yml`](.github/workflows/deploy-frontend.yml).
The workflow runs on every push to `main` that touches `frontend/**` (and can
be triggered manually with **Run workflow**). It runs `npm ci`,
`npm run build`, and `wrangler pages deploy dist`.

### One-time setup

1. **Create the Pages project.** In the Cloudflare dashboard, create a Pages
   project (e.g. `whatsapp-saas-frontend`) using **Direct Upload** — the
   GitHub Actions workflow pushes the build, so do *not* connect it to Git.
2. **Create an API token** with the *Cloudflare Pages → Edit* permission.
3. **Configure the GitHub repository** (Settings → Secrets and variables →
   Actions):

   | Kind     | Name                       | Value                                  |
   |----------|----------------------------|----------------------------------------|
   | Secret   | `CLOUDFLARE_API_TOKEN`     | the Pages-edit API token               |
   | Secret   | `CLOUDFLARE_ACCOUNT_ID`    | your Cloudflare account id              |
   | Variable | `CLOUDFLARE_PAGES_PROJECT` | the Pages project name                 |
   | Variable | `VITE_API_URL`             | backend API base URL, e.g. `https://api.yourdomain.com` |

4. **Custom domain (optional).** Add `app.yourdomain.com` to the Pages project;
   Cloudflare issues and renews TLS automatically.

### Notes

- `VITE_API_URL` is baked into the build at compile time. The axios client
  calls `${VITE_API_URL}/api/v1/...`, so it must point at the API Gateway
  origin. Changing it requires a rebuild (a new workflow run).
- **SPA routing** is handled by `frontend/public/_redirects` (`/* /index.html
  200`), which Vite ships into `dist/`. Cloudflare Pages serves deep links
  correctly without extra configuration.
- Pushes to `main` deploy to production (`--branch=main`). To get preview
  deployments for pull requests, add a `pull_request` trigger and drop the
  `--branch` flag so Cloudflare assigns a preview URL.

---

## 5. Webhook specifics on API Gateway

- API Gateway HTTP API forwards the request body; Mangum reconstructs the exact
  bytes (base64-decoding if needed). `WebhookService.ingest()` keeps working
  against the raw body, so `X-Hub-Signature-256` verification is unaffected.
- Configure Meta's webhook callback URL to
  `https://app.yourdomain.com/webhooks/meta`.
- The POST handler returns `200` immediately. When the queue worker is added
  (see `backend/app/workers/README.md`), `ingest()` should publish to **SQS**
  and a separate Lambda (SQS trigger) does the heavy processing.

---

## 6. Step-by-step rollout

1. **Provision AWS infra** (Terraform — see §7): VPC, subnets, NAT, RDS, RDS
   Proxy, ECR repo, API Gateway, Lambda functions, Secrets Manager entries, IAM
   roles. (The frontend has no AWS footprint — it lives on Cloudflare Pages.)
2. **Build & push the backend image:**
   ```bash
   aws ecr get-login-password | docker login --username AWS --password-stdin <acct>.dkr.ecr.<region>.amazonaws.com
   docker build -f backend/Dockerfile.lambda -t whatsapp-saas-backend backend/
   docker tag whatsapp-saas-backend:latest <ecr-repo>:<git-sha>
   docker push <ecr-repo>:<git-sha>
   ```
3. **Update the API + migration Lambda** to the new image tag.
4. **Run migrations:** `aws lambda invoke --function-name whatsapp-saas-migrate out.json`
5. **Deploy the frontend:** push to `main` (or run the workflow manually) —
   GitHub Actions builds and deploys to Cloudflare Pages (§4). Ensure the
   `VITE_API_URL` variable points at the API Gateway domain first.
6. **Smoke test:** hit `https://api.yourdomain.com/health`, then load the
   Cloudflare Pages URL and complete a register/login round-trip.

---

## 7. Terraform layout (recommended)

Keep infrastructure in an `infra/` directory, split into modules so each
concern is independently reviewable:

```
infra/
├── main.tf            # provider, backend (S3 state + DynamoDB lock)
├── variables.tf       # region, env, domain, db sizing
├── outputs.tf         # CloudFront URL, API URL, ECR repo
├── network.tf         # VPC, subnets, IGW, NAT, route tables, VPC endpoints
├── database.tf        # RDS PostgreSQL, RDS Proxy, subnet group, SGs
├── secrets.tf         # Secrets Manager: JWT_SECRET, ENCRYPTION_KEY, db creds
├── backend.tf         # ECR repo, API + migration Lambda, API Gateway,
│                      #   API Gateway custom domain + ACM cert + Route 53, IAM
└── environments/
    ├── staging.tfvars
    └── production.tfvars
```

The frontend is **not** managed by Terraform — it is deployed to Cloudflare
Pages by GitHub Actions (§4). The only cross-over is the `VITE_API_URL` GitHub
variable, which must match the API Gateway domain that Terraform provisions.

Notes:
- Store Terraform **state in S3** with **DynamoDB locking**.
- The Lambda functions reference an **image tag** passed as a variable; CI sets
  it to the git SHA so `terraform apply` deploys a specific build.
- Generate `ENCRYPTION_KEY` **once** (`Fernet.generate_key()`), store it in
  Secrets Manager, and mark it with `lifecycle { ignore_changes = [...] }` /
  `prevent_destroy` so Terraform never regenerates it.
- Use one state per environment (`staging`, `production`) via `*.tfvars` +
  separate state keys.

---

## 8. CI/CD outline

Two GitHub Actions workflows, split by path so each side deploys independently:

**Frontend — `deploy-frontend.yml` (implemented).**
Triggered by pushes to `main` under `frontend/**`. Runs `npm ci`,
`npm run build`, and `wrangler pages deploy` to Cloudflare Pages. See §4.

**Backend — `deploy-backend.yml` (to add).**
Triggered by pushes to `main` under `backend/**`:

1. Run backend tests.
2. Build and push the backend container image to ECR (tag = git SHA).
3. `terraform apply` with the new image tag → updates the API Lambda.
4. Invoke the migration Lambda (`aws lambda invoke`).

Promote staging → production by applying the same image tag with
`production.tfvars`. Keeping the two workflows separate means a frontend change
never triggers a backend `terraform apply`, and vice versa.

---

## 9. Indicative monthly cost (low traffic, single region)

| Item                         | Estimate (USD/mo) |
|------------------------------|-------------------|
| RDS `db.t4g.small`, single-AZ| ~$25              |
| RDS Proxy                    | ~$15              |
| NAT Gateway (1)              | ~$32 + data       |
| Lambda                       | <$5 (free tier)   |
| API Gateway HTTP API         | <$5               |
| Cloudflare Pages (frontend)  | $0 (free tier)    |
| Secrets Manager              | ~$1               |
| **Total**                    | **~$85–105**      |

Largest cost drivers are RDS, RDS Proxy and NAT. For staging, drop RDS Proxy
(use a tiny pool) and run a single-AZ NAT to cut roughly $40/mo. Cloudflare
Pages' free tier (unlimited static requests, 500 builds/mo) comfortably covers
the frontend — and builds run in GitHub Actions, not against that quota.

---

## 10. Production hardening checklist

- [ ] RDS Multi-AZ + automated backups + deletion protection
- [ ] RDS storage encryption (KMS) and `rds.force_ssl = 1`
- [ ] Secrets Manager rotation for the DB password (NOT `ENCRYPTION_KEY`)
- [ ] Cloudflare WAF + rate limiting in front of the Pages site
- [ ] AWS WAF on the API Gateway stage (rate limiting, common rule set)
- [ ] Lock `CORS_ORIGINS` to known frontend domains only (no `*`)
- [ ] Lambda reserved concurrency to cap DB connection fan-out
- [ ] CloudWatch alarms: Lambda errors/throttles, RDS CPU/connections, 5xx rate
- [ ] Structured logs already emitted by the app → CloudWatch Logs Insights
- [ ] Least-privilege IAM roles per Lambda
- [ ] API Gateway access logging + throttling limits
- [ ] Separate AWS accounts (or at least VPCs) for staging vs production
- [ ] `ENVIRONMENT=production` so future env-gated behavior is correct

---

## 11. Notable trade-offs

- **Lambda vs ECS/Fargate.** Lambda is the right call for spiky multi-tenant
  SaaS traffic and matches the queue-ready design. If a long-running worker or
  websockets are needed later, add a Fargate service rather than forcing it
  into Lambda.
- **Cold starts.** A container-image Lambda in a VPC has a noticeable cold
  start (~1–3 s). Acceptable for a dashboard API; for webhooks, Meta retries on
  timeout. Provisioned concurrency removes it at extra cost if needed.
- **RDS vs Aurora Serverless v2.** RDS provisioned is chosen here for the
  cheapest predictable cost. Revisit Aurora Serverless v2 if load becomes
  bursty enough that a fixed instance is consistently over- or under-sized.
