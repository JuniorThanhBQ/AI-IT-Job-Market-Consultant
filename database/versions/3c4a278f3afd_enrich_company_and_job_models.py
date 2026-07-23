"""enrich_company_and_job_models

Revision ID: 3c4a278f3afd
Revises: 50780b5d4025
Create Date: 2026-07-21 09:49:08.906744

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

revision: str = "3c4a278f3afd"
down_revision: Union[str, Sequence[str], None] = "50780b5d4025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "companies",
        sa.Column("slogan", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column("companies", sa.Column("rating", sa.Float(), nullable=True))
    op.add_column(
        "companies",
        sa.Column("company_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("country", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("addresses", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("working_days", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("overtime_policy", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("vision", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("mission", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.create_index(
        op.f("ix_companies_company_type"), "companies", ["company_type"], unique=False
    )
    op.create_index(
        op.f("ix_companies_country"), "companies", ["country"], unique=False
    )
    op.add_column(
        "jobs",
        sa.Column("reference_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column(
        "jobs", sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=True)
    )
    op.add_column("jobs", sa.Column("applicants_count", sa.Integer(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column(
            "experience_required", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column(
        "jobs",
        sa.Column("content_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "responsibilities", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "required_qualifications",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "preferred_qualifications",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "nice_to_have", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "top_reasons", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )
    op.add_column(
        "jobs",
        sa.Column("domains", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("culture", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_index(op.f("ix_jobs_content_hash"), "jobs", ["content_hash"], unique=True)
    op.create_index(
        op.f("ix_jobs_reference_id"), "jobs", ["reference_id"], unique=False
    )
    op.create_index(op.f("ix_jobs_status"), "jobs", ["status"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_jobs_status"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_reference_id"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_content_hash"), table_name="jobs")
    op.drop_column("jobs", "culture")
    op.drop_column("jobs", "domains")
    op.drop_column("jobs", "top_reasons")
    op.drop_column("jobs", "nice_to_have")
    op.drop_column("jobs", "preferred_qualifications")
    op.drop_column("jobs", "required_qualifications")
    op.drop_column("jobs", "responsibilities")
    op.drop_column("jobs", "content_hash")
    op.drop_column("jobs", "experience_required")
    op.drop_column("jobs", "applicants_count")
    op.drop_column("jobs", "status")
    op.drop_column("jobs", "reference_id")
    op.drop_index(op.f("ix_companies_country"), table_name="companies")
    op.drop_index(op.f("ix_companies_company_type"), table_name="companies")
    op.drop_column("companies", "mission")
    op.drop_column("companies", "vision")
    op.drop_column("companies", "overtime_policy")
    op.drop_column("companies", "working_days")
    op.drop_column("companies", "addresses")
    op.drop_column("companies", "country")
    op.drop_column("companies", "company_type")
    op.drop_column("companies", "slogan")
