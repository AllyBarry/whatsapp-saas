"""Outbound message schemas."""
from pydantic import BaseModel, Field


class SendTemplateRequest(BaseModel):
    template_name: str = Field(min_length=1)
    language: str = Field(default="en", min_length=2)
    recipient: str = Field(min_length=5, description="E.164 phone number, e.g. +27821234567")
    variables: dict[str, str] = Field(default_factory=dict)


class SendTemplateResult(BaseModel):
    message_id: str | None
    recipient: str
    conversation_id: str
    status: str
