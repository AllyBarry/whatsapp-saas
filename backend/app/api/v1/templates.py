"""Template endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession, require_admin
from app.models.user import TenantUser
from app.schemas.common import ok
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("")
def list_templates(
    user: CurrentUser,
    db: DbSession,
    status: Annotated[str | None, Query(description="Filter by Meta status")] = None,
):
    return ok(TemplateService(db, user.tenant_id).list(status=status))


@router.post("/sync")
async def sync_templates(
    db: DbSession,
    user: Annotated[TenantUser, Depends(require_admin)],
):
    """Pull templates from Meta into local storage."""
    return ok(await TemplateService(db, user.tenant_id).sync())
