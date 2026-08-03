import uuid

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
    *, session: Session, profile: ConsulteeProfile, data: dict
) -> ConsulteeProfile:
    profile.sqlmodel_update(data)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def get_cv_by_profile_id(
    *, session: Session, profile_id: int
) -> CurriculumVitae | None:
    statement = select(CurriculumVitae).where(CurriculumVitae.profile_id == profile_id)
    return session.exec(statement).first()


def update_cv(*, session: Session, cv: CurriculumVitae, data: dict) -> CurriculumVitae:
    cv.sqlmodel_update(data)
    session.add(cv)
    session.commit()
    session.refresh(cv)
    return cv


def get_cv_project(
    *, session: Session, project_id: int
) -> CurriculumVitaeProject | None:
    return session.get(CurriculumVitaeProject, project_id)


def create_cv_project(
    *, session: Session, cv_id: int, data: dict
) -> CurriculumVitaeProject:
    project = CurriculumVitaeProject(cv_id=cv_id, **data)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def update_cv_project(
    *, session: Session, project: CurriculumVitaeProject, data: dict
) -> CurriculumVitaeProject:
    project.sqlmodel_update(data)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_cv_project(*, session: Session, project: CurriculumVitaeProject) -> None:
    session.delete(project)
    session.commit()
