from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlmodel import Column, Field, Relationship, SQLModel

from app.core.enums import Currency, JobStatus, SeniorityLevel, WorkingModel
from app.db.base_model import BaseModel
from app.modules.company.models import Company


class JobSkill(SQLModel, table=True):
    __tablename__ = "job_skills"

    job_id: int = Field(foreign_key="jobs.id", primary_key=True, ondelete="CASCADE")
    skill_id: int = Field(foreign_key="skills.id", primary_key=True, ondelete="CASCADE")


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
            lazy="selectin",
        )
    )


class Job(BaseModel, table=True):
    __tablename__ = "jobs"

    company_id: int | None = Field(
        default=None, foreign_key="companies.id", ondelete="CASCADE", index=True
    )
    title: str = Field(index=True)
    job_description: str
    expired_date: datetime
    seniority: SeniorityLevel = Field(index=True)
    min_salary: float
    max_salary: float
    currency: Currency = Field(default=Currency.VND, index=True)
    working_hours: str
    working_model: WorkingModel = Field(default=WorkingModel.ONSITE, index=True)
    status: JobStatus | None = Field(default=JobStatus.OPEN, index=True)
    content_hash: str | None = Field(default=None, unique=True, index=True)
    responsibilities: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    required_qualifications: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    nice_to_have: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    domains: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    vector_context: str
    embedding: list[float] | None = Field(
        default=None, sa_column=Column(Vector(768).with_variant(JSON(), "sqlite"))
    )
    embedding_model: str | None = Field(default=None, index=True)
    embedding_version: int | None = Field(default=None, index=True)
    source: str
    url: str = Field(unique=True, index=True)

    __table_args__ = (
        CheckConstraint(
            "min_salary <= max_salary", name="check_min_salary_le_max_salary"
        ),
        Index(
            "idx_jobs_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    company: Company | None = Relationship(
        sa_relationship=relationship(
            "Company",
            back_populates="jobs",
            lazy="selectin",
        )
    )
    skills: list[Skills] = Relationship(
        sa_relationship=relationship(
            "Skills",
            back_populates="jobs",
            secondary="job_skills",
            uselist=True,
            lazy="selectin",
        )
    )
