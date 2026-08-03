from typing import Any

from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.modules.consultee_profile import services as profile_service
from app.modules.consultee_profile.schemas import (
    ConsulteeProfileRead,
    ConsulteeProfileUpdate,
    CurriculumVitaeProjectCreate,
    CurriculumVitaeProjectRead,
    CurriculumVitaeProjectUpdate,
    CurriculumVitaeRead,
    CurriculumVitaeUpdate,
    CvAttachmentUpload,
)
from app.modules.user.schemas import MessageResponse

profile_router = APIRouter()
cv_router = APIRouter()


# ──────────────────────────────────────────────
# Profile endpoints
# ──────────────────────────────────────────────


@profile_router.get("/", response_model=ConsulteeProfileRead)
def get_my_profile(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """Get the authenticated user's consultee profile."""
    return profile_service.get_my_profile(session=session, user_id=current_user.id)


@profile_router.patch("/", response_model=ConsulteeProfileRead)
def update_my_profile(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: ConsulteeProfileUpdate,
) -> Any:
    """Partially update the authenticated user's consultee profile."""
    return profile_service.update_my_profile(
        session=session, user_id=current_user.id, data=data
    )


# ──────────────────────────────────────────────
# CV endpoints
# ──────────────────────────────────────────────


@cv_router.get("/", response_model=CurriculumVitaeRead)
def get_my_cv(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """Get the authenticated user's curriculum vitae."""
    return profile_service.get_my_cv(session=session, user_id=current_user.id)


@cv_router.put("/", response_model=CurriculumVitaeRead)
def update_my_cv(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: CurriculumVitaeUpdate,
) -> Any:
    """Update the authenticated user's curriculum vitae."""
    return profile_service.update_my_cv(
        session=session,
        user_id=current_user.id,
        data=data.model_dump(exclude_unset=True),
    )


@cv_router.post("/attachment", response_model=MessageResponse)
def upload_cv_attachment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    upload: CvAttachmentUpload,
) -> Any:
    """Upload a CV attachment (temp mock)."""
    return profile_service.upload_cv_attachment(
        session=session, user_id=current_user.id, upload=upload
    )


@cv_router.post("/projects", response_model=CurriculumVitaeProjectRead, status_code=201)
def create_cv_project(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: CurriculumVitaeProjectCreate,
) -> Any:
    """Add a project to the authenticated user's CV."""
    return profile_service.create_cv_project(
        session=session, user_id=current_user.id, data=data
    )


@cv_router.patch("/projects/{project_id}", response_model=CurriculumVitaeProjectRead)
def update_cv_project(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
    data: CurriculumVitaeProjectUpdate,
) -> Any:
    """Update a specific project in the authenticated user's CV."""
    return profile_service.update_cv_project(
        session=session,
        user_id=current_user.id,
        project_id=project_id,
        data=data,
    )


@cv_router.delete("/projects/{project_id}", response_model=MessageResponse)
def delete_cv_project(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
) -> Any:
    """Delete a specific project from the authenticated user's CV."""
    return profile_service.delete_cv_project(
        session=session, user_id=current_user.id, project_id=project_id
    )
