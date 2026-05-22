"""Tenant / company model."""
import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class TenantStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    cancelled = "cancelled"


class SubscriptionPlan(str, enum.Enum):
    free = "free"
    starter = "starter"
    business = "business"
    enterprise = "enterprise"


# Mock plan limits — surfaced in the UI, not enforced yet.
PLAN_LIMITS: dict[SubscriptionPlan, dict[str, int]] = {
    SubscriptionPlan.free: {"numbers": 1, "templates": 5},
    SubscriptionPlan.starter: {"numbers": 3, "templates": 25},
    SubscriptionPlan.business: {"numbers": 10, "templates": 100},
    SubscriptionPlan.enterprise: {"numbers": 100, "templates": 1000},
}


class Tenant(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus, name="tenant_status"), default=TenantStatus.active, nullable=False
    )
    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan, name="subscription_plan"),
        default=SubscriptionPlan.free,
        nullable=False,
    )

    users: Mapped[list["TenantUser"]] = relationship(back_populates="tenant")  # noqa: F821
