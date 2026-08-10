from __future__ import annotations

from decimal import Decimal

from sqlmodel import Session

from app.core.enums import SeniorityLevel, WorkingModel
from app.modules.consultant import repository as consultant_repo
from app.modules.job import repository as job_repo
from app.modules.job.models import Job
from app.modules.job.schemas import CompanyRead, JobSearchResult, SkillRead
from app.utils.embeddings import generate_embedding_async


class JobService:
    def __init__(self, db: Session):
        self.db = db

    def get_job(self, job_id: int) -> Job | None:
        return job_repo.get_job_by_id(session=self.db, job_id=job_id)

    def list_jobs(
        self,
        title: str | None = None,
        seniority: SeniorityLevel | None = None,
        working_model: WorkingModel | None = None,
        min_salary: Decimal | None = None,
        max_salary: Decimal | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Job]:
        return job_repo.list_jobs(
            session=self.db,
            title=title,
            seniority=seniority,
            working_model=working_model,
            min_salary=min_salary,
            max_salary=max_salary,
            skip=skip,
            limit=limit,
        )

    async def semantic_search(
        self,
        query: str,
        seniority: SeniorityLevel | None = None,
        working_model: WorkingModel | None = None,
        min_salary: Decimal | None = None,
        limit: int = 15,
    ) -> list[JobSearchResult]:
        embedding = await generate_embedding_async(query)

        candidates = consultant_repo.get_hybrid_candidates(
            session=self.db,
            user_query=query,
            user_vector=embedding,
            limit=limit * 2,
        )

        filtered = [
            (job, company, dist)
            for job, company, dist in candidates
            if (not seniority or job.seniority == seniority)
            and (not working_model or job.working_model == working_model)
            and (min_salary is None or job.min_salary >= min_salary)
        ]

        reranked = filtered[:limit]

        results: list[JobSearchResult] = []
        for job, company, distance in reranked:
            score = max(0.0, round(1.0 - float(distance), 4))
            results.append(
                JobSearchResult(
                    id=job.id if job.id is not None else 0,
                    company_id=job.company_id,
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

        return results
