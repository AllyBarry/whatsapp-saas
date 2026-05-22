"""User repository — unscoped lookups needed for login live here."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import TenantUser


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> TenantUser | None:
        """Look up a user by email across tenants (login entrypoint only)."""
        stmt = select(TenantUser).where(TenantUser.email == email.lower())
        return self.db.scalars(stmt).first()

    def add(self, user: TenantUser) -> TenantUser:
        self.db.add(user)
        self.db.flush()
        return user
