"""WhatsApp phone number schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NumberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone_number_id: str
    display_phone_number: str | None
    verified_name: str | None
    quality_rating: str | None
    status: str | None
    messaging_limit: str | None
    created_at: datetime
