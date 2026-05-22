"""Tenant-scoped repository base.

Every query goes through `_scoped()` which pins `tenant_id`, so callers
cannot accidentally read across tenants. See MULTI-TENANCY in README.
"""
import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class TenantScopedRepository(Generic[ModelT]):
    """Base repository that enforces tenant isolation on every read."""

    model: type[ModelT]

    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id

    def _scoped(self):
        """Base SELECT statement already filtered to the current tenant."""
        return select(self.model).where(self.model.tenant_id == self.tenant_id)

    def list(self) -> list[ModelT]:
        return list(self.db.scalars(self._scoped()).all())

    def get(self, entity_id: uuid.UUID) -> ModelT | None:
        stmt = self._scoped().where(self.model.id == entity_id)
        return self.db.scalars(stmt).first()

    def add(self, entity: ModelT) -> ModelT:
        # Defensive: never persist an entity for a different tenant.
        if getattr(entity, "tenant_id", self.tenant_id) != self.tenant_id:
            raise ValueError("Entity tenant_id does not match repository scope")
        entity.tenant_id = self.tenant_id
        self.db.add(entity)
        self.db.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        self.db.delete(entity)
        self.db.flush()

    def count(self) -> int:
        return len(self.list())
