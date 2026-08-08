from __future__ import annotations

from pydantic import BaseModel, Field


class MarketConsultantInput(BaseModel):
    query: str = Field(description="The user's market analysis question")


class TopSkillsChartInput(BaseModel):
    limit: int = Field(
        default=15,
        ge=1,
        le=50,
        description="Number of top skills to return",
    )
    seniority_filter: str | None = Field(
        default=None,
        description="Filter by seniority level (e.g., 'Junior', 'Senior', 'Mid')",
    )


class MarketOverviewInput(BaseModel):
    seniority_filter: str | None = Field(
        default=None,
        description="Filter by seniority level (e.g., 'Junior', 'Senior')",
    )
    working_model_filter: str | None = Field(
        default=None,
        description="Filter by working model (e.g., 'Remote', 'Hybrid', 'Onsite')",
    )


class SkillChartItem(BaseModel):
    label: str = Field(description="Skill name")
    value: int = Field(description="Number of job postings requiring this skill")
    category: str = Field(description="Skill category (e.g., Language, Framework)")


class SalaryStats(BaseModel):
    currency: str
    min_salary: float
    max_salary: float
    avg_salary: float
    job_count: int


class DomainCount(BaseModel):
    domain: str
    count: int


class CompanyCount(BaseModel):
    company: str
    count: int


class SeniorityCount(BaseModel):
    seniority: str
    count: int


class WorkingModelCount(BaseModel):
    working_model: str
    count: int


class MarketOverviewResult(BaseModel):
    total_jobs: int
    by_seniority: list[SeniorityCount]
    by_working_model: list[WorkingModelCount]
    salary_stats: list[SalaryStats]
    top_domains: list[DomainCount]
    top_companies: list[CompanyCount]
