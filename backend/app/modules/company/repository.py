from __future__ import annotations

from typing import Any, cast

from sqlmodel import Session, select

from app.core.enums import CompanyType
from app.modules.company.models import Company


def get_company_by_id(*, session: Session, company_id: int) -> Company | None:
    return session.get(Company, company_id)


def get_company_by_name(*, session: Session, name: str) -> Company | None:
    statement = select(Company).where(Company.name == name)
    return session.exec(statement).first()


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


def create_company(*, session: Session, data: dict[str, Any]) -> Company:
    company = Company(**data)
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


def update_company(
    *, session: Session, company: Company, data: dict[str, Any]
) -> Company:
    company.sqlmodel_update(data)
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


def delete_company(*, session: Session, company: Company) -> None:
    session.delete(company)
    session.commit()
