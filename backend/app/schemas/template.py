"""Template schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meta_template_id: str | None
    name: str
    language: str
    category: str | None
    status: str | None
    template_json: dict
    created_at: datetime


class SyncResult(BaseModel):
    synced: int
    created: int
    updated: int
