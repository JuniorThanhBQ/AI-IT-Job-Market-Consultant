from datetime import date

from sqlmodel import Field, SQLModel

from app.utils.validators import SafeStr


class ConsulteeProfileUpdate(SQLModel):
    first_name: SafeStr | None = Field(default=None, max_length=255)
    last_name: SafeStr | None = Field(default=None, max_length=255)
    birthday: date | None = None
    biography: SafeStr | None = None
    goal: SafeStr | None = None


class ConsulteeProfileRead(SQLModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None
    biography: str | None = None
    goal: str | None = None
