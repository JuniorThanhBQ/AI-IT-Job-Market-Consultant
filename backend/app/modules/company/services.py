from __future__ import annotations

from sqlmodel import Session

from app.core.enums import CompanyType
from app.modules.company import repository as company_repo
from app.modules.company.exceptions import (
    CompanyAlreadyExistsError,
    CompanyNotFoundError,
    SuperuserRequiredError,
)
from app.modules.company.models import Company
from app.modules.company.schemas import (
    CompanyCreate,
    CompanyDetail,
    CompanyRead,
    CompanyUpdate,
)
from app.modules.user.models import User
from app.modules.user.schemas import MessageResponse
from app.utils.vector_utils import build_company_vector_context


def get_company_or_raise(*, session: Session, company_id: int) -> Company:
    company = company_repo.get_company_by_id(session=session, company_id=company_id)
    if not company:
        raise CompanyNotFoundError("Company not found")
    return company


def get_company(*, session: Session, company_id: int) -> CompanyDetail:
    company = get_company_or_raise(session=session, company_id=company_id)
    return CompanyDetail.model_validate(company)


def list_companies(
    *,
    session: Session,
    name: str | None = None,
    industry: str | None = None,
    company_type: CompanyType | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[CompanyRead]:
    companies = company_repo.list_companies(
        session=session,
        name=name,
        industry=industry,
        company_type=company_type,
        skip=skip,
        limit=limit,
    )
    return [CompanyRead.model_validate(c) for c in companies]


def create_company(
    *, session: Session, current_user: User, data: CompanyCreate
) -> CompanyRead:
    if not current_user.is_superuser:
        raise SuperuserRequiredError("Superuser access required.")

    existing = company_repo.get_company_by_name(session=session, name=data.name)
    if existing:
        raise CompanyAlreadyExistsError("Company with this name already exists.")

    create_dict = data.model_dump()
    create_dict["vector_context"] = build_company_vector_context(
        name=data.name,
        slogan=data.slogan,
        company_type=data.company_type.value if data.company_type else None,
        industry=data.industry,
        size=data.size,
        country=data.country.value if data.country else None,
        location=data.location,
        description=data.description,
        working_days=data.working_days,
        overtime_policy=data.overtime_policy,
    )
    company = company_repo.create_company(session=session, data=create_dict)
    return CompanyRead.model_validate(company)


def update_company(
    *,
    session: Session,
    current_user: User,
    company_id: int,
    data: CompanyUpdate,
) -> CompanyRead:
    if not current_user.is_superuser:
        raise SuperuserRequiredError("Superuser access required.")

    company = get_company_or_raise(session=session, company_id=company_id)
    update_dict = data.model_dump(exclude_unset=True)
    if "name" in update_dict and update_dict["name"] != company.name:
        existing = company_repo.get_company_by_name(
            session=session, name=update_dict["name"]
        )
        if existing and existing.id != company.id:
            raise CompanyAlreadyExistsError("Company with this name already exists.")

    company_type_value = (
        update_dict["company_type"].value
        if "company_type" in update_dict and update_dict["company_type"] is not None
        else (company.company_type.value if company.company_type else None)
    )
    country_value = (
        update_dict["country"].value
        if "country" in update_dict and update_dict["country"] is not None
        else (company.country.value if company.country else None)
    )
    update_dict["vector_context"] = build_company_vector_context(
        name=update_dict.get("name", company.name),
        slogan=update_dict.get("slogan", company.slogan),
        company_type=company_type_value,
        industry=update_dict.get("industry", company.industry),
        size=update_dict.get("size", company.size),
        country=country_value,
        location=update_dict.get("location", company.location),
        description=update_dict.get("description", company.description),
        working_days=update_dict.get("working_days", company.working_days),
        overtime_policy=update_dict.get("overtime_policy", company.overtime_policy),
    )
    updated = company_repo.update_company(
        session=session, company=company, data=update_dict
    )
    return CompanyRead.model_validate(updated)


def delete_company(
    *, session: Session, current_user: User, company_id: int
) -> MessageResponse:
    if not current_user.is_superuser:
        raise SuperuserRequiredError("Superuser access required.")

    company = get_company_or_raise(session=session, company_id=company_id)
    company_repo.delete_company(session=session, company=company)
    return MessageResponse(message="Company deleted successfully")
