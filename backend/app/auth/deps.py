"""FastAPI auth dependencies — resolve and authorize the current user."""
import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.core.errors import AuthError, PermissionError_
from app.db.session import get_db
from app.models.user import TenantUser, UserRole

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> TenantUser:
    """Resolve the authenticated TenantUser from the Bearer token."""
    if credentials is None:
        raise AuthError("Missing authentication credentials")

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthError("Malformed token")

    user = db.get(TenantUser, uuid.UUID(user_id))
    if user is None:
        raise AuthError("User no longer exists")
    return user


CurrentUser = Annotated[TenantUser, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    """Dependency factory that enforces the user holds one of the given roles."""

    def _checker(user: CurrentUser) -> TenantUser:
        if user.role not in roles:
            raise PermissionError_(
                f"Requires one of: {', '.join(r.value for r in roles)}"
            )
        return user

    return _checker


# Convenience: write access requires owner or admin.
require_admin = require_roles(UserRole.owner, UserRole.admin)
