import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import func, select

from app.core.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.modules.user import repository as user_repo
from app.modules.user import services as user_service
from app.modules.user.models import User
from app.modules.user.schemas import (
    ForgotPassword,
    MessageResponse,
    NewPassword,
    Token,
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    VerifyAccount,
)

auth_router = APIRouter()
router = APIRouter()


@auth_router.post("/register", response_model=UserPublic, status_code=201)
def register(*, session: SessionDep, user_in: UserRegister) -> Any:
    return user_service.register_user(session=session, user_in=user_in)


@auth_router.post("/login", response_model=Token)
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    return user_service.login_user(
        session=session, email=form_data.username, password=form_data.password
    )


@auth_router.post("/verify", response_model=MessageResponse)
def verify_account(*, session: SessionDep, body: VerifyAccount) -> Any:
    return user_service.verify_account(session=session, token=body.token)


@auth_router.post("/password/forgot", response_model=MessageResponse)
def forgot_password(*, session: SessionDep, body: ForgotPassword) -> Any:
    return user_service.request_password_reset(session=session, email=body.email)


@auth_router.post("/password/reset", response_model=MessageResponse)
def reset_password(*, session: SessionDep, body: NewPassword) -> Any:
    return user_service.reset_password(
        session=session, token=body.token, new_password=body.new_password
    )


@auth_router.get("/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    return current_user


@router.get("/", response_model=UsersPublic)
def list_users(
    session: SessionDep,
    _current_user: Annotated[User, Depends(get_current_active_superuser)],
    skip: int = 0,
    limit: int = 100,
) -> Any:
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    count = session.exec(select(func.count()).select_from(User)).one()
    return UsersPublic(data=users, count=count)


@router.post("/", response_model=UserPublic, status_code=201)
def create_user(
    *,
    session: SessionDep,
    _current_user: Annotated[User, Depends(get_current_active_superuser)],
    user_in: UserCreate,
) -> Any:
    existing = user_repo.get_user_by_email(session=session, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="A user with this email already exists.",
        )
    return user_repo.create_user(
        session=session,
        email=user_in.email,
        password=user_in.password,
        username=user_in.username,
    )


@router.get("/me", response_model=UserPublic)
def get_me(current_user: CurrentUser) -> Any:
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_me(
    *,
    session: SessionDep,
    user_in: UserUpdateMe,
    current_user: CurrentUser,
) -> Any:
    if user_in.email:
        existing = user_repo.get_user_by_email(session=session, email=user_in.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=409,
                detail="Email already registered by another user",
            )

    current_user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(current_user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=MessageResponse)
def update_my_password(
    *,
    session: SessionDep,
    body: UpdatePassword,
    current_user: CurrentUser,
) -> Any:
    return user_service.update_my_password(
        session=session,
        user=current_user,
        current_password=body.current_password,
        new_password=body.new_password,
    )


@router.get("/{user_id}", response_model=UserPublic)
def get_user(
    user_id: uuid.UUID,
    session: SessionDep,
    _current_user: Annotated[User, Depends(get_current_active_superuser)],
) -> Any:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    *,
    session: SessionDep,
    _current_user: Annotated[User, Depends(get_current_active_superuser)],
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_in.email:
        existing = user_repo.get_user_by_email(session=session, email=user_in.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=409,
                detail="Email already registered by another user",
            )
    return user_repo.update_user(
        session=session,
        db_user=db_user,
        user_data=user_in.model_dump(exclude_unset=True),
    )


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    *,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    user_id: uuid.UUID,
) -> Any:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Superusers cannot delete themselves"
        )
    session.delete(user)
    session.commit()
    return MessageResponse(message="User deleted successfully")
