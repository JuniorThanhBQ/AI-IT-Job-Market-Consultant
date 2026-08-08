from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import model_validator
from sqlalchemy import JSON, CheckConstraint, Index, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlmodel import Column, Field, Relationship, SQLModel

from app.core.enums import (
    CrawlWebsite,
    Currency,
    JobStatus,
    SeniorityLevel,
    WorkingModel,
)
from app.db.base_model import BaseModel, EmbeddingModel
from app.modules.company.models import Company
from app.utils.validators import validate_salary_range


class JobSkill(SQLModel, table=True):
    __tablename__ = "job_skills"

    job_id: int = Field(foreign_key="jobs.id", primary_key=True, ondelete="CASCADE")
    skill_id: int = Field(foreign_key="skills.id", primary_key=True, ondelete="CASCADE")

    __table_args__ = (Index("idx_job_skills_skill_id", "skill_id"),)


class Skills(SQLModel, table=True):
    __tablename__ = "skills"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    category: str

    jobs: list["Job"] = Relationship(  # noqa: UP037
        sa_relationship=relationship(
            "Job",
            back_populates="skills",
            secondary="job_skills",
            uselist=True,
            passive_deletes=True,
            lazy="select",
        )
    )


class JobEmbedding(EmbeddingModel, table=True):
    __tablename__ = "job_embeddings"

    job_id: int = Field(
        foreign_key="jobs.id", unique=True, index=True, ondelete="CASCADE"
    )

    job: Job = Relationship(
        sa_relationship=relationship(
            "Job",
            back_populates="embedding",
            uselist=False,
        )
    )

    __table_args__ = (
        Index(
            "idx_job_embeddings_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
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
    min_salary: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    max_salary: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
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
    source: CrawlWebsite = Field(index=True)
    url: str = Field(unique=True, index=True)

    __table_args__ = (
        CheckConstraint(
            "min_salary <= max_salary", name="check_min_salary_le_max_salary"
        ),
    )

    company: Company | None = Relationship(
        sa_relationship=relationship(
            "Company",
            back_populates="jobs",
            lazy="joined",
        )
    )
    skills: list[Skills] = Relationship(
        sa_relationship=relationship(
            "Skills",
            back_populates="jobs",
            secondary="job_skills",
            uselist=True,
            passive_deletes=True,
            lazy="selectin",
        )
    )
    embedding: JobEmbedding | None = Relationship(
        sa_relationship=relationship(
            "JobEmbedding",
            back_populates="job",
            uselist=False,
            cascade="all, delete-orphan",
            passive_deletes=True,
            lazy="select",
        )
    )

    @model_validator(mode="after")
    def validate_salary_range(self):
        validate_salary_range(self.min_salary, self.max_salary)
        return self
