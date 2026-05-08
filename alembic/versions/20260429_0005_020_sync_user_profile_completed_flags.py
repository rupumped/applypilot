"""Set users.profile_completed when the profile matches POST /complete rules.

Revision ID: 20260429_020
Revises: 20260429_019
Create Date: 2026-04-29

Context
-------
Revisions 016–018 add ``education`` and backfill ``[]`` so the *education step*
is satisfied the same way as work experience (non-NULL ``[]`` = step saved).
019 clears cached ``GET /profile`` JSON.

Problem
-------
``users.profile_completed`` can stay ``FALSE`` for legacy accounts who already
had **basic info, work experience, skills, and career preferences** in good
shape, but never re-ran ``POST /profile/complete`` after the new education
column existed. The ``[]`` backfill fixes the *education* gap in data; this
revision fixes the **User** flag when the row now passes the **same five
checks** as ``POST /complete`` (we cannot detect “only education was ever
wrong” in SQL after the fact, so we require **all** checks—if skills or work
are still incomplete, we do not flip the flag).

Solution
--------
For each user with ``profile_completed = FALSE``, load ``user_profiles`` and
require:

- The **four** sections that existed before education: basic info, work
  experience, skills, career preferences — all must pass.
- **Education** must pass too (``[]`` or saved entries), same as after 018.

That is identical to “all five ``_check_*`` pass”; we evaluate the four and
education explicitly so the intent matches the product story above.

Then clear the user_profile Redis cache again so JWT and cached payloads
align.
"""

from datetime import datetime, timezone

from alembic import op
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

revision = "20260429_020"
down_revision = "20260429_019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    SessionLocal = sessionmaker(bind=bind, class_=Session, autoflush=False)
    session = SessionLocal()
    try:
        from models.database import User, UserProfile as UserProfileModel
        from api.profile import (
            _check_basic_info_completion,
            _check_career_preferences_completion,
            _check_education_completion,
            _check_skills_qualifications_completion,
            _check_work_experience_completion,
        )
        from utils.cache import invalidate_all_user_profile_caches_sync

        users = session.scalars(select(User)).all()
        now = datetime.now(timezone.utc)
        for user in users:
            if user.profile_completed:
                continue
            prof = session.scalar(
                select(UserProfileModel).where(UserProfileModel.user_id == user.id)
            )
            if prof is None:
                continue
            # Same rules as POST /complete: all sections that existed before
            # education, plus education after [] / user saves.
            basic_ok = _check_basic_info_completion(prof)
            work_ok = _check_work_experience_completion(prof)
            skills_ok = _check_skills_qualifications_completion(prof)
            career_ok = _check_career_preferences_completion(prof)
            education_ok = _check_education_completion(prof)
            if not (basic_ok and work_ok and skills_ok and career_ok and education_ok):
                continue
            user.profile_completed = True
            user.profile_completion_percentage = 100
            user.updated_at = now
        session.commit()
        invalidate_all_user_profile_caches_sync()
    finally:
        session.close()


def downgrade() -> None:
    pass
