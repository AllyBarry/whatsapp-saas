"""WhatsApp credential schemas. Secrets are write-only — never serialized back."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CredentialInput(BaseModel):
    access_token: str = Field(min_length=1)
    app_secret: str = Field(min_length=1)
    verify_token: str = Field(min_length=1)
    waba_id: str = Field(min_length=1)
    phone_number_id: str = Field(min_length=1)


class CredentialOut(BaseModel):
    """Safe representation — secrets reduced to a boolean presence flag."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    waba_id: str
    phone_number_id: str
    verify_token: str
    has_access_token: bool
    has_app_secret: bool
    created_at: datetime
