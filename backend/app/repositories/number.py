"""WhatsApp number repository."""
from app.models.whatsapp import WhatsAppNumber
from app.repositories.base import TenantScopedRepository


class NumberRepository(TenantScopedRepository[WhatsAppNumber]):
    model = WhatsAppNumber

    def get_by_phone_number_id(self, phone_number_id: str) -> WhatsAppNumber | None:
        stmt = self._scoped().where(WhatsAppNumber.phone_number_id == phone_number_id)
        return self.db.scalars(stmt).first()
