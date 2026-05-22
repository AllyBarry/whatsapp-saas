"""WhatsApp credential management endpoints. Secrets are never returned."""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession, require_admin
from app.models.user import TenantUser
from app.schemas.common import ok
from app.schemas.credential import CredentialInput
from app.services.credential_service import CredentialService

router = APIRouter(prefix="/credentials", tags=["credentials"])


@router.get("")
def get_credentials(user: CurrentUser, db: DbSession):
    """Return the tenant's credential metadata (no secret values)."""
    return ok(CredentialService(db, user.tenant_id).get())


@router.put("")
def upsert_credentials(
    payload: CredentialInput,
    db: DbSession,
    user: Annotated[TenantUser, Depends(require_admin)],
):
    """Create or replace WhatsApp credentials. Owner/admin only."""
    return ok(CredentialService(db, user.tenant_id).upsert(payload))
