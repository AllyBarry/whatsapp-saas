"""Template sync service."""
from __future__ import annotations  # method `list` would otherwise shadow builtin

import uuid

from sqlalchemy.orm import Session

from app.core.logging import get_logger, log_event
from app.models.template import Template
from app.repositories.template import TemplateRepository
from app.schemas.template import SyncResult, TemplateOut
from app.services.credential_service import CredentialService

logger = get_logger("app.templates")


class TemplateService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = TemplateRepository(db, tenant_id)
        self.credentials = CredentialService(db, tenant_id)

    def list(self, status: str | None = None) -> list[TemplateOut]:
        templates = self.repo.list()
        if status:
            templates = [t for t in templates if (t.status or "").upper() == status.upper()]
        return [TemplateOut.model_validate(t) for t in templates]

    async def sync(self) -> SyncResult:
        """Pull templates from Meta and upsert them locally."""
        wa = self.credentials.whatsapp_service()
        remote = await wa.get_templates()

        created = updated = 0
        for item in remote:
            meta_id = item.get("id")
            if not meta_id:
                continue
            template = self.repo.get_by_meta_id(meta_id)
            if template is None:
                template = Template(tenant_id=self.tenant_id, meta_template_id=meta_id)
                self.db.add(template)
                created += 1
            else:
                updated += 1
            template.name = item.get("name", template.name or "unnamed")
            template.language = item.get("language", template.language or "en")
            template.category = item.get("category")
            template.status = item.get("status")
            template.template_json = item

        self.db.flush()
        log_event(
            logger, "info", "Templates synced",
            tenant_id=str(self.tenant_id), created=created, updated=updated,
        )
        return SyncResult(synced=len(remote), created=created, updated=updated)
