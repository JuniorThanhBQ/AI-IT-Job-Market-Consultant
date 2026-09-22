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
from app.utils.validators import SafeStr


class SkillRead(BaseModel):
    id: int
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class JobCreate(BaseModel):
    company_id: int | None = None
    title: SafeStr = Field(max_length=255)
    job_description: SafeStr
    expired_date: datetime
    seniority: SeniorityLevel
    min_salary: Decimal = Field(ge=0)
    max_salary: Decimal = Field(ge=0)
    currency: Currency = Field(default=Currency.VND)
    working_hours: SafeStr = Field(max_length=255)
    working_model: WorkingModel = Field(default=WorkingModel.ONSITE)
    status: JobStatus = Field(default=JobStatus.OPEN)
    source: CrawlWebsite = Field(default=CrawlWebsite.ITVIEC)
    url: SafeStr
    responsibilities: list[SafeStr] | None = None
    required_qualifications: list[SafeStr] | None = None
    nice_to_have: list[SafeStr] | None = None
    domains: list[SafeStr] | None = None
    skill_ids: list[int] | None = None


class JobUpdate(BaseModel):
    company_id: int | None = None
    title: SafeStr | None = Field(default=None, max_length=255)
    job_description: SafeStr | None = None
    expired_date: datetime | None = None
    seniority: SeniorityLevel | None = None
    min_salary: Decimal | None = Field(default=None, ge=0)
    max_salary: Decimal | None = Field(default=None, ge=0)
    currency: Currency | None = None
    working_hours: SafeStr | None = Field(default=None, max_length=255)
    working_model: WorkingModel | None = None
    status: JobStatus | None = None
    source: CrawlWebsite | None = None
    url: SafeStr | None = None
    responsibilities: list[SafeStr] | None = None
    required_qualifications: list[SafeStr] | None = None
    nice_to_have: list[SafeStr] | None = None
    domains: list[SafeStr] | None = None
    skill_ids: list[int] | None = None


class JobRead(BaseModel):
    id: int
    company_id: int | None = None
    company_name: str | None = None
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
    source: CrawlWebsite | None = None
    url: str

    model_config = ConfigDict(from_attributes=True)


class JobDetail(JobRead):
    source: CrawlWebsite | None = None
    company: CompanyRead | None = None
    skills: list[SkillRead] = []
    responsibilities: list[str] | None = None
    required_qualifications: list[str] | None = None
    nice_to_have: list[str] | None = None
    domains: list[str] | None = None


class SemanticSearchRequest(BaseModel):
    query: SafeStr
    seniority: list[SeniorityLevel] | None = None
    working_model: list[WorkingModel] | None = None
    min_salary: Decimal | None = None
    limit: int = Field(default=15, ge=5, le=30)


class JobSearchResult(JobDetail):
    score: float = 0.0
