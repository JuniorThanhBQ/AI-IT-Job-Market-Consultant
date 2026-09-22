from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

from pydantic import ValidationInfo, field_validator
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship, validates
from sqlmodel import Field, Relationship, Session, SQLModel, select

from app.core.db import engine

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

    def __str__(self) -> str:
        return self.username or self.email


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

    @validates("is_superuser")
    def validate_superuser_assignment(self, key: str, value: bool) -> bool:
        if value:
            try:
                with Session(engine) as session:
                    existing = session.exec(
                        select(User).where(User.is_superuser == True)  # noqa: E712
                    ).first()
                    current_id = getattr(self, "id", None)
                    if existing and (current_id is None or existing.id != current_id):
                        raise ValueError("Only one account can be a superuser.")
            except Exception as e:
                if isinstance(e, ValueError):
                    raise
        return value

    @field_validator("is_superuser")
    @classmethod
    def validate_single_superuser(cls, value: bool, info: ValidationInfo) -> bool:
        if value:
            try:
                with Session(engine) as session:
                    existing = session.exec(
                        select(cls).where(cls.is_superuser == True)  # noqa: E712
                    ).first()
                    current_id = info.data.get("id") if info.data else None
                    if existing and (current_id is None or existing.id != current_id):
                        raise ValueError("Only one account can be a superuser.")
            except Exception as e:
                if isinstance(e, ValueError):
                    raise
        return value
