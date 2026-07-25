from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


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
