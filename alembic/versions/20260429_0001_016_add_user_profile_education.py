"""Add education JSONB to user_profiles.

Revision ID: 20260429_016
Revises: 20260327_015
Create Date: 2026-04-29
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260429_016"
down_revision = "20260327_015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("education", JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "education")
