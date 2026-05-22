"""Conversation schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.conversation import ConversationStatus, EventDirection


class ConversationEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    direction: EventDirection
    payload: dict
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_number: str
    started_at: datetime
    last_message_at: datetime
    status: ConversationStatus


class ConversationDetail(ConversationOut):
    events: list[ConversationEventOut] = []


class DashboardStats(BaseModel):
    numbers_count: int
    templates_count: int
    conversations_count: int
    recent_sends: list[ConversationEventOut]
    recent_webhooks: list[dict]
