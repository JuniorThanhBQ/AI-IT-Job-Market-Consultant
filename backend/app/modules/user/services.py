from datetime import timedelta

from fastapi import HTTPException
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.modules.user import repository as user_repo
from app.modules.user.schemas import (
    Token,
    UserPublic,
    UserRegister,
)


def register_user(*, session: Session, user_in: UserRegister) -> UserPublic:
    existing = user_repo.get_user_by_email(session=session, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="A user with this email already exists.",
        )
    user = user_repo.create_user(
        session=session,
        email=user_in.email,
        password=user_in.password,
        username=user_in.username,
    )
    return UserPublic.model_validate(user)


def login_user(*, session: Session, email: str, password: str) -> Token:
    user = user_repo.authenticate(session=session, email=email, password=password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    user_repo.update_last_login(session=session, user=user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.email, expires_delta=access_token_expires
        )
    )
