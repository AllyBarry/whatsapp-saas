"""Shared API dependency aliases."""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.deps import CurrentUser, require_admin
from app.db.session import get_db

DbSession = Annotated[Session, Depends(get_db)]

__all__ = ["DbSession", "CurrentUser", "require_admin"]
