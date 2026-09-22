from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from sqlmodel import Session, select

from app.core.enums import JobStatus, SeniorityLevel, WorkingModel
from app.modules.job.models import Job, SemanticSearchLog, Skills


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


def create_job(
    *, session: Session, data: dict[str, Any], skill_ids: list[int] | None = None
) -> Job:
    job = Job(**data)
    if skill_ids:
        skills = session.exec(
            select(Skills).where(cast(Any, Skills.id).in_(skill_ids))
        ).all()
        job.skills = list(skills)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def update_job(
    *,
    session: Session,
    job: Job,
    data: dict[str, Any],
    skill_ids: list[int] | None = None,
) -> Job:
    job.sqlmodel_update(data)
    if skill_ids is not None:
        skills = session.exec(
            select(Skills).where(cast(Any, Skills.id).in_(skill_ids))
        ).all()
        job.skills = list(skills)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def delete_job(*, session: Session, job: Job) -> None:
    session.delete(job)
    session.commit()


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
