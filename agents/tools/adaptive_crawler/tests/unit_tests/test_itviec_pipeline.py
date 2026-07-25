import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from app.core.enums import (
    JobStatus,
    SeniorityLevel,
    WorkingModel,
    CompanyType,
    Currency,
)
from agents.tools.adaptive_crawler.crawler_adapter.itviec_adapter import adapter_itviec
from agents.tools.adaptive_crawler.crawler_repository.job_repository import (
    JobRepository,
)


def test_itviec_adapter_transformation():
    raw_data = {
        "title": "Senior Full-stack Developer (Node.js, React, .NET)",
        "url": "https://itviec.com/it-jobs/senior-full-stack-developer-1549",
        "company": {
            "name": "Restaff – House Of Norway",
            "industry": "Software Products",
            "size": "151-300 employees",
            "type": "IT Product",
            "country": "Norway",
            "slogan": "Experienced software development business",
            "working_days": "Monday - Friday",
            "overtime_policy": "Extra salary for OT",
        },
        "job_overview": {
            "location": "Da Nang",
            "work_model": "At office",
            "skills": ["ReactJS", "NodeJS", ".NET"],
            "domains": ["Software Products"],
            "salary": "$2000 - $3500",
        },
        "job_details": {
            "description": "Building next-gen enterprise applications.",
            "responsibilities": [
                "Develop frontend features using React",
                "Maintain backend Node services",
            ],
            "requirements": [
                "5+ years experience in React and Node",
                "Solid understanding of OOP",
            ],
            "nice_to_have": ["Experience with cloud providers"],
        },
        "schema_data": {
            "validThrough": "2026-12-31",
            "employmentType": "FULL_TIME",
        },
    }

    job = adapter_itviec(raw_data)

    assert job.title == "Senior Full-stack Developer (Node.js, React, .NET)"
    assert job.url == "https://itviec.com/it-jobs/senior-full-stack-developer-1549"
    assert job.seniority == SeniorityLevel.SENIOR
    assert job.working_model == WorkingModel.ONSITE
    assert job.min_salary == 2000.0
    assert job.max_salary == 3500.0
    assert job.currency == Currency.USD
    assert job.status == JobStatus.OPEN
    assert job.source == "itviec"
    assert job.content_hash is not None

    assert job.company is not None
    assert job.company.name == "Restaff – House Of Norway"
    assert job.company.company_type == CompanyType.PRODUCT
    assert job.company.country == "Norway"
    assert job.company.location == "Da Nang"

    assert len(job.skills) == 3
    skill_names = [s.name for s in job.skills]
    assert "ReactJS" in skill_names
    assert "NodeJS" in skill_names
    assert ".NET" in skill_names

    assert "Job Title: Senior Full-stack Developer" in job.vector_context
    assert "Company Name: Restaff – House Of Norway" in job.company.vector_context


@patch(
    "agents.tools.adaptive_crawler.crawler_repository.job_repository.generate_embedding_async",
    new_callable=AsyncMock,
)
def test_job_repository_save_or_update(mock_generate_embedding):
    mock_generate_embedding.return_value = [0.1] * 768

    raw_data = {
        "title": "Junior Python Developer",
        "url": "https://itviec.com/it-jobs/junior-python-dev",
        "company": {"name": "Tech Corp"},
        "job_overview": {"location": "Ho Chi Minh", "work_model": "Remote"},
        "job_details": {"description": "Write clean Python code."},
    }
    job = adapter_itviec(raw_data)

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.get_bind = MagicMock()
    mock_session.begin_nested = MagicMock(return_value=AsyncMock())
    mock_exec_result = MagicMock()
    mock_exec_result.first.return_value = None
    mock_session.exec.return_value = mock_exec_result

    async def _run():
        repo = JobRepository(mock_session)
        return await repo.save_or_update(job)

    saved_job = asyncio.run(_run())

    assert saved_job.title == "Junior Python Developer"
    assert mock_generate_embedding.called
    assert len(saved_job.embedding) == 768
    assert saved_job.embedding_model == "models/gemini-embedding-001"
