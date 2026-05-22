"""WhatsApp number sync service."""
from __future__ import annotations  # method `list` would otherwise shadow builtin

import uuid

from sqlalchemy.orm import Session

from app.core.logging import get_logger, log_event
from app.models.whatsapp import WhatsAppNumber
from app.repositories.number import NumberRepository
from app.schemas.number import NumberOut
from app.services.credential_service import CredentialService

logger = get_logger("app.numbers")


class NumberService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = NumberRepository(db, tenant_id)
        self.credentials = CredentialService(db, tenant_id)

    def list(self) -> list[NumberOut]:
        return [NumberOut.model_validate(n) for n in self.repo.list()]

    async def sync(self) -> list[NumberOut]:
        """Pull phone numbers from Meta and upsert them locally."""
        wa = self.credentials.whatsapp_service()
        remote = await wa.get_phone_numbers()

        for item in remote:
            pnid = item.get("id")
            if not pnid:
                continue
            number = self.repo.get_by_phone_number_id(pnid)
            if number is None:
                number = WhatsAppNumber(tenant_id=self.tenant_id, phone_number_id=pnid)
                self.db.add(number)
            number.display_phone_number = item.get("display_phone_number")
            number.verified_name = item.get("verified_name")
            number.quality_rating = item.get("quality_rating")
            number.status = item.get("status")
            number.messaging_limit = item.get("messaging_limit_tier")

        self.db.flush()
        log_event(
            logger, "info", "Numbers synced",
            tenant_id=str(self.tenant_id), count=len(remote),
        )
        return self.list()
