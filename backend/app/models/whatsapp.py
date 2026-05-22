"""WhatsApp credential and phone number models."""
import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class WhatsAppCredential(Base, UUIDMixin, TimestampMixin):
    """One Meta credential set per tenant. Secrets stored encrypted at rest."""

    __tablename__ = "whatsapp_credentials"
    __table_args__ = (UniqueConstraint("tenant_id", name="uq_credential_tenant"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    access_token_encrypted: Mapped[str] = mapped_column(String, nullable=False)
    app_secret_encrypted: Mapped[str] = mapped_column(String, nullable=False)
    verify_token: Mapped[str] = mapped_column(String(255), nullable=False)
    waba_id: Mapped[str] = mapped_column(String(64), nullable=False)
    phone_number_id: Mapped[str] = mapped_column(String(64), nullable=False)


class WhatsAppNumber(Base, UUIDMixin, TimestampMixin):
    """A phone number synced from the Meta WABA."""

    __tablename__ = "whatsapp_numbers"
    __table_args__ = (
        UniqueConstraint("tenant_id", "phone_number_id", name="uq_number_tenant_pnid"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    phone_number_id: Mapped[str] = mapped_column(String(64), nullable=False)
    display_phone_number: Mapped[str | None] = mapped_column(String(32))
    verified_name: Mapped[str | None] = mapped_column(String(255))
    quality_rating: Mapped[str | None] = mapped_column(String(32))
    status: Mapped[str | None] = mapped_column(String(64))
    messaging_limit: Mapped[str | None] = mapped_column(String(64))
