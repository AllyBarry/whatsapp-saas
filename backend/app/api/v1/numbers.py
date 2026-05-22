"""WhatsApp number endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession, require_admin
from app.models.user import TenantUser
from app.schemas.common import ok
from app.services.number_service import NumberService

router = APIRouter(prefix="/numbers", tags=["numbers"])


@router.get("")
def list_numbers(user: CurrentUser, db: DbSession):
    return ok(NumberService(db, user.tenant_id).list())


@router.post("/sync")
async def sync_numbers(
    db: DbSession,
    user: Annotated[TenantUser, Depends(require_admin)],
):
    """Pull the latest phone numbers and statuses from Meta."""
    return ok(await NumberService(db, user.tenant_id).sync())
