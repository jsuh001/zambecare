"""Add Phase 2 identity, session, and audit structures.

Revision ID: 20260902_01
Revises: None
Create Date: 2026-09-02
"""

from alembic import op
import sqlalchemy as sa

revision = "20260902_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS security")
    op.execute("CREATE SCHEMA IF NOT EXISTS clinical")

    op.create_table(
        "user_account",
        sa.Column("user_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(500), nullable=False),
        sa.Column("account_status", sa.String(20), nullable=False, server_default="ACTIVE"),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_user_account_email"),
        schema="security",
    )
    op.create_index("ix_user_account_email", "user_account", ["email"], unique=True, schema="security")

    op.create_table(
        "role",
        sa.Column("role_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_name", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255)),
        sa.UniqueConstraint("role_name", name="uq_role_name"),
        schema="security",
    )
    op.create_table(
        "user_role",
        sa.Column("user_role_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("security.user_account.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            sa.Integer(),
            sa.ForeignKey("security.role.role_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        schema="security",
    )
    op.create_table(
        "refresh_session",
        sa.Column("refresh_session_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("security.user_account.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="security",
    )
    op.create_index(
        "ix_refresh_session_user_id", "refresh_session", ["user_id"], schema="security"
    )
    op.create_table(
        "audit_event",
        sa.Column("audit_event_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor_id", sa.String(100), nullable=False),
        sa.Column("actor_role", sa.String(50), nullable=False),
        sa.Column("action_name", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=False),
        sa.Column("outcome", sa.String(20), nullable=False),
        sa.Column("request_id", sa.String(36), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="security",
    )
    op.create_index("ix_audit_event_request_id", "audit_event", ["request_id"], schema="security")

    op.add_column("patient", sa.Column("user_id", sa.Integer(), nullable=True), schema="clinical")
    op.add_column(
        "patient",
        sa.Column("preferred_language", sa.String(30), nullable=False, server_default="English"),
        schema="clinical",
    )
    op.create_unique_constraint("uq_patient_user_id", "patient", ["user_id"], schema="clinical")
    op.create_foreign_key(
        "fk_patient_user_account",
        "patient",
        "user_account",
        ["user_id"],
        ["user_id"],
        source_schema="clinical",
        referent_schema="security",
    )

    role_table = sa.table(
        "role",
        sa.column("role_name", sa.String),
        sa.column("description", sa.String),
        schema="security",
    )
    op.bulk_insert(
        role_table,
        [
            {"role_name": "PATIENT", "description": "Patient portal user"},
            {"role_name": "DOCTOR", "description": "Authorized physician"},
            {"role_name": "NURSE", "description": "Authorized nursing professional"},
            {"role_name": "FACILITY_ADMIN", "description": "Facility directory administrator"},
            {"role_name": "SYSTEM_ADMIN", "description": "System administrator"},
            {"role_name": "SECURITY_AUDITOR", "description": "Read-only security auditor"},
        ],
    )


def downgrade() -> None:
    op.drop_constraint("fk_patient_user_account", "patient", schema="clinical", type_="foreignkey")
    op.drop_constraint("uq_patient_user_id", "patient", schema="clinical", type_="unique")
    op.drop_column("patient", "preferred_language", schema="clinical")
    op.drop_column("patient", "user_id", schema="clinical")
    op.drop_table("audit_event", schema="security")
    op.drop_table("refresh_session", schema="security")
    op.drop_table("user_role", schema="security")
    op.drop_table("role", schema="security")
    op.drop_table("user_account", schema="security")
