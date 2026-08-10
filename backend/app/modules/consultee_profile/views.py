from typing import Any

from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.modules.consultee_profile import services as profile_service
from app.modules.consultee_profile.schemas import (
    ConsulteeProfileRead,
    ConsulteeProfileUpdate,
)

profile_router = APIRouter()
cv_router = APIRouter()


@profile_router.get("/", response_model=ConsulteeProfileRead)
def get_my_profile(*, session: SessionDep, current_user: CurrentUser) -> Any:
    return profile_service.get_my_profile(session=session, user_id=current_user.id)


@profile_router.patch("/", response_model=ConsulteeProfileRead)
def update_my_profile(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: ConsulteeProfileUpdate,
) -> Any:
    return profile_service.update_my_profile(
        session=session, user_id=current_user.id, data=data
    )
