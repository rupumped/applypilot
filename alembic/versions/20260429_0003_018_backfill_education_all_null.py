"""Backfill education for any profile still NULL after 017.

Revision ID: 20260429_018
Revises: 20260429_017
Create Date: 2026-04-29

017 only updated rows where users.profile_completed was TRUE. Legacy accounts
that already used the app but never had that flag set (or data drift) still
had education IS NULL, so computed completion_status kept education=false.

Setting education to [] for every remaining NULL matches the work_experience
pattern: non-NULL [] means the step is satisfied (including no entries).
New signups after this migration still insert NULL until they save step 3;
this one-time UPDATE does not affect future rows.
"""

from alembic import op

revision = "20260429_018"
down_revision = "20260429_017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE user_profiles
        SET education = '[]'::jsonb
        WHERE education IS NULL
        """
    )


def downgrade() -> None:
    pass
