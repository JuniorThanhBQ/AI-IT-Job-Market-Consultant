from datetime import date

from sqlmodel import Field, SQLModel


class ConsulteeProfileUpdate(SQLModel):
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    birthday: date | None = None
    biography: str | None = None
    goal: str | None = None


class ConsulteeProfileRead(SQLModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None
    biography: str | None = None
    goal: str | None = None
