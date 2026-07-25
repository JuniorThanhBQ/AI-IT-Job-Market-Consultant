from __future__ import annotations

from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlmodel import Column, Field, Relationship

from app.core.enums import CompanyType
from app.db.base_model import BaseModel

if TYPE_CHECKING:
    from app.modules.job.models import Job
else:

    class Job:
        pass


class CompanyBenefit(BaseModel, table=True):
    __tablename__ = "company_benefits"

    company_id: int = Field(foreign_key="companies.id", ondelete="CASCADE", index=True)
    name: str

    company: Company = Relationship(
        sa_relationship=relationship(
            "Company",
            back_populates="benefits",
            lazy="selectin",
        )
    )


class Company(BaseModel, table=True):
    __tablename__ = "companies"

    name: str = Field(index=True, unique=True)
    industry: str
    size: str
    location: str
    description: str
    website: str
    slogan: str | None = Field(default=None)
    company_type: CompanyType | None = Field(default=None, index=True)
    country: str | None = Field(default=None, index=True)
    addresses: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    working_days: str | None = Field(default=None)
    overtime_policy: str | None = Field(default=None)
    vector_context: str
    embedding: list[float] | None = Field(
        default=None, sa_column=Column(Vector(768).with_variant(JSON(), "sqlite"))
    )
    embedding_model: str | None = Field(default=None, index=True)
    embedding_version: int | None = Field(default=None, index=True)

    __table_args__ = (
        Index(
            "idx_companies_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    benefits: list[CompanyBenefit] = Relationship(
        sa_relationship=relationship(
            "CompanyBenefit",
            back_populates="company",
            cascade="all, delete-orphan",
            lazy="selectin",
        )
    )
    jobs: list[Job] = Relationship(
        sa_relationship=relationship(
            "Job",
            back_populates="company",
            uselist=True,
            lazy="selectin",
        )
    )
