"""FastAPI application entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.webhooks import router as webhooks_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger("app.main")

app = FastAPI(
    title="WhatsApp SaaS Core",
    description="Multi-tenant WhatsApp management platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router)
app.include_router(webhooks_router)


@app.get("/health", tags=["meta"])
def health():
    return {"success": True, "data": {"status": "ok", "environment": settings.environment}}


@app.on_event("startup")
def _startup():
    logger.info("WhatsApp SaaS Core started (env=%s)", settings.environment)
