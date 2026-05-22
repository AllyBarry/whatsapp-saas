"""Conversation and conversation event models."""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class ConversationStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class EventDirection(str, enum.Enum):
    inbound = "inbound"
    outbound = "outbound"
    system = "system"


class Conversation(Base, UUIDMixin):
    __tablename__ = "conversations"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, name="conversation_status"),
        default=ConversationStatus.open,
        nullable=False,
    )

    events: Mapped[list["ConversationEvent"]] = relationship(
        back_populates="conversation", order_by="ConversationEvent.created_at"
    )


class ConversationEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversation_events"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    direction: Mapped[EventDirection] = mapped_column(
        Enum(EventDirection, name="event_direction"), nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    conversation: Mapped["Conversation"] = relationship(back_populates="events")
