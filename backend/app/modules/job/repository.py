from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from sqlmodel import Session, select

from app.core.enums import JobStatus, SeniorityLevel, WorkingModel
from app.modules.job.models import Job, SemanticSearchLog


def get_job_by_id(*, session: Session, job_id: int) -> Job | None:
    return session.get(Job, job_id)


def list_jobs(
    *,
    session: Session,
    title: str | None = None,
    seniority: list[SeniorityLevel] | None = None,
    working_model: list[WorkingModel] | None = None,
    min_salary: Decimal | None = None,
    max_salary: Decimal | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Job]:
    stmt = select(Job).where(Job.status == JobStatus.OPEN)

    if title:
        stmt = stmt.where(
            cast(Any, Job.title).ilike(f"%{title}%")
            | cast(Any, Job.job_description).ilike(f"%{title}%")
        )
    if seniority:
        stmt = stmt.where(cast(Any, Job.seniority).in_(seniority))
    if working_model:
        stmt = stmt.where(cast(Any, Job.working_model).in_(working_model))
    if min_salary is not None:
        stmt = stmt.where(Job.min_salary >= min_salary)
    if max_salary is not None:
        stmt = stmt.where(Job.max_salary <= max_salary)

    stmt = stmt.offset(skip).limit(limit)
    result = session.exec(stmt)
    return list(result.all())


def create_semantic_search_log(
    *,
    session: Session,
    query: str,
    results: list[dict[str, Any]],
    latency: float,
    request_meta: dict[str, Any] | None = None,
) -> SemanticSearchLog:
    log = SemanticSearchLog(
        query=query,
        results=results,
        latency=latency,
        request_meta=request_meta,
    )
    session.add(log)
    session.commit()
    return log
