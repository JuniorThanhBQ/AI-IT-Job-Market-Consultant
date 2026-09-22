from datetime import UTC, datetime
from typing import Any, cast

from pgvector.sqlalchemy import Vector
from pydantic import field_validator, model_validator
from sqlalchemy import JSON, DateTime
from sqlmodel import Field, SQLModel

from app.utils.validators import validate_timestamps


class BaseModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)

    created_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=cast(Any, DateTime(timezone=True)),
    )
    updated_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=cast(Any, DateTime(timezone=True)),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
    )

    @model_validator(mode="after")
    def validate_timestamps(self):
        validate_timestamps(self.created_date, self.updated_date)
        return self


class EmbeddingModel(BaseModel):
    id: int | None = Field(default=None, primary_key=True)

    embedding: list[float] | None = Field(
        default=None, sa_type=cast(Any, Vector(768).with_variant(JSON(), "sqlite"))
    )
    embedding_model: str | None = Field(default=None, index=True)
    token_used: float | None = Field(default=0.0)
    latency: float | None = Field(default=0.0)
    log: str | None = Field(default=None)

    def __str__(self) -> str:
        return self.embedding_model or f"Embedding #{self.id}"

    @field_validator("embedding_model")
    @classmethod
    def validate_embedding_model(cls, value):
        if value is not None and not value.strip():
            raise ValueError("embedding_model cannot be empty")
        return value

    @field_validator("embedding")
    @classmethod
    def validate_embedding(cls, value):
        if value is not None and len(value) != 768:
            raise ValueError("embedding must contain exactly 768 dimensions")
        return value
