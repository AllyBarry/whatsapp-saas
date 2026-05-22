"""Conversation read service + dashboard aggregation."""
from __future__ import annotations  # method `list` would otherwise shadow builtin

import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.conversation import EventDirection
from app.repositories.conversation import ConversationRepository
from app.repositories.number import NumberRepository
from app.repositories.template import TemplateRepository
from app.repositories.webhook import WebhookRepository
from app.schemas.conversation import (
    ConversationDetail,
    ConversationEventOut,
    ConversationOut,
    DashboardStats,
)


class ConversationService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = ConversationRepository(db, tenant_id)

    def list(self) -> list[ConversationOut]:
        return [ConversationOut.model_validate(c) for c in self.repo.list()]

    def get(self, conversation_id: uuid.UUID) -> ConversationDetail:
        conversation = self.repo.get(conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return ConversationDetail.model_validate(conversation)


class DashboardService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def stats(self) -> DashboardStats:
        conversations = ConversationRepository(self.db, self.tenant_id)
        numbers = NumberRepository(self.db, self.tenant_id)
        templates = TemplateRepository(self.db, self.tenant_id)
        webhooks = WebhookRepository(self.db)

        recent_sends = conversations.recent_events(limit=10, direction=EventDirection.outbound)
        recent_webhooks = webhooks.recent_for_tenant(self.tenant_id, limit=10)

        return DashboardStats(
            numbers_count=numbers.count(),
            templates_count=templates.count(),
            conversations_count=conversations.count(),
            recent_sends=[ConversationEventOut.model_validate(e) for e in recent_sends],
            recent_webhooks=[
                {
                    "id": str(w.id),
                    "object_type": w.object_type,
                    "signature_valid": w.signature_valid,
                    "created_at": w.created_at.isoformat(),
                }
                for w in recent_webhooks
            ],
        )
