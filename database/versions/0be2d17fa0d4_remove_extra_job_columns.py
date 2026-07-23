"""
remove_extra_job_columns

Revision ID: 0be2d17fa0d4
Revises: 3c4a278f3afd
Create Date: 2026-07-21 12:27:05.095356
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0be2d17fa0d4"
down_revision: Union[str, Sequence[str], None] = "3c4a278f3afd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f("ix_jobs_reference_id"), table_name="jobs")
    op.drop_column("jobs", "reference_id")
    op.drop_column("jobs", "experience_required")
    op.drop_column("jobs", "applicants_count")
    op.drop_column("jobs", "preferred_qualifications")
    op.drop_column("jobs", "culture")
    op.drop_column("jobs", "language_level")
    op.drop_column("jobs", "top_reasons")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "jobs",
        sa.Column(
            "top_reasons",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "jobs",
        sa.Column("language_level", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "culture",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "preferred_qualifications",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "jobs",
        sa.Column("applicants_count", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "experience_required", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "jobs",
        sa.Column("reference_id", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.create_index(
        op.f("ix_jobs_reference_id"), "jobs", ["reference_id"], unique=False
    )
