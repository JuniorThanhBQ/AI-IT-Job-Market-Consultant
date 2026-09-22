import uuid

from sqlmodel import Session

from app.modules.consultee_profile import repository as profile_repo
from app.modules.consultee_profile.exceptions import (
    CVNotFoundError,
    InvalidProjectDateRangeError,
    ProfileNotFoundError,
    ProjectLimitExceededError,
    ProjectNotFoundError,
)
from app.modules.consultee_profile.models import (
    ConsulteeProfile,
    CurriculumVitae,
    CurriculumVitaeProject,
)
from app.modules.consultee_profile.schemas import (
    ConsulteeProfileRead,
    ConsulteeProfileUpdate,
    CurriculumVitaeProjectCreate,
    CurriculumVitaeProjectRead,
    CurriculumVitaeProjectUpdate,
    CurriculumVitaeRead,
    CurriculumVitaeUpdate,
)
from app.modules.user.schemas import MessageResponse
from app.utils.validators import validate_date_range


def get_profile_or_raise(*, session: Session, user_id: uuid.UUID) -> ConsulteeProfile:
    profile = profile_repo.get_profile_by_user_id(session=session, user_id=user_id)
    if not profile:
        raise ProfileNotFoundError("Profile not found")

    return profile


def get_my_profile(*, session: Session, user_id: uuid.UUID) -> ConsulteeProfileRead:
    profile = get_profile_or_raise(session=session, user_id=user_id)
    return ConsulteeProfileRead.model_validate(profile)


def update_my_profile(
    *, session: Session, user_id: uuid.UUID, data: ConsulteeProfileUpdate
) -> ConsulteeProfileRead:
    profile = get_profile_or_raise(session=session, user_id=user_id)
    updated = profile_repo.update_profile(
        session=session, profile=profile, data=data.model_dump(exclude_unset=True)
    )
    return ConsulteeProfileRead.model_validate(updated)


def get_cv_or_raise(*, session: Session, user_id: uuid.UUID) -> CurriculumVitae:
    cv = profile_repo.get_cv_by_user_id(session=session, user_id=user_id)
    if not cv:
        raise CVNotFoundError("Curriculum Vitae not found")

    return cv


def get_my_cv(*, session: Session, user_id: uuid.UUID) -> CurriculumVitaeRead:
    cv = get_cv_or_raise(session=session, user_id=user_id)
    return CurriculumVitaeRead.model_validate(cv)


def update_my_cv(
    *, session: Session, user_id: uuid.UUID, data: CurriculumVitaeUpdate
) -> CurriculumVitaeRead:
    cv = get_cv_or_raise(session=session, user_id=user_id)
    updated = profile_repo.update_cv(
        session=session, cv=cv, data=data.model_dump(exclude_unset=True)
    )
    return CurriculumVitaeRead.model_validate(updated)


def get_project_or_raise(
    *, session: Session, cv_id: int, project_id: int
) -> CurriculumVitaeProject:
    project = profile_repo.get_project_by_id(session=session, project_id=project_id)
    if not project or project.cv_id != cv_id:
        raise ProjectNotFoundError("Project not found")

    return project


def get_my_cv_projects(
    *, session: Session, user_id: uuid.UUID
) -> list[CurriculumVitaeProjectRead]:
    cv = get_cv_or_raise(session=session, user_id=user_id)
    if cv.id is None:
        raise CVNotFoundError("Curriculum Vitae not found")

    projects = profile_repo.get_projects_by_cv_id(session=session, cv_id=cv.id)
    return [CurriculumVitaeProjectRead.model_validate(p) for p in projects]


def create_cv_project(
    *, session: Session, user_id: uuid.UUID, data: CurriculumVitaeProjectCreate
) -> CurriculumVitaeProjectRead:
    cv = get_cv_or_raise(session=session, user_id=user_id)
    if cv.id is None:
        raise CVNotFoundError("Curriculum Vitae not found")

    existing_projects = profile_repo.get_projects_by_cv_id(session=session, cv_id=cv.id)
    if len(existing_projects) >= 3:
        raise ProjectLimitExceededError(
            "A Curriculum Vitae can have at most 3 projects."
        )

    try:
        validate_date_range(data.start_date, data.end_date)
    except ValueError as exc:
        raise InvalidProjectDateRangeError(str(exc)) from exc

    project = profile_repo.create_project(
        session=session, cv_id=cv.id, data=data.model_dump()
    )
    return CurriculumVitaeProjectRead.model_validate(project)


def update_cv_project(
    *,
    session: Session,
    user_id: uuid.UUID,
    project_id: int,
    data: CurriculumVitaeProjectUpdate,
) -> CurriculumVitaeProjectRead:
    cv = get_cv_or_raise(session=session, user_id=user_id)
    if cv.id is None:
        raise CVNotFoundError("Curriculum Vitae not found")

    project = get_project_or_raise(session=session, cv_id=cv.id, project_id=project_id)
    update_dict = data.model_dump(exclude_unset=True)
    new_start = update_dict.get("start_date", project.start_date)
    new_end = update_dict.get("end_date", project.end_date)
    try:
        validate_date_range(new_start, new_end)
    except ValueError as exc:
        raise InvalidProjectDateRangeError(str(exc)) from exc

    updated = profile_repo.update_project(
        session=session, project=project, data=update_dict
    )
    return CurriculumVitaeProjectRead.model_validate(updated)


def delete_cv_project(
    *, session: Session, user_id: uuid.UUID, project_id: int
) -> MessageResponse:
    cv = get_cv_or_raise(session=session, user_id=user_id)
    if cv.id is None:
        raise CVNotFoundError("Curriculum Vitae not found")

    project = get_project_or_raise(session=session, cv_id=cv.id, project_id=project_id)
    profile_repo.delete_project(session=session, project=project)
    return MessageResponse(message="Project deleted successfully")
