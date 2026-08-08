from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from pydantic import field_validator, model_validator
from sqlalchemy import JSON, Column, Date, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship

from app.db.base_model import BaseModel, EmbeddingModel
from app.utils.validators import name_validator, validate_birthday, validate_date_range

if TYPE_CHECKING:
    from app.modules.user.models import User


class ConsulteeEmbedding(EmbeddingModel, table=True):
    __tablename__ = "consultee_embeddings"

    profile_id: int = Field(
        foreign_key="consultee_profiles.id", unique=True, index=True, ondelete="CASCADE"
    )

    profile: ConsulteeProfile = Relationship(
        sa_relationship=relationship(
            "ConsulteeProfile",
            back_populates="embedding",
            uselist=False,
        )
    )

    __table_args__ = (
        Index(
            "idx_consultee_embeddings_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class ConsulteeProfile(BaseModel, table=True):
    __tablename__ = "consultee_profiles"

    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = Field(default=None, sa_type=Date)
    biography: str | None = None
    goal: str | None = None
    vector_context: str | None = None
    user_id: uuid.UUID = Field(
        foreign_key="user.id", unique=True, index=True, ondelete="CASCADE"
    )

    user: User = Relationship(
        sa_relationship=relationship(
            "User",
            back_populates="consultee_profile",
            uselist=False,
        )
    )
    cv: CurriculumVitae | None = Relationship(
        sa_relationship=relationship(
            "CurriculumVitae",
            back_populates="profile",
            uselist=False,
            cascade="all, delete-orphan",
            passive_deletes=True,
            lazy="joined",
        )
    )
    embedding: ConsulteeEmbedding | None = Relationship(
        sa_relationship=relationship(
            "ConsulteeEmbedding",
            back_populates="profile",
            uselist=False,
            cascade="all, delete-orphan",
            passive_deletes=True,
            lazy="select",
        )
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return name_validator(v)

    @field_validator("birthday")
    @classmethod
    def birthday_validator(cls, v: date | None) -> date | None:
        if v is None:
            return v
        return validate_birthday(v)


class CurriculumVitae(BaseModel, table=True):
    __tablename__ = "curriculum_vitaes"

    profile_id: int = Field(
        foreign_key="consultee_profiles.id", unique=True, index=True, ondelete="CASCADE"
    )
    general_information: str | None = None
    job_position: str | None = None
    summary: str | None = None
    education: str | None = None
    certifications: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    skills: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    score: int | None = Field(default=0)
    structure_illogical: bool = False
    bad_text_recognition: bool = False
    exceed_page_limit: bool = False
    using_cv_mode: bool = False
    attachment: str | None = None

    profile: ConsulteeProfile = Relationship(
        sa_relationship=relationship(
            "ConsulteeProfile",
            back_populates="cv",
            uselist=False,
        )
    )
    projects: list[CurriculumVitaeProject] = Relationship(
        sa_relationship=relationship(
            "CurriculumVitaeProject",
            back_populates="cv",
            cascade="all, delete-orphan",
            passive_deletes=True,
            lazy="selectin",
        )
    )

    @field_validator("projects", check_fields=False)
    @classmethod
    def validate_projects_limit(
        cls, v: list[CurriculumVitaeProject]
    ) -> list[CurriculumVitaeProject]:
        if len(v) > 3:
            raise ValueError("A Curriculum Vitae can have at most 3 projects.")
        return v


class CurriculumVitaeProject(BaseModel, table=True):
    __tablename__ = "curriculum_vitae_projects"

    cv_id: int = Field(
        foreign_key="curriculum_vitaes.id", index=True, ondelete="CASCADE"
    )
    name: str
    role: str
    tech_stacks: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )
    description: str
    start_date: date = Field(sa_type=Date)
    end_date: date = Field(sa_type=Date)
    link: str
    team_size: int = Field(default=1, ge=1)
    responsibilities: list[str] | None = Field(
        default=None, sa_column=Column(JSONB().with_variant(JSON(), "sqlite"))
    )

    cv: CurriculumVitae = Relationship(
        sa_relationship=relationship(
            "CurriculumVitae",
            back_populates="projects",
        )
    )

    @model_validator(mode="after")
    def validate_project_dates(self):
        validate_date_range(self.start_date, self.end_date)
        return self
