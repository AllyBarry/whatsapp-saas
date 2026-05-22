"""Tenant + subscription endpoints (mock plans)."""
from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.models.tenant import PLAN_LIMITS
from app.schemas.common import ok
from app.schemas.tenant import PlanInfo, PlanLimits
from app.services.tenant_service import TenantService

router = APIRouter(tags=["tenant"])


@router.get("/tenant")
def get_tenant(user: CurrentUser, db: DbSession):
    return ok(TenantService(db, user.tenant_id).get())


@router.get("/subscription")
def get_subscription(user: CurrentUser, db: DbSession):
    """Current plan, mock limits and usage counters."""
    return ok(TenantService(db, user.tenant_id).subscription())


@router.get("/plans")
def list_plans():
    """Static catalogue of mock plans (no billing)."""
    return ok([
        PlanInfo(plan=plan, limits=PlanLimits(**limits))
        for plan, limits in PLAN_LIMITS.items()
    ])
