"""Pydantic schemas for market analysis agent tools."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Tool Input Schemas ──────────────────────────────────────────


class MarketConsultantInput(BaseModel):
    """Input for the RAG-based market consultant tool."""

    query: str = Field(description="The user's market analysis question")


class TopSkillsChartInput(BaseModel):
    """Input for the top skills chart data tool."""

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
    """Input for the market overview statistics tool."""

    seniority_filter: str | None = Field(
        default=None,
        description="Filter by seniority level (e.g., 'Junior', 'Senior')",
    )
    working_model_filter: str | None = Field(
        default=None,
        description="Filter by working model (e.g., 'Remote', 'Hybrid', 'Onsite')",
    )


# ── Tool Output Schemas ─────────────────────────────────────────


class SkillChartItem(BaseModel):
    """A single skill data point for chart rendering."""

    label: str = Field(description="Skill name")
    value: int = Field(description="Number of job postings requiring this skill")
    category: str = Field(description="Skill category (e.g., Language, Framework)")


class SalaryStats(BaseModel):
    """Salary statistics for a currency."""

    currency: str
    min_salary: float
    max_salary: float
    avg_salary: float
    job_count: int


class DomainCount(BaseModel):
    """Domain frequency data."""

    domain: str
    count: int


class CompanyCount(BaseModel):
    """Company hiring frequency data."""

    company: str
    count: int


class SeniorityCount(BaseModel):
    """Seniority level distribution."""

    seniority: str
    count: int


class WorkingModelCount(BaseModel):
    """Working model distribution."""

    working_model: str
    count: int


class MarketOverviewResult(BaseModel):
    """Comprehensive market statistics."""

    total_jobs: int
    by_seniority: list[SeniorityCount]
    by_working_model: list[WorkingModelCount]
    salary_stats: list[SalaryStats]
    top_domains: list[DomainCount]
    top_companies: list[CompanyCount]
