# WhatsApp SaaS Core

Multi-tenant WhatsApp management platform built on the Meta WhatsApp Cloud API.

- **Backend** — FastAPI · SQLAlchemy 2.x · Alembic · PostgreSQL · JWT
- **Frontend** — React · Vite · Tailwind · React Query · Zustand · React Router
- **Deployment** — Dockerized, Terraform-ready, queue-ready

## Quick start (Docker)

```bash
cd whatsapp-saas
docker compose up --build
```

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:3000        |
| Backend   | http://localhost:8000        |
| API docs  | http://localhost:8000/docs   |
| Health    | http://localhost:8000/health |

The backend container runs `alembic upgrade head` on start, so the schema is
created automatically.

## Local development

### Backend

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit values
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Architecture

```
backend/app/
├── api/          HTTP routes (v1 + webhooks) — thin controllers
├── auth/         JWT, password hashing, dependency guards
├── core/         config, logging, encryption, error handling
├── db/           engine, session, declarative base
├── models/       SQLAlchemy ORM models
├── repositories/ tenant-scoped data access
├── schemas/      Pydantic request/response models
├── services/     business logic
│   └── integrations/meta/   ALL Meta-specific logic lives here
└── workers/      queue-ready placeholder (see workers/README.md)
```

### Multi-tenancy

Every tenant-scoped query goes through `TenantScopedRepository`, which pins
`tenant_id` on every `SELECT`. Controllers derive `tenant_id` only from the
authenticated JWT (`current_user.tenant_id`) — it is never accepted from
client input. See `backend/app/repositories/base.py`.

### Meta integration boundary

Controllers and services never touch `httpx` or Graph API URLs directly. All
Meta logic is confined to `services/integrations/meta/`:

- `client.py` — HTTP transport + error normalization
- `whatsapp.py` — `WhatsAppService` (numbers, templates, sending)
- `signature.py` — webhook `X-Hub-Signature-256` verification

This keeps Meta swappable and the rest of the app testable.

### Security

- JWT auth with expiry · bcrypt password hashing
- WhatsApp credentials (access token, app secret) encrypted at rest (Fernet)
- Secrets never returned in API responses or logs
- Webhook signature verification against the raw request body
- CORS configured via `CORS_ORIGINS`
- Standardized error envelope: `{ "success": false, "error": { code, message } }`

## Webhooks

| Method | Path            | Purpose                                   |
|--------|-----------------|-------------------------------------------|
| GET    | `/webhooks/meta`| Subscription verification challenge       |
| POST   | `/webhooks/meta`| Event ingestion (signature-verified)      |

POST persists the raw payload immediately and returns `200`. Heavier
processing is deferred — see `backend/app/workers/README.md`.

## Environment variables

### Backend (`backend/.env`)

| Variable             | Description                                      |
|----------------------|--------------------------------------------------|
| `DATABASE_URL`       | PostgreSQL DSN (`postgresql+psycopg://…`)         |
| `JWT_SECRET`         | JWT signing secret                                |
| `ENCRYPTION_KEY`     | Fernet key, or any string (a key is derived)      |
| `META_GRAPH_VERSION` | Graph API version (default `v22.0`)               |
| `CORS_ORIGINS`       | Comma-separated allowed origins                   |
| `REDIS_URL`          | Optional, for the future queue                    |

### Frontend (`frontend/.env`)

| Variable       | Description           |
|----------------|-----------------------|
| `VITE_API_URL` | Backend base URL      |

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for the full guide:

- **Frontend** → Cloudflare Pages, deployed automatically by GitHub Actions
  ([`.github/workflows/deploy-frontend.yml`](.github/workflows/deploy-frontend.yml)).
- **Backend** → AWS Lambda + API Gateway, with PostgreSQL on RDS — recommended
  architecture, required backend changes, and a Terraform layout.

## Status

MVP scope: tenant + user management, credential storage, number/template sync,
template sending, conversation logging, webhook verification, mock subscription
pages. No billing integration, no template creation, no queue worker yet — the
architecture leaves clean seams for all of these.
