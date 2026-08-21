from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlmodel import Column, Field, Relationship

from app.core.enums import CompanyType, CountryEnum
from app.db.base_model import BaseModel, EmbeddingModel

if TYPE_CHECKING:
    from app.modules.job.models import Job


class CompanyEmbedding(EmbeddingModel, table=True):
    __tablename__ = "company_embeddings"

    company_id: int = Field(
        foreign_key="companies.id", unique=True, index=True, ondelete="CASCADE"
    )

    company: Company = Relationship(
        sa_relationship=relationship(
            "Company",
            back_populates="embedding",
            uselist=False,
        )
    )

    __table_args__ = (
        Index(
            "idx_company_embeddings_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class Company(BaseModel, table=True):
    __tablename__ = "companies"

    name: str = Field(index=True, unique=True)
    industry: str
    size: str
    location: str
    description: str
    website: str | None = None
    slogan: str | None = Field(default=None)
    company_type: CompanyType | None = Field(default=CompanyType.PRODUCT, index=True)
    country: CountryEnum | None = Field(default=CountryEnum.VIETNAM, index=True)
    addresses: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    benefits: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    working_days: str | None = Field(default=None)
    overtime_policy: str | None = Field(default=None)
    vector_context: str

    __table_args__ = ()

    jobs: list[Job] = Relationship(
        sa_relationship=relationship(
            "Job",
            back_populates="company",
            uselist=True,
            passive_deletes=True,
            lazy="select",
        )
    )
    embedding: CompanyEmbedding | None = Relationship(
        sa_relationship=relationship(
            "CompanyEmbedding",
            back_populates="company",
            uselist=False,
            cascade="all, delete-orphan",
            passive_deletes=True,
            lazy="select",
        )
    )
