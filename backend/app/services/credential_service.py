"""WhatsApp credential management — encrypts secrets at rest."""
import uuid

from sqlalchemy.orm import Session

from app.core.encryption import decrypt, encrypt
from app.core.errors import NotFoundError
from app.core.logging import get_logger, log_event
from app.models.whatsapp import WhatsAppCredential
from app.repositories.credential import CredentialRepository
from app.schemas.credential import CredentialInput, CredentialOut
from app.services.integrations.meta import WhatsAppService

logger = get_logger("app.credentials")


class CredentialService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = CredentialRepository(db, tenant_id)

    def get(self) -> CredentialOut | None:
        cred = self.repo.get_current()
        return _to_out(cred) if cred else None

    def upsert(self, data: CredentialInput) -> CredentialOut:
        """Create or replace the tenant's credential set."""
        cred = self.repo.get_current()
        if cred is None:
            cred = WhatsAppCredential(tenant_id=self.tenant_id)
            self.db.add(cred)

        cred.access_token_encrypted = encrypt(data.access_token)
        cred.app_secret_encrypted = encrypt(data.app_secret)
        cred.verify_token = data.verify_token
        cred.waba_id = data.waba_id
        cred.phone_number_id = data.phone_number_id
        self.db.flush()

        log_event(logger, "info", "Credentials updated", tenant_id=str(self.tenant_id))
        return _to_out(cred)

    def get_decrypted(self) -> WhatsAppCredential:
        """Raw credential record — for internal service use only."""
        cred = self.repo.get_current()
        if cred is None:
            raise NotFoundError(
                "No WhatsApp credentials configured for this tenant",
                code="NO_CREDENTIALS",
            )
        return cred

    def whatsapp_service(self) -> WhatsAppService:
        """Build a Meta-backed WhatsAppService from stored credentials."""
        cred = self.get_decrypted()
        return WhatsAppService(
            access_token=decrypt(cred.access_token_encrypted),
            waba_id=cred.waba_id,
            phone_number_id=cred.phone_number_id,
        )

    def app_secret(self) -> str:
        return decrypt(self.get_decrypted().app_secret_encrypted)


def _to_out(cred: WhatsAppCredential) -> CredentialOut:
    return CredentialOut(
        id=cred.id,
        tenant_id=cred.tenant_id,
        waba_id=cred.waba_id,
        phone_number_id=cred.phone_number_id,
        verify_token=cred.verify_token,
        has_access_token=bool(cred.access_token_encrypted),
        has_app_secret=bool(cred.app_secret_encrypted),
        created_at=cred.created_at,
    )
