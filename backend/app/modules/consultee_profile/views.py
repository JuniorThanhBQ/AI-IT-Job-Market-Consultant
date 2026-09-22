from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, SessionDep
from app.modules.consultee_profile import services as profile_service
from app.modules.consultee_profile.exceptions import (
    CVNotFoundError,
    InvalidProjectDateRangeError,
    ProfileNotFoundError,
    ProjectLimitExceededError,
    ProjectNotFoundError,
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

profile_router = APIRouter()


@profile_router.get("/", response_model=ConsulteeProfileRead)
def get_my_profile(
    *, session: SessionDep, current_user: CurrentUser
) -> ConsulteeProfileRead:
    try:
        return profile_service.get_my_profile(session=session, user_id=current_user.id)
    except ProfileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@profile_router.patch("/", response_model=ConsulteeProfileRead)
def update_my_profile(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: ConsulteeProfileUpdate,
) -> ConsulteeProfileRead:
    try:
        return profile_service.update_my_profile(
            session=session, user_id=current_user.id, data=data
        )
    except ProfileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@profile_router.get("/cv/", response_model=CurriculumVitaeRead)
def get_my_cv(*, session: SessionDep, current_user: CurrentUser) -> CurriculumVitaeRead:
    try:
        return profile_service.get_my_cv(session=session, user_id=current_user.id)
    except CVNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@profile_router.patch("/cv/", response_model=CurriculumVitaeRead)
def update_my_cv(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: CurriculumVitaeUpdate,
) -> CurriculumVitaeRead:
    try:
        return profile_service.update_my_cv(
            session=session, user_id=current_user.id, data=data
        )
    except CVNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@profile_router.get("/cv/projects/", response_model=list[CurriculumVitaeProjectRead])
def get_my_cv_projects(
    *, session: SessionDep, current_user: CurrentUser
) -> list[CurriculumVitaeProjectRead]:
    try:
        return profile_service.get_my_cv_projects(
            session=session, user_id=current_user.id
        )
    except CVNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@profile_router.post(
    "/cv/projects/",
    response_model=CurriculumVitaeProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_cv_project(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: CurriculumVitaeProjectCreate,
) -> CurriculumVitaeProjectRead:
    try:
        return profile_service.create_cv_project(
            session=session, user_id=current_user.id, data=data
        )
    except CVNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except (ProjectLimitExceededError, InvalidProjectDateRangeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@profile_router.patch(
    "/cv/projects/{project_id}/", response_model=CurriculumVitaeProjectRead
)
def update_cv_project(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: int,
    data: CurriculumVitaeProjectUpdate,
) -> CurriculumVitaeProjectRead:
    try:
        return profile_service.update_cv_project(
            session=session,
            user_id=current_user.id,
            project_id=project_id,
            data=data,
        )
    except (CVNotFoundError, ProjectNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except InvalidProjectDateRangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@profile_router.delete("/cv/projects/{project_id}/", response_model=MessageResponse)
def delete_cv_project(
    *, session: SessionDep, current_user: CurrentUser, project_id: int
) -> MessageResponse:
    try:
        return profile_service.delete_cv_project(
            session=session, user_id=current_user.id, project_id=project_id
        )
    except (CVNotFoundError, ProjectNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
