from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import CompanyType, CountryEnum
from app.utils.validators import SafeStr

if TYPE_CHECKING:
    from app.modules.job.schemas import JobRead


class CompanyCreate(BaseModel):
    name: SafeStr = Field(max_length=255)
    industry: SafeStr = Field(max_length=255)
    size: SafeStr = Field(max_length=255)
    location: SafeStr = Field(max_length=255)
    description: SafeStr
    website: SafeStr | None = Field(default=None, max_length=255)
    slogan: SafeStr | None = Field(default=None, max_length=255)
    company_type: CompanyType | None = Field(default=CompanyType.PRODUCT)
    country: CountryEnum | None = Field(default=CountryEnum.VIETNAM)
    addresses: list[SafeStr] | None = None
    benefits: list[SafeStr] | None = None
    working_days: SafeStr | None = Field(default=None, max_length=255)
    overtime_policy: SafeStr | None = Field(default=None, max_length=255)


class CompanyUpdate(BaseModel):
    name: SafeStr | None = Field(default=None, max_length=255)
    industry: SafeStr | None = Field(default=None, max_length=255)
    size: SafeStr | None = Field(default=None, max_length=255)
    location: SafeStr | None = Field(default=None, max_length=255)
    description: SafeStr | None = None
    website: SafeStr | None = Field(default=None, max_length=255)
    slogan: SafeStr | None = Field(default=None, max_length=255)
    company_type: CompanyType | None = None
    country: CountryEnum | None = None
    addresses: list[SafeStr] | None = None
    benefits: list[SafeStr] | None = None
    working_days: SafeStr | None = Field(default=None, max_length=255)
    overtime_policy: SafeStr | None = Field(default=None, max_length=255)


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
    name: SafeStr | None = None
    industry: SafeStr | None = None
    company_type: CompanyType | None = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
