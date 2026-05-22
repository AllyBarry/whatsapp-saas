"""Meta webhook endpoints (outside /api/v1 — called by Meta, not the SPA)."""
from fastapi import APIRouter, Header, Query, Request, Response
from fastapi.responses import PlainTextResponse

from app.api.deps import DbSession
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/meta")
def verify_webhook(
    db: DbSession,
    mode: str | None = Query(default=None, alias="hub.mode"),
    token: str | None = Query(default=None, alias="hub.verify_token"),
    challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    """Meta subscription verification handshake."""
    result = WebhookService(db).verify_challenge(mode, token, challenge)
    if result is None:
        return PlainTextResponse("Forbidden", status_code=403)
    return PlainTextResponse(result, status_code=200)


@router.post("/meta")
async def receive_webhook(
    request: Request,
    db: DbSession,
    x_hub_signature_256: str | None = Header(default=None),
):
    """Ingest a webhook event.

    Uses the raw request body for signature verification, persists the event,
    and returns 200 immediately. No synchronous business logic — heavier
    processing is deferred to workers (queue-ready).
    """
    raw_body = await request.body()
    WebhookService(db).ingest(raw_body, x_hub_signature_256)
    return Response(status_code=200)
