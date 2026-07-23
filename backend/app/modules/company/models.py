from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlmodel import Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.job.models import Job


class CompanyBenefit(SQLModel, table=True):
    __tablename__ = "company_benefits"

    id: int | None = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id")
    name: str
    created_date: datetime = Field(default_factory=datetime.utcnow)
    updated_date: datetime = Field(default_factory=datetime.utcnow)

    company: Company = Relationship(
        sa_relationship=relationship(
            "Company",
            back_populates="benefits",
        )
    )


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    industry: str
    size: str
    location: str
    description: str
    website: str
    slogan: str | None = Field(default=None)
    company_type: str | None = Field(default=None, index=True)
    country: str | None = Field(default=None, index=True)
    addresses: list[str] | None = Field(default=None, sa_column=Column(JSONB))
    working_days: str | None = Field(default=None)
    overtime_policy: str | None = Field(default=None)
    created_date: datetime = Field(default_factory=datetime.utcnow)
    updated_date: datetime = Field(default_factory=datetime.utcnow)
    vector_context: str
    embedding: list[float] | None = Field(default=None, sa_column=Column(Vector(768)))

    benefits: list[CompanyBenefit] = Relationship(
        sa_relationship=relationship(
            "CompanyBenefit",
            back_populates="company",
            cascade="all, delete-orphan",
        )
    )
    jobs: list[Job] = Relationship(
        sa_relationship=relationship(
            "Job",
            back_populates="company",
        )
    )


CompanyBenefit.model_rebuild()
Company.model_rebuild()
