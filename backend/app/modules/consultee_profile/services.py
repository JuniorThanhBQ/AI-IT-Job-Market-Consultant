import uuid

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.consultee_profile import repository as profile_repo
from app.modules.consultee_profile.models import ConsulteeProfile
from app.modules.consultee_profile.schemas import (
    ConsulteeProfileRead,
    ConsulteeProfileUpdate,
)


def _get_profile_or_404(session: Session, user_id: uuid.UUID) -> ConsulteeProfile:
    profile = profile_repo.get_profile_by_user_id(session=session, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def get_my_profile(*, session: Session, user_id: uuid.UUID) -> ConsulteeProfileRead:
    profile = _get_profile_or_404(session, user_id)
    return ConsulteeProfileRead.model_validate(profile)


def update_my_profile(
    *, session: Session, user_id: uuid.UUID, data: ConsulteeProfileUpdate
) -> ConsulteeProfileRead:
    profile = _get_profile_or_404(session, user_id)
    updated = profile_repo.update_profile(
        session=session, profile=profile, data=data.model_dump(exclude_unset=True)
    )
    return ConsulteeProfileRead.model_validate(updated)
