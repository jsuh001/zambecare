"""Add patient location fields for care-directory proximity search.

Revision ID: 20260902_02
Revises: 20260902_01
Create Date: 2026-09-02
"""

from alembic import op
import sqlalchemy as sa

revision = "20260902_02"
down_revision = "20260902_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "patient",
        sa.Column(
            "country",
            sa.String(56),
            nullable=False,
            server_default="United States",
        ),
        schema="clinical",
    )
    op.add_column("patient", sa.Column("state", sa.String(50), nullable=True), schema="clinical")
    op.add_column("patient", sa.Column("city", sa.String(100), nullable=True), schema="clinical")
    op.add_column(
        "patient", sa.Column("postal_code", sa.String(20), nullable=True), schema="clinical"
    )
    op.create_index(
        "ix_patient_city_state", "patient", ["city", "state"], schema="clinical"
    )

    # facility_name uniqueness (needed for the idempotent directory seed) is defined
    # in db/postgres/init/001_oltp_schema.sql; add it here only where it is missing
    # so databases created before that change are brought in line.
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'uq_facility_name'
            ) THEN
                ALTER TABLE clinical.facility
                    ADD CONSTRAINT uq_facility_name UNIQUE (facility_name);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE clinical.facility DROP CONSTRAINT IF EXISTS uq_facility_name")
    op.drop_index("ix_patient_city_state", table_name="patient", schema="clinical")
    op.drop_column("patient", "postal_code", schema="clinical")
    op.drop_column("patient", "city", schema="clinical")
    op.drop_column("patient", "state", schema="clinical")
    op.drop_column("patient", "country", schema="clinical")
