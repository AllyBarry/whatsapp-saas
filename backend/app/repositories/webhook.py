"""Webhook event repository."""
import uuid

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.webhook import WebhookEvent


class WebhookRepository:
    """Not tenant-scoped on write — webhooks may arrive before tenant resolution."""

    def __init__(self, db: Session):
        self.db = db

    def add(self, event: WebhookEvent) -> WebhookEvent:
        self.db.add(event)
        self.db.flush()
        return event

    def recent_for_tenant(self, tenant_id: uuid.UUID, limit: int = 10) -> list[WebhookEvent]:
        stmt = (
            select(WebhookEvent)
            .where(WebhookEvent.tenant_id == tenant_id)
            .order_by(desc(WebhookEvent.created_at))
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
