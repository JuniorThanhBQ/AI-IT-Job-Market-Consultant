import uuid
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import func, select

from app.core import security
from app.core.config import settings
from app.core.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.modules.user import repository as user_repo
from app.modules.user.models import (
    Message,
    NewPassword,
    Token,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils.utils import (
    generate_password_reset_token,
    verify_password_reset_token,
)

router = APIRouter()
login_router = APIRouter()


@login_router.post("/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = user_repo.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.email, expires_delta=access_token_expires
        )
    )


@login_router.post("/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    return current_user


@login_router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    user = user_repo.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    _password_reset_token = generate_password_reset_token(email=email)

    return Message(message="Password recovery email sent (mocked). Token generated.")


@login_router.post("/reset-password/")
def reset_password(new_password: NewPassword, session: SessionDep) -> Message:
    email = verify_password_reset_token(token=new_password.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = user_repo.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    hashed_password = security.get_password_hash(new_password.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/", response_model=UsersPublic)
def read_users(
    session: SessionDep,
    _current_user: Annotated[User, Depends(get_current_active_superuser)],
    skip: int = 0,
    limit: int = 100,
) -> Any:
    stat = select(User).offset(skip).limit(limit)
    users = session.exec(stat).all()
    count = session.exec(select(func.count()).select_from(User)).one()
    return UsersPublic(data=users, count=count)


@router.post("/", response_model=UserPublic)
def create_user(
    *,
    session: SessionDep,
    _current_user: Annotated[User, Depends(get_current_active_superuser)],
    user_in: UserCreate,
) -> Any:
    user = user_repo.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    return user_repo.create_user(session=session, user_create=user_in)


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *,
    session: SessionDep,
    user_in: UserUpdateMe,
    current_user: CurrentUser,
) -> Any:
    if user_in.email:
        existing_user = user_repo.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=400, detail="Email already registered by another user"
            )

    current_user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(current_user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *,
    session: SessionDep,
    body: UpdatePassword,
    current_user: CurrentUser,
) -> Any:
    is_valid, _ = security.verify_password(
        body.current_password, current_user.hashed_password
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as current password",
        )

    hashed_password = security.get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID,
    session: SessionDep,
    _current_user: Annotated[User, Depends(get_current_active_superuser)],
) -> Any:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user_by_id(
    *,
    session: SessionDep,
    _current_user: Annotated[User, Depends(get_current_active_superuser)],
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = user_repo.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=400, detail="Email already registered by another user"
            )

    return user_repo.update_user(session=session, db_user=db_user, user_in=user_in)


@router.delete("/{user_id}", response_model=Message)
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
    return Message(message="User deleted successfully")
