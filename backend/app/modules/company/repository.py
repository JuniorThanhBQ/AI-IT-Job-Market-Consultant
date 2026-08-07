from __future__ import annotations

from typing import Any, cast

from sqlmodel import Session, select

from app.core.enums import CompanyType
from app.modules.company.models import Company


def get_company_by_id(*, session: Session, company_id: int) -> Company | None:
    return session.get(Company, company_id)


def list_companies(
    *,
    session: Session,
    name: str | None = None,
    industry: str | None = None,
    company_type: CompanyType | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Company]:
    stmt = select(Company)

    if name:
        stmt = stmt.where(cast(Any, Company.name).ilike(f"%{name}%"))
    if industry:
        stmt = stmt.where(cast(Any, Company.industry).ilike(f"%{industry}%"))
    if company_type:
        stmt = stmt.where(Company.company_type == company_type)

    stmt = stmt.offset(skip).limit(limit)
    result = session.exec(stmt)
    return list(result.all())
