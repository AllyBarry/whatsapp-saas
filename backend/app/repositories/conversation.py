"""Conversation + event repository."""
import uuid

from sqlalchemy import desc, select

from app.models.conversation import Conversation, ConversationEvent, EventDirection
from app.repositories.base import TenantScopedRepository


class ConversationRepository(TenantScopedRepository[Conversation]):
    model = Conversation

    def get_or_create(self, customer_number: str) -> Conversation:
        stmt = self._scoped().where(Conversation.customer_number == customer_number)
        conversation = self.db.scalars(stmt).first()
        if conversation is None:
            conversation = Conversation(
                tenant_id=self.tenant_id, customer_number=customer_number
            )
            self.db.add(conversation)
            self.db.flush()
        return conversation

    def add_event(
        self,
        conversation_id: uuid.UUID,
        event_type: str,
        direction: EventDirection,
        payload: dict,
    ) -> ConversationEvent:
        event = ConversationEvent(
            conversation_id=conversation_id,
            event_type=event_type,
            direction=direction,
            payload=payload,
        )
        self.db.add(event)
        self.db.flush()
        return event

    def recent_events(self, limit: int = 10, direction: EventDirection | None = None):
        """Recent events across the tenant's conversations."""
        stmt = (
            select(ConversationEvent)
            .join(Conversation, ConversationEvent.conversation_id == Conversation.id)
            .where(Conversation.tenant_id == self.tenant_id)
            .order_by(desc(ConversationEvent.created_at))
            .limit(limit)
        )
        if direction is not None:
            stmt = stmt.where(ConversationEvent.direction == direction)
        return list(self.db.scalars(stmt).all())
