"""Meta WhatsApp Cloud API integration.

ALL Meta-specific HTTP and payload logic lives in this package. Controllers
and other services must depend only on `WhatsAppService` and `verify_signature`
— never on httpx or Graph API URLs directly. This keeps Meta swappable and
the rest of the app testable.
"""
from app.services.integrations.meta.signature import verify_signature
from app.services.integrations.meta.whatsapp import WhatsAppService

__all__ = ["WhatsAppService", "verify_signature"]
