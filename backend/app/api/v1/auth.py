"""Authentication endpoints."""
from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import AuthResult, LoginRequest, RegisterRequest, UserOut
from app.schemas.common import ok
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: DbSession):
    """Create a new tenant and its first owner user."""
    result: AuthResult = AuthService(db).register(payload)
    return ok(result)


@router.post("/login")
def login(payload: LoginRequest, db: DbSession):
    result: AuthResult = AuthService(db).login(payload)
    return ok(result)


@router.get("/me")
def me(user: CurrentUser):
    """Return the currently authenticated user."""
    return ok(UserOut.model_validate(user))
