from __future__ import annotations

import time
from decimal import Decimal

from sqlmodel import Session

from app.core.enums import SeniorityLevel, WorkingModel
from app.modules.company import repository as company_repo
from app.modules.consultant import repository as consultant_repo
from app.modules.job import repository as job_repo
from app.modules.job.exceptions import (
    InvalidSalaryRangeError,
    JobNotFoundError,
    SuperuserRequiredError,
)
from app.modules.job.models import Job
from app.modules.job.schemas import (
    CompanyRead,
    JobCreate,
    JobDetail,
    JobRead,
    JobSearchResult,
    JobUpdate,
    SkillRead,
)
from app.modules.user.models import User
from app.modules.user.schemas import MessageResponse
from app.utils.embeddings import generate_embedding_async
from app.utils.vector_utils import build_job_vector_context


def get_job_or_raise(*, session: Session, job_id: int) -> Job:
    job = job_repo.get_job_by_id(session=session, job_id=job_id)
    if not job:
        raise JobNotFoundError("Job posting not found")
    return job


def get_job(*, session: Session, job_id: int) -> JobDetail:
    job = get_job_or_raise(session=session, job_id=job_id)
    return JobDetail.model_validate(job)


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
) -> list[JobRead]:
    jobs = job_repo.list_jobs(
        session=session,
        title=title,
        seniority=seniority,
        working_model=working_model,
        min_salary=min_salary,
        max_salary=max_salary,
        skip=skip,
        limit=limit,
    )
    return [JobRead.model_validate(j) for j in jobs]


async def semantic_search(
    *,
    session: Session,
    query: str,
    seniority: list[SeniorityLevel] | None = None,
    working_model: list[WorkingModel] | None = None,
    min_salary: Decimal | None = None,
    limit: int = 15,
) -> list[JobSearchResult]:
    start_time = time.time()
    embedding = await generate_embedding_async(query)
    embedding_latency = time.time() - start_time
    candidates, retrieval_latency, rrf_latency = consultant_repo.get_hybrid_candidates(
        session=session,
        user_query=query,
        user_vector=embedding,
        limit=limit * 2,
    )
    top_candidates = candidates[:limit]
    results: list[JobSearchResult] = []
    for job, company, distance in top_candidates:
        score = max(0.0, round(1.0 - float(distance), 4))
        results.append(
            JobSearchResult(
                id=job.id if job.id is not None else 0,
                company_id=job.company_id,
                company_name=company.name if company else None,
                title=job.title,
                job_description=job.job_description,
                expired_date=job.expired_date,
                seniority=job.seniority,
                min_salary=job.min_salary,
                max_salary=job.max_salary,
                currency=job.currency,
                working_hours=job.working_hours,
                working_model=job.working_model,
                status=job.status,
                url=job.url,
                source=job.source,
                company=CompanyRead.model_validate(company) if company else None,
                skills=[SkillRead.model_validate(s) for s in (job.skills or [])],
                score=score,
            )
        )

    latency = time.time() - start_time
    job_repo.create_semantic_search_log(
        session=session,
        query=query,
        results=[
            {
                "embedding_latency": embedding_latency,
                "retrieval_latency": retrieval_latency,
                "rrf_latency": rrf_latency,
            }
        ]
        + [
            {
                "job_id": job.id,
                "score": float(max(0.0, round(1.0 - float(distance), 4))),
                "distance": float(distance),
            }
            for job, company, distance in top_candidates
        ],
        latency=latency,
        request_meta={
            "limit": limit,
            "seniority": [s.value for s in seniority] if seniority else None,
            "working_model": [wm.value for wm in working_model]
            if working_model
            else None,
            "min_salary": float(min_salary) if min_salary is not None else None,
        },
    )

    results.sort(key=lambda x: x.score, reverse=True)
    return results


def create_job(*, session: Session, current_user: User, data: JobCreate) -> JobDetail:
    if not current_user.is_superuser:
        raise SuperuserRequiredError("Superuser access required.")
    if data.min_salary > data.max_salary:
        raise InvalidSalaryRangeError("min_salary cannot be greater than max_salary")

    create_dict = data.model_dump()
    skill_ids = create_dict.pop("skill_ids", None)
    company = None
    if data.company_id:
        company = company_repo.get_company_by_id(
            session=session, company_id=data.company_id
        )

    create_dict["vector_context"] = build_job_vector_context(
        title=data.title,
        company_name=company.name if company else None,
        location=company.location if company else None,
        seniority=data.seniority.value if data.seniority else None,
        min_salary=data.min_salary,
        max_salary=data.max_salary,
        currency=data.currency.value if data.currency else None,
        working_hours=data.working_hours,
        working_model=data.working_model.value if data.working_model else None,
        domains=data.domains,
        responsibilities=data.responsibilities,
        required_qualifications=data.required_qualifications,
        nice_to_have=data.nice_to_have,
        job_description=data.job_description,
    )

    job = job_repo.create_job(session=session, data=create_dict, skill_ids=skill_ids)
    return JobDetail.model_validate(job)


def update_job(
    *, session: Session, current_user: User, job_id: int, data: JobUpdate
) -> JobDetail:
    if not current_user.is_superuser:
        raise SuperuserRequiredError("Superuser access required.")

    job = get_job_or_raise(session=session, job_id=job_id)
    update_dict = data.model_dump(exclude_unset=True)
    skill_ids = update_dict.pop("skill_ids", None)
    job_min_salary = update_dict.get("min_salary", job.min_salary)
    job_max_salary = update_dict.get("max_salary", job.max_salary)
    if job_min_salary > job_max_salary:
        raise InvalidSalaryRangeError("min_salary cannot be greater than max_salary")

    company = job.company
    if "company_id" in update_dict:
        if update_dict["company_id"] is not None:
            company = company_repo.get_company_by_id(
                session=session, company_id=update_dict["company_id"]
            )
        else:
            company = None

    seniority_value = (
        update_dict["seniority"].value
        if "seniority" in update_dict and update_dict["seniority"] is not None
        else (job.seniority.value if job.seniority else None)
    )
    currency_value = (
        update_dict["currency"].value
        if "currency" in update_dict and update_dict["currency"] is not None
        else (job.currency.value if job.currency else None)
    )
    working_model_value = (
        update_dict["working_model"].value
        if "working_model" in update_dict and update_dict["working_model"] is not None
        else (job.working_model.value if job.working_model else None)
    )
    update_dict["vector_context"] = build_job_vector_context(
        title=update_dict.get("title", job.title),
        company_name=company.name if company else None,
        location=company.location if company else None,
        seniority=seniority_value,
        min_salary=job_min_salary,
        max_salary=job_max_salary,
        currency=currency_value,
        working_hours=update_dict.get("working_hours", job.working_hours),
        working_model=working_model_value,
        domains=update_dict.get("domains", job.domains),
        responsibilities=update_dict.get("responsibilities", job.responsibilities),
        required_qualifications=update_dict.get(
            "required_qualifications", job.required_qualifications
        ),
        nice_to_have=update_dict.get("nice_to_have", job.nice_to_have),
        job_description=update_dict.get("job_description", job.job_description),
    )

    updated = job_repo.update_job(
        session=session, job=job, data=update_dict, skill_ids=skill_ids
    )
    return JobDetail.model_validate(updated)


def delete_job(*, session: Session, current_user: User, job_id: int) -> MessageResponse:
    if not current_user.is_superuser:
        raise SuperuserRequiredError("Superuser access required.")

    job = get_job_or_raise(session=session, job_id=job_id)
    job_repo.delete_job(session=session, job=job)
    return MessageResponse(message="Job posting deleted successfully")
