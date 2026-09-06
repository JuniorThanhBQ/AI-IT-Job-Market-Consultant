from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import CurrentUser, SessionDep
from app.modules.job import services as job_service
from app.modules.job.exceptions import (
    InvalidSalaryRangeError,
    JobNotFoundError,
    SuperuserRequiredError,
)
from app.modules.job.schemas import (
    JobCreate,
    JobDetail,
    JobRead,
    JobSearchResult,
    JobUpdate,
    SemanticSearchRequest,
)
from app.modules.user.schemas import MessageResponse
from app.utils.job_utils import parse_seniority_levels, parse_working_models

router = APIRouter()


@router.get("/", response_model=list[JobRead])
def list_jobs(
    _current_user: CurrentUser,
    session: SessionDep,
    title: str | None = Query(default=None, description="Filter by job title"),
    seniority: list[str] | None = Query(
        default=None, description="Filter by seniority levels"
    ),
    working_model: list[str] | None = Query(
        default=None, description="Filter by working models"
    ),
    min_salary: Decimal | None = Query(
        default=None, description="Filter by minimum salary"
    ),
    max_salary: Decimal | None = Query(
        default=None, description="Filter by maximum salary"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[JobRead]:
    parsed_seniority = parse_seniority_levels(seniority)
    parsed_working_model = parse_working_models(working_model)
    return job_service.list_jobs(
        session=session,
        title=title,
        seniority=parsed_seniority,
        working_model=parsed_working_model,
        min_salary=min_salary,
        max_salary=max_salary,
        skip=skip,
        limit=limit,
    )


@router.get("/{id}/", response_model=JobDetail)
def get_job(
    id: int,
    _current_user: CurrentUser,
    session: SessionDep,
) -> JobDetail:
    try:
        return job_service.get_job(session=session, job_id=id)
    except JobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post("/hybrid/", response_model=list[JobSearchResult])
async def job_hybrid_search(
    body: SemanticSearchRequest,
    _current_user: CurrentUser,
    session: SessionDep,
) -> list[JobSearchResult]:
    return await job_service.semantic_search(
        session=session,
        query=body.query,
        seniority=body.seniority,
        working_model=body.working_model,
        min_salary=body.min_salary,
        limit=body.limit,
    )


@router.post("/", response_model=JobDetail, status_code=status.HTTP_201_CREATED)
def create_job(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: JobCreate,
) -> JobDetail:
    try:
        return job_service.create_job(
            session=session, current_user=current_user, data=data
        )
    except SuperuserRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except InvalidSalaryRangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.patch("/{id}/", response_model=JobDetail)
def update_job(
    id: int,
    *,
    session: SessionDep,
    current_user: CurrentUser,
    data: JobUpdate,
) -> JobDetail:
    try:
        return job_service.update_job(
            session=session, current_user=current_user, job_id=id, data=data
        )
    except SuperuserRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except JobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except InvalidSalaryRangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc


@router.delete("/{id}/", response_model=MessageResponse)
def delete_job(
    id: int,
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> MessageResponse:
    try:
        return job_service.delete_job(
            session=session, current_user=current_user, job_id=id
        )
    except SuperuserRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except JobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
