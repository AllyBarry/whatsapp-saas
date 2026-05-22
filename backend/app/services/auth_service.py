"""Authentication + registration service."""
import re

from sqlalchemy.orm import Session

from app.auth.security import create_access_token, hash_password, verify_password
from app.core.errors import AuthError, ConflictError
from app.core.logging import get_logger, log_event
from app.models.tenant import Tenant
from app.models.user import TenantUser, UserRole
from app.repositories.tenant import TenantRepository
from app.repositories.user import UserRepository
from app.schemas.auth import AuthResult, LoginRequest, RegisterRequest, TokenResponse, UserOut

logger = get_logger("app.auth")


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return base or "tenant"


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.tenants = TenantRepository(db)

    def register(self, data: RegisterRequest) -> AuthResult:
        """Create a tenant and its first owner user."""
        if self.users.get_by_email(data.email.lower()):
            raise ConflictError("An account with this email already exists", code="EMAIL_TAKEN")

        slug = self._unique_slug(_slugify(data.company_name))
        tenant = self.tenants.add(Tenant(name=data.company_name, slug=slug))

        user = self.users.add(
            TenantUser(
                tenant_id=tenant.id,
                email=data.email.lower(),
                password_hash=hash_password(data.password),
                role=UserRole.owner,
            )
        )
        log_event(logger, "info", "Tenant registered", tenant_id=str(tenant.id), slug=slug)
        return self._issue(user)

    def login(self, data: LoginRequest) -> AuthResult:
        user = self.users.get_by_email(data.email.lower())
        if user is None or not verify_password(data.password, user.password_hash):
            log_event(logger, "warning", "Failed login attempt", email=data.email.lower())
            raise AuthError("Invalid email or password")
        return self._issue(user)

    def _issue(self, user: TenantUser) -> AuthResult:
        token, expires_in = create_access_token(
            user_id=user.id, tenant_id=user.tenant_id, role=user.role.value
        )
        return AuthResult(
            token=TokenResponse(access_token=token, expires_in=expires_in),
            user=UserOut.model_validate(user),
        )

    def _unique_slug(self, base: str) -> str:
        slug, suffix = base, 1
        while self.tenants.get_by_slug(slug) is not None:
            suffix += 1
            slug = f"{base}-{suffix}"
        return slug
