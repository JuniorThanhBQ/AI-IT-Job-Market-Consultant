from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import CurrentUser, SessionDep
from app.core.enums import CompanyType
from app.modules.company.schemas import CompanyDetail, CompanyRead
from app.modules.company.services import CompanyService

router = APIRouter()


def get_company_service(session: SessionDep) -> CompanyService:
    """Dependency injector for CompanyService."""
    return CompanyService(session)


@router.get("/", response_model=list[CompanyRead])
def list_companies_endpoint(
    _current_user: CurrentUser,  # pylint: disable=unused-argument
    name: str | None = Query(default=None, description="Filter by company name"),
    industry: str | None = Query(default=None, description="Filter by industry"),
    company_type: CompanyType | None = Query(
        default=None, description="Filter by company type"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    service: CompanyService = Depends(get_company_service),
):
    """Retrieve filtered, paginated list of hiring companies."""
    return service.list_companies(
        name=name,
        industry=industry,
        company_type=company_type,
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=CompanyDetail)
def get_company_endpoint(
    id: int,
    _current_user: CurrentUser,  # pylint: disable=unused-argument
    service: CompanyService = Depends(get_company_service),
):
    """Retrieve detailed company card by database ID."""
    company = service.get_company(id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    return company
