from datetime import timedelta

from fastapi import HTTPException
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.modules.user import repository as user_repo
from app.modules.user.models import User
from app.modules.user.schemas import (
    MessageResponse,
    Token,
    UserPublic,
    UserRegister,
)
from app.utils.utils import generate_password_reset_token, verify_password_reset_token


def register_user(*, session: Session, user_in: UserRegister) -> UserPublic:
    """Register a new user with auto-created ConsulteeProfile + CurriculumVitae."""
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
    """Authenticate user and return JWT token."""
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


def verify_account(*, session: Session, token: str) -> MessageResponse:
    """Temp mock: mark user as verified. Will be enhanced later."""
    # TODO: Implement real token verification logic
    email = verify_password_reset_token(token=token)
    if not email:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token"
        )

    user = user_repo.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    session.add(user)
    session.commit()
    return MessageResponse(message="Account verified successfully (mocked)")


def request_password_reset(*, session: Session, email: str) -> MessageResponse:
    """Generate a password reset token (mock email send)."""
    user = user_repo.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404, detail="User with this email does not exist"
        )

    _token = generate_password_reset_token(email=email)
    # TODO: Send email with reset token
    return MessageResponse(
        message="Password recovery email sent (mocked). Token generated."
    )


def reset_password(
    *, session: Session, token: str, new_password: str
) -> MessageResponse:
    """Reset password using a token. Only allowed if user is_verified."""
    email = verify_password_reset_token(token=token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = user_repo.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Account must be verified before resetting password",
        )

    user.hashed_password = security.get_password_hash(new_password)
    session.add(user)
    session.commit()
    return MessageResponse(message="Password updated successfully")


def update_my_password(
    *, session: Session, user: User, current_password: str, new_password: str
) -> MessageResponse:
    """Change password for authenticated user."""
    if not user.hashed_password:
        raise HTTPException(
            status_code=400,
            detail="Password is not set. Use password recovery or social account settings.",
        )
    is_valid, _ = security.verify_password(current_password, user.hashed_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Incorrect password")
    if current_password == new_password:
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as current password",
        )

    user.hashed_password = security.get_password_hash(new_password)
    session.add(user)
    session.commit()
    return MessageResponse(message="Password updated successfully")
