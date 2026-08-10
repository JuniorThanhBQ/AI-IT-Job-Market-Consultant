from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import (
    CrawlWebsite,
    Currency,
    JobStatus,
    SeniorityLevel,
    WorkingModel,
)
from app.modules.company.schemas import CompanyRead


class SkillRead(BaseModel):
    id: int
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class JobRead(BaseModel):
    id: int
    company_id: int | None = None
    title: str
    job_description: str
    expired_date: datetime
    seniority: SeniorityLevel
    min_salary: Decimal
    max_salary: Decimal
    currency: Currency
    working_hours: str
    working_model: WorkingModel
    status: JobStatus | None = None
    url: str

    model_config = ConfigDict(from_attributes=True)


class JobDetail(JobRead):
    source: CrawlWebsite | None = None
    company: CompanyRead | None = None
    skills: list[SkillRead] = []


class SemanticSearchRequest(BaseModel):
    query: str
    seniority: SeniorityLevel | None = None
    working_model: WorkingModel | None = None
    min_salary: Decimal | None = None
    limit: int = Field(default=15, ge=5, le=30)


class JobSearchResult(JobDetail):
    score: float = 0.0
