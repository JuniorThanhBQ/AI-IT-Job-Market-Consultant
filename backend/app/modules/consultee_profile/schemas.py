from datetime import date

from sqlmodel import Field, SQLModel


class ConsulteeProfileUpdate(SQLModel):
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    birthday: date | None = None
    biography: str | None = None
    goal: str | None = None


class CurriculumVitaeUpdate(SQLModel):
    general_information: str | None = None
    job_position: str | None = None
    summary: str | None = None
    education: str | None = None
    certifications: list[str] | None = None
    skills: list[str] | None = None


class CurriculumVitaeProjectCreate(SQLModel):
    name: str
    role: str
    tech_stacks: list[str] | None = None
    description: str
    start_date: date
    end_date: date
    link: str
    team_size: int = Field(default=1, ge=1)
    responsibilities: list[str] | None = None


class CurriculumVitaeProjectUpdate(SQLModel):
    name: str | None = None
    role: str | None = None
    tech_stacks: list[str] | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    link: str | None = None
    team_size: int | None = Field(default=None, ge=1)
    responsibilities: list[str] | None = None


class CvAttachmentUpload(SQLModel):
    filename: str


class CurriculumVitaeProjectRead(SQLModel):
    id: int
    name: str
    role: str
    tech_stacks: list[str] | None = None
    description: str
    start_date: date
    end_date: date
    link: str
    team_size: int
    responsibilities: list[str] | None = None


class CurriculumVitaeRead(SQLModel):
    id: int
    general_information: str | None = None
    job_position: str | None = None
    summary: str | None = None
    education: str | None = None
    certifications: list[str] | None = None
    skills: list[str] | None = None
    score: int | None = None
    structure_illogical: bool = False
    bad_text_recognition: bool = False
    exceed_page_limit: bool = False
    using_cv_mode: bool = False
    attachment: str | None = None
    projects: list[CurriculumVitaeProjectRead] | None = None


class ConsulteeProfileRead(SQLModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None
    biography: str | None = None
    goal: str | None = None
    cv: CurriculumVitaeRead | None = None
