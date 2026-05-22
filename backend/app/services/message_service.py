"""Outbound template message service — sends via Meta and logs the conversation."""
import uuid

from sqlalchemy.orm import Session

from app.core.errors import MetaAPIError
from app.core.logging import get_logger, log_event
from app.models.conversation import EventDirection
from app.repositories.conversation import ConversationRepository
from app.schemas.message import SendTemplateRequest, SendTemplateResult
from app.services.credential_service import CredentialService

logger = get_logger("app.messages")


class MessageService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.credentials = CredentialService(db, tenant_id)
        self.conversations = ConversationRepository(db, tenant_id)

    async def send_template(self, data: SendTemplateRequest) -> SendTemplateResult:
        """Send a template message and persist it as an outbound event."""
        wa = self.credentials.whatsapp_service()
        conversation = self.conversations.get_or_create(data.recipient)

        try:
            result = await wa.send_template(
                recipient=data.recipient,
                template_name=data.template_name,
                language=data.language,
                variables=data.variables,
            )
        except MetaAPIError:
            # Record the failed attempt and commit it before re-raising, so the
            # failure survives the request-level rollback triggered by the error.
            self.conversations.add_event(
                conversation.id,
                event_type="template_send_failed",
                direction=EventDirection.outbound,
                payload={"template": data.template_name, "recipient": data.recipient},
            )
            self.db.commit()
            raise

        message_id = _extract_message_id(result)
        self.conversations.add_event(
            conversation.id,
            event_type="template_sent",
            direction=EventDirection.outbound,
            payload={
                "template": data.template_name,
                "language": data.language,
                "variables": data.variables,
                "message_id": message_id,
            },
        )
        log_event(
            logger, "info", "Outbound template logged",
            tenant_id=str(self.tenant_id), message_id=message_id,
        )
        return SendTemplateResult(
            message_id=message_id,
            recipient=data.recipient,
            conversation_id=str(conversation.id),
            status="sent",
        )


def _extract_message_id(result: dict) -> str | None:
    messages = result.get("messages")
    if isinstance(messages, list) and messages:
        return messages[0].get("id")
    return None
