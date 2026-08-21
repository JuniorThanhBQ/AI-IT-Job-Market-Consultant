from __future__ import annotations

import time
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
        seniority: list[SeniorityLevel] | None = None,
        working_model: list[WorkingModel] | None = None,
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
        seniority: list[SeniorityLevel] | None = None,
        working_model: list[WorkingModel] | None = None,
        min_salary: Decimal | None = None,
        limit: int = 10,
    ) -> list[JobSearchResult]:
        start_time = time.time()
        embedding = await generate_embedding_async(query)
        embedding_latency = time.time() - start_time
        candidates, retrieval_latency, rrf_latency = (
            consultant_repo.get_hybrid_candidates(
                session=self.db,
                user_query=query,
                user_vector=embedding,
                limit=limit * 2,
            )
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
            session=self.db,
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
