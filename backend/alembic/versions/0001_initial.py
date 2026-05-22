"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "suspended", "cancelled", name="tenant_status"),
            nullable=False,
        ),
        sa.Column(
            "subscription_plan",
            sa.Enum("free", "starter", "business", "enterprise", name="subscription_plan"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)

    op.create_table(
        "tenant_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("owner", "admin", "viewer", name="user_role"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "email", name="uq_tenant_user_email"),
    )
    op.create_index("ix_tenant_users_tenant_id", "tenant_users", ["tenant_id"])
    op.create_index("ix_tenant_users_email", "tenant_users", ["email"])

    op.create_table(
        "whatsapp_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("access_token_encrypted", sa.String(), nullable=False),
        sa.Column("app_secret_encrypted", sa.String(), nullable=False),
        sa.Column("verify_token", sa.String(255), nullable=False),
        sa.Column("waba_id", sa.String(64), nullable=False),
        sa.Column("phone_number_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", name="uq_credential_tenant"),
    )
    op.create_index("ix_whatsapp_credentials_tenant_id", "whatsapp_credentials", ["tenant_id"])

    op.create_table(
        "whatsapp_numbers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phone_number_id", sa.String(64), nullable=False),
        sa.Column("display_phone_number", sa.String(32)),
        sa.Column("verified_name", sa.String(255)),
        sa.Column("quality_rating", sa.String(32)),
        sa.Column("status", sa.String(64)),
        sa.Column("messaging_limit", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "phone_number_id", name="uq_number_tenant_pnid"),
    )
    op.create_index("ix_whatsapp_numbers_tenant_id", "whatsapp_numbers", ["tenant_id"])

    op.create_table(
        "templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("meta_template_id", sa.String(64)),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("language", sa.String(16), nullable=False),
        sa.Column("category", sa.String(64)),
        sa.Column("status", sa.String(64)),
        sa.Column("template_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("tenant_id", "meta_template_id", name="uq_template_tenant_meta"),
    )
    op.create_index("ix_templates_tenant_id", "templates", ["tenant_id"])

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_number", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_message_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", sa.Enum("open", "closed", name="conversation_status"), nullable=False),
    )
    op.create_index("ix_conversations_tenant_id", "conversations", ["tenant_id"])
    op.create_index("ix_conversations_customer_number", "conversations", ["customer_number"])

    op.create_table(
        "conversation_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("direction", sa.Enum("inbound", "outbound", "system", name="event_direction"), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_conversation_events_conversation_id", "conversation_events", ["conversation_id"])

    op.create_table(
        "webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="SET NULL")),
        sa.Column("signature_valid", sa.Boolean(), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=False),
        sa.Column("normalized", postgresql.JSONB(), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False),
        sa.Column("object_type", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_webhook_events_tenant_id", "webhook_events", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("webhook_events")
    op.drop_table("conversation_events")
    op.drop_table("conversations")
    op.drop_table("templates")
    op.drop_table("whatsapp_numbers")
    op.drop_table("whatsapp_credentials")
    op.drop_table("tenant_users")
    op.drop_table("tenants")
    for enum_name in (
        "tenant_status", "subscription_plan", "user_role",
        "conversation_status", "event_direction",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
