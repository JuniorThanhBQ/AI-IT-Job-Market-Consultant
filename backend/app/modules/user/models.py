from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.consultant.models import ConsultantHistory
    from app.modules.consultee_profile.models import ConsulteeProfile


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    is_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False
    username: str | None = Field(default=None, max_length=255)
    last_login: datetime | None = Field(
        default=None,
        sa_type=cast(Any, DateTime(timezone=True)),
    )


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: str | None = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    email: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    username: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    username: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str | None = Field(default=None, nullable=True)
    google_id: str | None = Field(default=None, unique=True, index=True, nullable=True)
    github_id: str | None = Field(default=None, unique=True, index=True, nullable=True)

    consultant_histories: list[ConsultantHistory] = Relationship(
        sa_relationship=relationship(
            "ConsultantHistory",
            back_populates="user",
            cascade="all, delete-orphan",
            passive_deletes=True,
            lazy="select",
        )
    )
    consultee_profile: ConsulteeProfile | None = Relationship(
        sa_relationship=relationship(
            "ConsulteeProfile",
            back_populates="user",
            uselist=False,
            cascade="all, delete-orphan",
            passive_deletes=True,
            lazy="joined",
        )
    )


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
