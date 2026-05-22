"""Tenant + subscription read service (mock plans, no billing)."""
import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.tenant import PLAN_LIMITS
from app.repositories.number import NumberRepository
from app.repositories.template import TemplateRepository
from app.repositories.tenant import TenantRepository
from app.schemas.tenant import PlanLimits, SubscriptionOut, TenantOut


class TenantService:
    def __init__(self, db: Session, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = TenantRepository(db)

    def _tenant(self):
        tenant = self.repo.get(self.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        return tenant

    def get(self) -> TenantOut:
        return TenantOut.model_validate(self._tenant())

    def subscription(self) -> SubscriptionOut:
        """Current mock plan with limits and usage — limits are not enforced."""
        tenant = self._tenant()
        limits = PLAN_LIMITS[tenant.subscription_plan]
        return SubscriptionOut(
            plan=tenant.subscription_plan,
            limits=PlanLimits(**limits),
            numbers_used=NumberRepository(self.db, self.tenant_id).count(),
            templates_used=TemplateRepository(self.db, self.tenant_id).count(),
        )
