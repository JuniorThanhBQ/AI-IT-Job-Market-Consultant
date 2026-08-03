from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.core.enums import Currency, JobStatus, SeniorityLevel, WorkingModel
from app.modules.company.schemas import CompanyRead


class SkillRead(BaseModel):
    """Schema for basic skill info."""

    id: int
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class JobRead(BaseModel):
    """Schema for basic job details."""

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
    """Schema for complete job details including company context and skills required."""

    company: CompanyRead | None = None
    skills: list[SkillRead] = []
