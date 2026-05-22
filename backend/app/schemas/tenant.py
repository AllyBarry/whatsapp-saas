"""Tenant schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.tenant import SubscriptionPlan, TenantStatus


class TenantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    status: TenantStatus
    subscription_plan: SubscriptionPlan
    created_at: datetime


class PlanLimits(BaseModel):
    numbers: int
    templates: int


class SubscriptionOut(BaseModel):
    plan: SubscriptionPlan
    limits: PlanLimits
    numbers_used: int
    templates_used: int


class PlanInfo(BaseModel):
    plan: SubscriptionPlan
    limits: PlanLimits
