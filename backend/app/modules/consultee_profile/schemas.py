from datetime import date, datetime
from typing import Self

from pydantic import model_validator
from sqlmodel import Field, SQLModel

from app.utils.validators import SafeStr, validate_date_range


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


class CurriculumVitaeProjectCreate(SQLModel):
    name: SafeStr
    role: SafeStr
    tech_stacks: list[SafeStr] | None = None
    description: SafeStr
    start_date: date
    end_date: date
    link: SafeStr
    team_size: int = Field(default=1, ge=1)
    responsibilities: list[SafeStr] | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        validate_date_range(self.start_date, self.end_date)
        return self


class CurriculumVitaeProjectUpdate(SQLModel):
    name: SafeStr | None = None
    role: SafeStr | None = None
    tech_stacks: list[SafeStr] | None = None
    description: SafeStr | None = None
    start_date: date | None = None
    end_date: date | None = None
    link: SafeStr | None = None
    team_size: int | None = Field(default=None, ge=1)
    responsibilities: list[SafeStr] | None = None


class CurriculumVitaeProjectRead(SQLModel):
    id: int
    cv_id: int
    name: str
    role: str
    tech_stacks: list[str] | None = None
    description: str
    start_date: date
    end_date: date
    link: str
    team_size: int
    responsibilities: list[str] | None = None
    created_date: datetime | None = None
    updated_date: datetime | None = None


class CurriculumVitaeUpdate(SQLModel):
    general_information: SafeStr | None = None
    job_position: SafeStr | None = None
    summary: SafeStr | None = None
    education: SafeStr | None = None
    certifications: list[SafeStr] | None = None
    skills: list[SafeStr] | None = None
    using_cv_mode: bool | None = None
    attachment: SafeStr | None = None


class CurriculumVitaeRead(SQLModel):
    id: int
    profile_id: int
    general_information: str | None = None
    job_position: str | None = None
    summary: str | None = None
    education: str | None = None
    certifications: list[str] | None = None
    skills: list[str] | None = None
    score: int | None = 0
    structure_illogical: bool = False
    bad_text_recognition: bool = False
    exceed_page_limit: bool = False
    using_cv_mode: bool = False
    attachment: str | None = None
    created_date: datetime | None = None
    updated_date: datetime | None = None
