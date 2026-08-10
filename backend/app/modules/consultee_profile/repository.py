import uuid

from sqlmodel import Session, select

from app.modules.consultee_profile.models import (
    ConsulteeProfile,
    CurriculumVitae,
)


def get_profile_by_user_id(
    *, session: Session, user_id: uuid.UUID
) -> ConsulteeProfile | None:
    statement = select(ConsulteeProfile).where(ConsulteeProfile.user_id == user_id)
    return session.exec(statement).first()


def update_profile(
    *, session: Session, profile: ConsulteeProfile, data: dict
) -> ConsulteeProfile:
    profile.sqlmodel_update(data)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def update_cv(*, session: Session, cv: CurriculumVitae, data: dict) -> CurriculumVitae:
    cv.sqlmodel_update(data)
    session.add(cv)
    session.commit()
    session.refresh(cv)
    return cv
