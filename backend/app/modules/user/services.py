from datetime import timedelta

from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.modules.user import repository as user_repo
from app.modules.user.exceptions import (
    InactiveUserError,
    IncorrectPasswordError,
    InvalidConfirmPassword,
    InvalidCredentialsError,
    InvalidVerificationStatus,
    InvalidVerificationTokenError,
    PasswordMismatchError,
    SamePasswordError,
    UserAlreadyExistsError,
    UserAlreadyVerifiedError,
    UserNotFoundError,
)
from app.modules.user.models import User
from app.modules.user.schemas import (
    MessageResponse,
    PasswordReset,
    Token,
    UserPublic,
    UserRegister,
)
from app.utils.utils import (
    generate_verification_email,
    generate_verification_token,
    send_email,
    verify_verification_token,
)


def register_user(*, session: Session, user_in: UserRegister) -> UserPublic:
    existing = user_repo.get_user_by_email(session=session, email=user_in.email)
    if existing:
        raise UserAlreadyExistsError("A user with this email already exists.")

    if user_in.confirm_password != user_in.password:
        raise InvalidConfirmPassword("Passwords do not match.")

    user = user_repo.create_user(
        session=session,
        email=user_in.email,
        password=user_in.password,
        username=user_in.username,
    )
    if settings.smtp.emails_enabled:
        token = generate_verification_token(user.email)
        email_data = generate_verification_email(
            email_to=user.email,
            username=user.username or user.email,
            token=token,
        )
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return UserPublic.model_validate(user)


def login_user(*, session: Session, email_name: str, password: str) -> Token:
    user = user_repo.authenticate(
        session=session, email_name=email_name, password=password
    )
    if not user:
        raise InvalidCredentialsError("Incorrect account or password")
    if not user.is_active:
        raise InactiveUserError("Inactive user")
    if not user.is_verified:
        raise InvalidVerificationStatus("This account is not verified")

    user_repo.update_last_login(session=session, user=user)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.email, expires_delta=access_token_expires
        )
    )


def reset_password(
    *, session: Session, user: User, data: PasswordReset
) -> MessageResponse:
    if data.new_password != data.confirm_new_password:
        raise PasswordMismatchError("New password and confirm password do not match.")
    if data.old_password == data.new_password:
        raise SamePasswordError("New password cannot be the same as the old password.")
    if not user.hashed_password:
        raise IncorrectPasswordError("Incorrect old password.")

    is_valid, _ = security.verify_password(data.old_password, user.hashed_password)
    if not is_valid:
        raise IncorrectPasswordError("Incorrect old password.")

    user_repo.update_password(
        session=session, user=user, new_password=data.new_password
    )
    return MessageResponse(message="Password updated successfully")


def verify_email(*, session: Session, token: str) -> MessageResponse:
    email = verify_verification_token(token)
    if not email:
        raise InvalidVerificationTokenError("Invalid or expired verification token.")

    user = user_repo.get_user_by_email(session=session, email=email)
    if not user:
        raise UserNotFoundError("User not found.")
    if user.is_verified:
        return MessageResponse(message="Account already verified")

    user_repo.update_user(
        session=session, db_user=user, user_data={"is_verified": True}
    )
    return MessageResponse(message="Account verified successfully")


def send_verification_email(*, session: Session, email: str) -> MessageResponse:
    user = user_repo.get_user_by_email(session=session, email=email)
    if not user:
        raise UserNotFoundError("User not found.")
    if user.is_verified:
        raise UserAlreadyVerifiedError("User is already verified.")

    token = generate_verification_token(user.email)
    email_data = generate_verification_email(
        email_to=user.email,
        username=user.username or user.email,
        token=token,
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return MessageResponse(message="Verification email sent successfully")
