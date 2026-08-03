import uuid

from fastapi import HTTPException
from sqlmodel import Session

from app.modules.consultee_profile import repository as profile_repo
from app.modules.consultee_profile.models import (
    ConsulteeProfile,
    CurriculumVitae,
)
from app.modules.consultee_profile.schemas import (
    ConsulteeProfileRead,
    ConsulteeProfileUpdate,
    CurriculumVitaeProjectCreate,
    CurriculumVitaeProjectRead,
    CurriculumVitaeProjectUpdate,
    CurriculumVitaeRead,
    CvAttachmentUpload,
)
from app.modules.user.schemas import MessageResponse


def _get_profile_or_404(session: Session, user_id: uuid.UUID) -> ConsulteeProfile:
    profile = profile_repo.get_profile_by_user_id(session=session, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def _get_cv_or_404(session: Session, profile_id: int) -> CurriculumVitae:
    cv = profile_repo.get_cv_by_profile_id(session=session, profile_id=profile_id)
    if not cv:
        raise HTTPException(status_code=404, detail="Curriculum Vitae not found")
    return cv


def get_my_profile(*, session: Session, user_id: uuid.UUID) -> ConsulteeProfileRead:
    """Get current user's consultee profile."""
    profile = _get_profile_or_404(session, user_id)
    return ConsulteeProfileRead.model_validate(profile)


def update_my_profile(
    *, session: Session, user_id: uuid.UUID, data: ConsulteeProfileUpdate
) -> ConsulteeProfileRead:
    """Partially update current user's consultee profile."""
    profile = _get_profile_or_404(session, user_id)
    updated = profile_repo.update_profile(
        session=session, profile=profile, data=data.model_dump(exclude_unset=True)
    )
    return ConsulteeProfileRead.model_validate(updated)


def get_my_cv(*, session: Session, user_id: uuid.UUID) -> CurriculumVitaeRead:
    """Get current user's curriculum vitae."""
    profile = _get_profile_or_404(session, user_id)
    assert profile.id is not None
    cv = _get_cv_or_404(session, profile.id)
    return CurriculumVitaeRead.model_validate(cv)


def update_my_cv(
    *, session: Session, user_id: uuid.UUID, data: dict
) -> CurriculumVitaeRead:
    """Update current user's curriculum vitae fields."""
    profile = _get_profile_or_404(session, user_id)
    assert profile.id is not None
    cv = _get_cv_or_404(session, profile.id)
    updated = profile_repo.update_cv(session=session, cv=cv, data=data)
    return CurriculumVitaeRead.model_validate(updated)


def upload_cv_attachment(
    *, session: Session, user_id: uuid.UUID, upload: CvAttachmentUpload
) -> MessageResponse:
    """Temp mock: set using_cv_mode=True and store filename as attachment."""
    profile = _get_profile_or_404(session, user_id)
    assert profile.id is not None
    cv = _get_cv_or_404(session, profile.id)
    # TODO: Implement real file upload logic
    profile_repo.update_cv(
        session=session,
        cv=cv,
        data={"using_cv_mode": True, "attachment": upload.filename},
    )
    return MessageResponse(
        message=f"CV attachment '{upload.filename}' uploaded successfully (mocked)"
    )


def create_cv_project(
    *, session: Session, user_id: uuid.UUID, data: CurriculumVitaeProjectCreate
) -> CurriculumVitaeProjectRead:
    """Add a project to current user's CV."""
    profile = _get_profile_or_404(session, user_id)
    assert profile.id is not None
    cv = _get_cv_or_404(session, profile.id)
    assert cv.id is not None
    project = profile_repo.create_cv_project(
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
    """Update a specific project in current user's CV."""
    profile = _get_profile_or_404(session, user_id)
    assert profile.id is not None
    cv = _get_cv_or_404(session, profile.id)
    assert cv.id is not None
    project = profile_repo.get_cv_project(session=session, project_id=project_id)
    if not project or project.cv_id != cv.id:
        raise HTTPException(status_code=404, detail="Project not found")
    updated = profile_repo.update_cv_project(
        session=session, project=project, data=data.model_dump(exclude_unset=True)
    )
    return CurriculumVitaeProjectRead.model_validate(updated)


def delete_cv_project(
    *, session: Session, user_id: uuid.UUID, project_id: int
) -> MessageResponse:
    """Delete a specific project from current user's CV."""
    profile = _get_profile_or_404(session, user_id)
    assert profile.id is not None
    cv = _get_cv_or_404(session, profile.id)
    assert cv.id is not None
    project = profile_repo.get_cv_project(session=session, project_id=project_id)
    if not project or project.cv_id != cv.id:
        raise HTTPException(status_code=404, detail="Project not found")
    profile_repo.delete_cv_project(session=session, project=project)
    return MessageResponse(message="Project deleted successfully")
