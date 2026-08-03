from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from sqlmodel import Session, select

from app.core.enums import JobStatus, SeniorityLevel, WorkingModel
from app.modules.job.models import Job


def get_job_by_id(*, session: Session, job_id: int) -> Job | None:
    """Retrieve a single job with all pre-loaded associations by its ID."""
    return session.get(Job, job_id)


def list_jobs(
    *,
    session: Session,
    title: str | None = None,
    seniority: SeniorityLevel | None = None,
    working_model: WorkingModel | None = None,
    min_salary: Decimal | None = None,
    max_salary: Decimal | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Job]:
    """Retrieve a filtered, paginated list of open/active job postings."""
    # Only fetch jobs that are open or draft (not closed/expired) by default
    stmt = select(Job).where(Job.status == JobStatus.OPEN)

    if title:
        stmt = stmt.where(cast(Any, Job.title).ilike(f"%{title}%"))
    if seniority:
        stmt = stmt.where(Job.seniority == seniority)
    if working_model:
        stmt = stmt.where(Job.working_model == working_model)
    if min_salary is not None:
        stmt = stmt.where(Job.min_salary >= min_salary)
    if max_salary is not None:
        stmt = stmt.where(Job.max_salary <= max_salary)

    stmt = stmt.offset(skip).limit(limit)
    result = session.exec(stmt)
    return list(result.all())
