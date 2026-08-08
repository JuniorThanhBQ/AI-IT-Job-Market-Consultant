from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import CompanyType, CountryEnum

if TYPE_CHECKING:
    from app.modules.job.schemas import JobRead


class CompanyRead(BaseModel):
    id: int
    name: str
    industry: str
    size: str
    location: str
    description: str
    website: str | None = None
    slogan: str | None = None
    company_type: CompanyType | None = None
    country: CountryEnum | None = None
    addresses: list[str] | None = None
    benefits: list[str] | None = None
    working_days: str | None = None
    overtime_policy: str | None = None
    vector_context: str

    model_config = ConfigDict(from_attributes=True)


class CompanyDetail(CompanyRead):
    jobs: list[JobRead] = Field(default_factory=list)


class CompanyQueryParams(BaseModel):
    name: str | None = None
    industry: str | None = None
    company_type: CompanyType | None = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


from app.modules.job.schemas import JobRead  # noqa: E402  # pylint: disable=reimported

CompanyDetail.model_rebuild()
