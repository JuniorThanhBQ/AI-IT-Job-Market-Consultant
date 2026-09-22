from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import CurrentUser, SessionDep
from app.core.enums import CompanyType
from app.modules.company import services as company_service
from app.modules.company.exceptions import (
    CompanyAlreadyExistsError,
    CompanyNotFoundError,
    SuperuserRequiredError,
)
from app.modules.company.schemas import (
    CompanyCreate,
    CompanyDetail,
    CompanyRead,
    CompanyUpdate,
)
from app.modules.user.schemas import MessageResponse

router = APIRouter()


@router.get("/", response_model=list[CompanyRead])
def list_companies(
    _current_user: CurrentUser,
    session: SessionDep,
    name: str | None = Query(default=None),
    industry: str | None = Query(default=None),
    company_type: CompanyType | None = Query(
        default=None, description="Filter by company type"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[CompanyRead]:
    return company_service.list_companies(
        session=session,
        name=name,
        industry=industry,
        company_type=company_type,
        skip=skip,
        limit=limit,
    )


@router.get("/{id}/", response_model=CompanyDetail)
def get_company(
    id: int,
    _current_user: CurrentUser,
    session: SessionDep,
) -> CompanyDetail:
    try:
        return company_service.get_company(session=session, company_id=id)
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post("/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: CompanyCreate,
) -> CompanyRead:
    try:
        return company_service.create_company(
            session=session, current_user=current_user, data=data
        )
    except SuperuserRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except CompanyAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.patch("/{id}/", response_model=CompanyRead)
def update_company(
    id: int,
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: CompanyUpdate,
) -> CompanyRead:
    try:
        return company_service.update_company(
            session=session, current_user=current_user, company_id=id, data=data
        )
    except SuperuserRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except CompanyAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.delete("/{id}/", response_model=MessageResponse)
def delete_company(
    id: int,
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> MessageResponse:
    try:
        return company_service.delete_company(
            session=session, current_user=current_user, company_id=id
        )
    except SuperuserRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except CompanyNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
