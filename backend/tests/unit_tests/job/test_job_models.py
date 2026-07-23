from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.enums import Currency, JobStatus, SeniorityLevel, WorkingModel
from app.modules.company.models import Company
from app.modules.job.models import Job, Skills


class TestJobModels:
    def test_create_job_success(self, db_session: Session) -> None:
        job = Job(
            title="Senior Python Engineer",
            job_description="Build awesome APIs.",
            expired_date=datetime.now(UTC),
            seniority=SeniorityLevel.SENIOR,
            min_salary=3000.0,
            max_salary=5000.0,
            currency=Currency.USD,
            working_hours="9 AM - 6 PM",
            working_model=WorkingModel.REMOTE,
            status=JobStatus.OPEN,
            vector_context="Python FastAPI SQLModel",
            embedding=[0.5, 0.6, 0.7],
            source="Internal",
            url="https://jobs.example.com/python-engineer",
            responsibilities=["Write code", "Review PRs"],
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.id is not None
        assert job.title == "Senior Python Engineer"
        assert job.responsibilities == ["Write code", "Review PRs"]
        assert len(job.embedding) == 3

    def test_job_salary_check_constraint(self, db_session: Session) -> None:
        job = Job(
            title="Junior Dev",
            job_description="Learn things.",
            expired_date=datetime.now(UTC),
            seniority=SeniorityLevel.JUNIOR,
            min_salary=5000.0,
            max_salary=3000.0,
            working_hours="9 AM - 6 PM",
            vector_context="Context",
            source="Internal",
            url="https://jobs.example.com/junior-dev",
        )
        db_session.add(job)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_job_unique_url_constraint(self, db_session: Session) -> None:
        job1 = Job(
            title="Job 1",
            job_description="Desc 1",
            expired_date=datetime.now(UTC),
            seniority=SeniorityLevel.MID,
            min_salary=1000.0,
            max_salary=2000.0,
            working_hours="9-5",
            vector_context="Context 1",
            source="Source 1",
            url="https://duplicate-url.example.com",
        )
        db_session.add(job1)
        db_session.commit()

        job2 = Job(
            title="Job 2",
            job_description="Desc 2",
            expired_date=datetime.now(UTC),
            seniority=SeniorityLevel.MID,
            min_salary=1000.0,
            max_salary=2000.0,
            working_hours="9-5",
            vector_context="Context 2",
            source="Source 2",
            url="https://duplicate-url.example.com",
        )
        db_session.add(job2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_job_company_relationship(self, db_session: Session) -> None:
        company = Company(
            name="Employer Corp",
            industry="Tech",
            size="1-50",
            location="Remote",
            description="Desc",
            website="https://employer.example.com",
            vector_context="Context",
        )
        job = Job(
            title="Data Scientist",
            job_description="Analyze data.",
            expired_date=datetime.now(UTC),
            seniority=SeniorityLevel.MID,
            min_salary=2000.0,
            max_salary=4000.0,
            working_hours="9-5",
            vector_context="Context",
            source="Internal",
            url="https://jobs.example.com/data-scientist",
        )

        job.company = company
        db_session.add(company)
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert job.company_id == company.id
        assert job.company.name == "Employer Corp"

    def test_job_skills_many_to_many_relationship(self, db_session: Session) -> None:
        skill1 = Skills(name="Python", category="Programming Language")
        skill2 = Skills(name="FastAPI", category="Framework")

        job = Job(
            title="Backend Engineer",
            job_description="Build APIs.",
            expired_date=datetime.now(UTC),
            seniority=SeniorityLevel.MID,
            min_salary=2000.0,
            max_salary=4000.0,
            working_hours="9-5",
            vector_context="Context",
            source="Internal",
            url="https://jobs.example.com/backend",
        )

        job.skills.extend([skill1, skill2])
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        assert len(job.skills) == 2
        skill_names = [s.name for s in job.skills]
        assert "Python" in skill_names
        assert "FastAPI" in skill_names
