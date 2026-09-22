from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from pydantic import field_validator
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from sqlmodel import Column, Field, Relationship

from app.core.enums import ConsultantMode
from app.db.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.user.models import User


class ConsultantHistory(BaseModel, table=True):
    __tablename__ = "consultant_histories"

    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    user_input: str
    input_embedding: list[float] | None = Field(
        default=None, sa_column=Column(Vector(768).with_variant(JSON(), "sqlite"))
    )
    output: str
    consultant_mode: ConsultantMode = Field(
        default=ConsultantMode.MARKET_ANALYSIS, index=True
    )
    request_log: str
    response_log: str
    token_used: float | None = Field(default=0.0)
    latency: float | None = Field(default=0.0)

    user: User = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="consultant_histories",
        )
    )

    def __str__(self) -> str:
        preview = self.user_input[:30]
        return f"{self.user_id} - {preview}"

    @field_validator("input_embedding")
    @classmethod
    def validate_embedding(cls, value):
        if value is not None and len(value) != 768:
            raise ValueError("embedding must contain exactly 768 dimensions")
        return value
