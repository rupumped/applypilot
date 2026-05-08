"""Backfill education JSONB for users who already completed onboarding.

Revision ID: 20260429_017
Revises: 20260429_016
Create Date: 2026-04-29

Before the education step existed, completed profiles had no `education` column.
After 016, those rows are NULL; `_check_education_completion` treats NULL as
incomplete, so `profile_completed` becomes false and the dashboard redirects
to profile setup. Mirror the work_experience semantics: non-NULL `[]` means the
step was satisfied (including "no education entries yet").
"""

from alembic import op

revision = "20260429_017"
down_revision = "20260429_016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE user_profiles AS up
        SET education = '[]'::jsonb
        FROM users AS u
        WHERE up.user_id = u.id
          AND up.education IS NULL
          AND u.profile_completed IS TRUE
        """
    )


def downgrade() -> None:
    # Data-only fix; reversing would break completed users again.
    pass
