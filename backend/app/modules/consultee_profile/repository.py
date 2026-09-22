import uuid
from typing import Any

from sqlmodel import Session, select

from app.modules.consultee_profile.models import (
    ConsulteeProfile,
    CurriculumVitae,
    CurriculumVitaeProject,
)


def get_profile_by_user_id(
    *, session: Session, user_id: uuid.UUID
) -> ConsulteeProfile | None:
    statement = select(ConsulteeProfile).where(ConsulteeProfile.user_id == user_id)
    return session.exec(statement).first()


def update_profile(
    *, session: Session, profile: ConsulteeProfile, data: dict[str, Any]
) -> ConsulteeProfile:
    profile.sqlmodel_update(data)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def get_cv_by_user_id(
    *, session: Session, user_id: uuid.UUID
) -> CurriculumVitae | None:
    statement = (
        select(CurriculumVitae)
        .join(ConsulteeProfile)
        .where(ConsulteeProfile.user_id == user_id)
    )
    return session.exec(statement).first()


def update_cv(
    *, session: Session, cv: CurriculumVitae, data: dict[str, Any]
) -> CurriculumVitae:
    cv.sqlmodel_update(data)
    session.add(cv)
    session.commit()
    session.refresh(cv)
    return cv


def get_projects_by_cv_id(
    *, session: Session, cv_id: int
) -> list[CurriculumVitaeProject]:
    statement = select(CurriculumVitaeProject).where(
        CurriculumVitaeProject.cv_id == cv_id
    )
    return list(session.exec(statement).all())


def get_project_by_id(
    *, session: Session, project_id: int
) -> CurriculumVitaeProject | None:
    statement = select(CurriculumVitaeProject).where(
        CurriculumVitaeProject.id == project_id
    )
    return session.exec(statement).first()


def create_project(
    *, session: Session, cv_id: int, data: dict[str, Any]
) -> CurriculumVitaeProject:
    project = CurriculumVitaeProject(cv_id=cv_id, **data)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def update_project(
    *, session: Session, project: CurriculumVitaeProject, data: dict[str, Any]
) -> CurriculumVitaeProject:
    project.sqlmodel_update(data)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_project(*, session: Session, project: CurriculumVitaeProject) -> None:
    session.delete(project)
    session.commit()
