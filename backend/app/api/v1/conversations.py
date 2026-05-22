"""Conversation + dashboard endpoints."""
import uuid

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ok
from app.services.conversation_service import ConversationService, DashboardService

router = APIRouter(tags=["conversations"])


@router.get("/conversations")
def list_conversations(user: CurrentUser, db: DbSession):
    return ok(ConversationService(db, user.tenant_id).list())


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: uuid.UUID, user: CurrentUser, db: DbSession):
    return ok(ConversationService(db, user.tenant_id).get(conversation_id))


@router.get("/dashboard")
def dashboard(user: CurrentUser, db: DbSession):
    """Aggregate counts and recent activity for the dashboard home."""
    return ok(DashboardService(db, user.tenant_id).stats())
