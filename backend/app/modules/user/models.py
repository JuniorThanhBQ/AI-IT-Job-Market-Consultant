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
