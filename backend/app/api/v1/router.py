"""Aggregate /api/v1 router."""
from fastapi import APIRouter

from app.api.v1 import auth, conversations, credentials, messages, numbers, templates, tenants

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(tenants.router)
api_router.include_router(credentials.router)
api_router.include_router(numbers.router)
api_router.include_router(templates.router)
api_router.include_router(messages.router)
api_router.include_router(conversations.router)
