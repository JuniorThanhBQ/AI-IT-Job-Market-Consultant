from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import SessionDep
from app.modules.user import services as user_service
from app.modules.user.schemas import (
    Token,
    UserPublic,
    UserRegister,
)

auth_router = APIRouter()
router = APIRouter()


@auth_router.post("/", response_model=UserPublic, status_code=201)
def register(*, session: SessionDep, user_in: UserRegister) -> Any:
    return user_service.register_user(session=session, user_in=user_in)


@auth_router.post("/sessions/", response_model=Token)
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    return user_service.login_user(
        session=session, email=form_data.username, password=form_data.password
    )
