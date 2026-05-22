"""Outbound message endpoints."""
from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ok
from app.schemas.message import SendTemplateRequest
from app.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/send-template")
async def send_template(payload: SendTemplateRequest, user: CurrentUser, db: DbSession):
    """Send a WhatsApp template message and log it to the conversation."""
    return ok(await MessageService(db, user.tenant_id).send_template(payload))
