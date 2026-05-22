"""Import all models so Alembic autogenerate and metadata see them."""
from app.models.conversation import Conversation, ConversationEvent
from app.models.template import Template
from app.models.tenant import Tenant
from app.models.user import TenantUser
from app.models.webhook import WebhookEvent
from app.models.whatsapp import WhatsAppCredential, WhatsAppNumber

__all__ = [
    "Tenant",
    "TenantUser",
    "WhatsAppCredential",
    "WhatsAppNumber",
    "Template",
    "Conversation",
    "ConversationEvent",
    "WebhookEvent",
]
