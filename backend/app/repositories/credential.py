"""WhatsApp credential repository."""
from app.models.whatsapp import WhatsAppCredential
from app.repositories.base import TenantScopedRepository


class CredentialRepository(TenantScopedRepository[WhatsAppCredential]):
    model = WhatsAppCredential

    def get_current(self) -> WhatsAppCredential | None:
        """A tenant has at most one credential set."""
        return self.db.scalars(self._scoped()).first()
