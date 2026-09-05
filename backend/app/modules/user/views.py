from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.deps import CurrentUser, SessionDep
from app.modules.user import services as user_service
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
from app.modules.user.schemas import (
    MessageResponse,
    PasswordReset,
    Token,
    UserPublic,
    UserRegister,
    VerificationConfirm,
    VerificationRequest,
)

auth_router = APIRouter()
router = APIRouter()


@auth_router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(*, session: SessionDep, user_in: UserRegister) -> UserPublic:
    try:
        return user_service.register_user(session=session, user_in=user_in)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except InvalidConfirmPassword as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@auth_router.post("/sessions/", response_model=Token)
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    try:
        return user_service.login_user(
            session=session, email_name=form_data.username, password=form_data.password
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    except (InactiveUserError, InvalidVerificationStatus) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc


@auth_router.patch("/password/", response_model=MessageResponse)
def reset_password(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: PasswordReset,
) -> MessageResponse:
    try:
        return user_service.reset_password(
            session=session, user=current_user, data=data
        )
    except (PasswordMismatchError, SamePasswordError, IncorrectPasswordError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@auth_router.get("/verification/")
def verify_email_get(*, session: SessionDep, token: str) -> RedirectResponse:
    try:
        user_service.verify_email(session=session, token=token)
        return RedirectResponse(
            url=settings.FRONTEND_HOST, status_code=status.HTTP_302_FOUND
        )
    except InvalidVerificationTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@auth_router.post("/verification/", response_model=MessageResponse)
def verify_email(*, session: SessionDep, data: VerificationConfirm) -> MessageResponse:
    try:
        return user_service.verify_email(session=session, token=data.token)
    except InvalidVerificationTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@auth_router.post("/verification/email/", response_model=MessageResponse)
def send_verification_email(
    *, session: SessionDep, data: VerificationRequest
) -> MessageResponse:
    try:
        return user_service.send_verification_email(session=session, email=data.email)
    except UserAlreadyVerifiedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
