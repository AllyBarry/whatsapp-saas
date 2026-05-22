"""Meta webhook handling.

Webhooks are tenant-agnostic at the URL level (`/webhooks/meta`). The tenant
is resolved from the payload's WABA id (POST) or the verify token (GET) by
matching against stored credentials. Signature verification and raw-payload
persistence happen here; downstream business processing is intentionally
deferred (queue-ready) so the endpoint can return 200 immediately.
"""
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.encryption import decrypt
from app.core.logging import get_logger, log_event
from app.models.conversation import EventDirection
from app.models.webhook import WebhookEvent
from app.models.whatsapp import WhatsAppCredential
from app.repositories.conversation import ConversationRepository
from app.repositories.webhook import WebhookRepository
from app.services.integrations.meta import verify_signature

logger = get_logger("app.webhooks")


class WebhookService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WebhookRepository(db)

    # --- GET: subscription verification ---------------------------------
    def verify_challenge(self, mode: str | None, token: str | None, challenge: str | None):
        """Return the challenge string if a credential's verify token matches."""
        if mode != "subscribe" or not token or not challenge:
            return None
        stmt = select(WhatsAppCredential).where(WhatsAppCredential.verify_token == token)
        match = self.db.scalars(stmt).first()
        if match is None:
            log_event(logger, "warning", "Webhook verify token did not match")
            return None
        log_event(logger, "info", "Webhook verified", tenant_id=str(match.tenant_id))
        return challenge

    # --- POST: event ingestion ------------------------------------------
    def ingest(self, raw_body: bytes, signature_header: str | None) -> None:
        """Persist a webhook event. Always best-effort; never raises to caller."""
        try:
            payload = json.loads(raw_body or b"{}")
        except json.JSONDecodeError:
            payload = {}

        credential = self._resolve_credential(payload)
        signature_valid = False
        if credential is not None:
            signature_valid = verify_signature(
                app_secret=decrypt(credential.app_secret_encrypted),
                raw_body=raw_body,
                signature_header=signature_header,
            )

        normalized = _normalize(payload)
        event = WebhookEvent(
            tenant_id=credential.tenant_id if credential else None,
            signature_valid=signature_valid,
            raw_payload=payload,
            normalized=normalized,
            object_type=payload.get("object"),
            processed=False,
        )
        self.repo.add(event)

        log_event(
            logger, "info", "Webhook received",
            object_type=payload.get("object"),
            signature_valid=signature_valid,
            tenant_resolved=credential is not None,
        )

        # Mirror delivery statuses onto conversations. Kept lightweight; heavier
        # processing belongs in a worker (see app/workers/).
        if credential is not None and signature_valid:
            self._record_conversation_events(credential.tenant_id, normalized)
            event.processed = True
        self.db.flush()

    def _resolve_credential(self, payload: dict) -> WhatsAppCredential | None:
        """Match the payload's WABA id to a stored credential."""
        for entry in payload.get("entry", []):
            waba_id = entry.get("id")
            if not waba_id:
                continue
            stmt = select(WhatsAppCredential).where(WhatsAppCredential.waba_id == waba_id)
            credential = self.db.scalars(stmt).first()
            if credential is not None:
                return credential
        return None

    def _record_conversation_events(self, tenant_id, normalized: dict) -> None:
        conversations = ConversationRepository(self.db, tenant_id)
        for msg in normalized.get("messages", []):
            number = msg.get("from")
            if not number:
                continue
            conversation = conversations.get_or_create(number)
            conversations.add_event(
                conversation.id,
                event_type="inbound_message",
                direction=EventDirection.inbound,
                payload=msg,
            )
        for status in normalized.get("statuses", []):
            number = status.get("recipient_id")
            if not number:
                continue
            conversation = conversations.get_or_create(number)
            conversations.add_event(
                conversation.id,
                event_type=f"status_{status.get('status', 'unknown')}",
                direction=EventDirection.system,
                payload=status,
            )


def _normalize(payload: dict) -> dict:
    """Flatten the nested Meta webhook envelope into messages + statuses."""
    messages: list[dict] = []
    statuses: list[dict] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages.extend(value.get("messages", []))
            statuses.extend(value.get("statuses", []))
    return {"messages": messages, "statuses": statuses}
