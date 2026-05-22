# Workers (queue-ready placeholder)

The MVP runs without a queue. This package is the seam where asynchronous
processing will land so it can be added without touching controllers.

## Current behavior

Webhook events are persisted by `WebhookService.ingest()` and a lightweight
subset (conversation events) is recorded synchronously. The endpoint still
returns `200` immediately.

## Planned migration to a queue

1. `WebhookService.ingest()` persists the raw `WebhookEvent` and enqueues its
   id (Redis / RQ / Celery — `REDIS_URL` is already configured).
2. A worker process here consumes the queue and runs:
   - delivery-status reconciliation
   - inbound message routing / AI handling
   - campaign + flow-engine triggers
3. Outbound sends (`MessageService.send_template`) move behind the same queue
   for rate-limit handling and retries.

No controller or service interface needs to change — only the body of
`ingest()` and the addition of a worker entrypoint (`app/workers/main.py`).
