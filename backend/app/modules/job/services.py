from __future__ import annotations

from decimal import Decimal

from sqlmodel import Session

from app.core.enums import SeniorityLevel, WorkingModel
from app.modules.job import repository as job_repo
from app.modules.job.models import Job


class JobService:
    """Service layer for coordinating Job database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_job(self, job_id: int) -> Job | None:
        """Fetch a single job posting by ID."""
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
        """Fetch filtered job postings list."""
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
