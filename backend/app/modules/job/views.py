from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import CurrentUser, SessionDep
from app.core.enums import SeniorityLevel, WorkingModel
from app.modules.job.schemas import (
    JobDetail,
    JobRead,
    JobSearchResult,
    SemanticSearchRequest,
)
from app.modules.job.services import JobService

router = APIRouter()


def get_job_service(session: SessionDep) -> JobService:
    return JobService(session)


@router.get("/", response_model=list[JobRead])
def list_jobs_endpoint(
    _current_user: CurrentUser,  # pylint: disable=unused-argument
    title: str | None = Query(default=None, description="Filter by job title"),
    seniority: SeniorityLevel | None = Query(
        default=None, description="Filter by seniority level"
    ),
    working_model: WorkingModel | None = Query(
        default=None, description="Filter by working model"
    ),
    min_salary: Decimal | None = Query(
        default=None, description="Filter by minimum salary"
    ),
    max_salary: Decimal | None = Query(
        default=None, description="Filter by maximum salary"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    service: JobService = Depends(get_job_service),
):
    return service.list_jobs(
        title=title,
        seniority=seniority,
        working_model=working_model,
        min_salary=min_salary,
        max_salary=max_salary,
        skip=skip,
        limit=limit,
    )


@router.get("/{id}", response_model=JobDetail)
def get_job_endpoint(
    id: int,
    _current_user: CurrentUser,
    service: JobService = Depends(get_job_service),
):
    job = service.get_job(id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found",
        )
    return job


@router.post("/search/semantic", response_model=list[JobSearchResult])
async def semantic_search_endpoint(
    body: SemanticSearchRequest,
    _current_user: CurrentUser,
    service: JobService = Depends(get_job_service),
):
    return await service.semantic_search(
        query=body.query,
        seniority=body.seniority,
        working_model=body.working_model,
        min_salary=body.min_salary,
        limit=body.limit,
    )
