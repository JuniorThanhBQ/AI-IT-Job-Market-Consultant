from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlmodel import Column, Field, Relationship, SQLModel

from app.modules.company.models import Company


class JobSkill(SQLModel, table=True):
    __tablename__ = "job_skills"

    job_id: int = Field(foreign_key="jobs.id", primary_key=True)
    skill_id: int = Field(foreign_key="skills.id", primary_key=True)


class Skills(SQLModel, table=True):
    __tablename__ = "skills"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    category: str

    jobs: list[Job] = Relationship(
        sa_relationship=relationship(
            "Job",
            back_populates="skills",
            secondary="job_skills",
            uselist=True,
        )
    )


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: int | None = Field(default=None, primary_key=True)
    company_id: int | None = Field(default=None, foreign_key="companies.id")
    title: str = Field(index=True)
    job_description: str
    created_date: datetime = Field(default_factory=datetime.utcnow)
    expired_date: datetime
    updated_date: datetime = Field(default_factory=datetime.utcnow)
    seniority: str
    min_salary: float
    max_salary: float
    currency: str
    working_hours: str
    working_model: str
    status: str | None = Field(default="Open", index=True)
    content_hash: str | None = Field(default=None, unique=True, index=True)
    responsibilities: list[str] | None = Field(default=None, sa_column=Column(JSONB))
    required_qualifications: list[str] | None = Field(
        default=None, sa_column=Column(JSONB)
    )
    nice_to_have: list[str] | None = Field(default=None, sa_column=Column(JSONB))
    domains: list[str] | None = Field(default=None, sa_column=Column(JSONB))
    vector_context: str
    embedding: list[float] | None = Field(default=None, sa_column=Column(Vector(768)))
    source: str
    url: str = Field(unique=True, index=True)

    company: Company | None = Relationship(
        sa_relationship=relationship(
            "Company",
            back_populates="jobs",
        )
    )
    skills: list[Skills] = Relationship(
        sa_relationship=relationship(
            "Skills",
            back_populates="jobs",
            secondary="job_skills",
            uselist=True,
        )
    )


Skills.model_rebuild()
Job.model_rebuild()
