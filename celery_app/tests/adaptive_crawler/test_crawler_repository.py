from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.core.enums import CrawlWebsite, JobStatus
from app.modules.company.models import Company
from app.modules.job.models import Job
from tools.adaptive_crawler.crawler_repository.company_repository import (
    CompanyRepository,
)
from tools.adaptive_crawler.crawler_repository.job_repository import JobRepository


class FakeResult:
    def __init__(self, value):
        self._value = value

    def first(self):
        return self._value

    def all(self):
        if isinstance(self._value, list):
            return self._value
        return [self._value] if self._value is not None else []


@pytest.mark.asyncio
class TestCompanyRepositoryBehavior:
    @pytest.mark.parametrize("name_val", ["", "   ", None])
    async def test_returns_none_for_blank_name(self, name_val):
        session = AsyncMock()
        repo = CompanyRepository(session)

        company = await repo.get_by_name(name_val)

        assert company is None
        session.exec.assert_not_called()

    async def test_normalizes_name_and_returns_first_match(self):
        session = AsyncMock()
        expected_company = MagicMock(spec=Company)
        session.exec.return_value = FakeResult(expected_company)
        repo = CompanyRepository(session)

        company = await repo.get_by_name("  Acme Labs  ")

        assert company is expected_company
        session.exec.assert_awaited_once()

    async def test_returns_none_when_session_has_no_match(self):
        session = AsyncMock()
        session.exec.return_value = FakeResult(None)
        repo = CompanyRepository(session)

        company = await repo.get_by_name("Acme Labs")

        assert company is None

    async def test_save_or_update_missing_name_raises(self):
        session = AsyncMock()
        repo = CompanyRepository(session)
        company = MagicMock(spec=Company)
        company.name = None

        with pytest.raises(ValueError) as exc:
            await repo.save_or_update(company)
        assert "Company name is required" in str(exc.value)

    @patch(
        "tools.adaptive_crawler.crawler_repository.company_repository.generate_embedding_async",
        new_callable=AsyncMock,
    )
    async def test_save_or_update_existing_company(self, mock_emb):
        session = AsyncMock()
        repo = CompanyRepository(session)

        existing = Company(
            name="Acme Corp",
            addresses=["123 Old St"],
            benefits=["Insurance"],
        )
        repo.get_by_name = AsyncMock(return_value=existing)

        incoming = Company(
            name="Acme Corp",
            addresses=["456 New St"],
            benefits=["Gym"],
            description="Leading tech firm",
            vector_context="Acme tech context",
        )

        mock_emb.return_value = MagicMock(token_used=1.0, latency=0.1, log=None)

        result = await repo.save_or_update(incoming, generate_embedding=True)

        assert result is existing
        assert "123 old st" in [a.lower() for a in existing.addresses]
        assert "456 new st" in [a.lower() for a in existing.addresses]
        assert "insurance" in [b.lower() for b in existing.benefits]
        assert "gym" in [b.lower() for b in existing.benefits]
        session.add.assert_called_with(existing)
        session.flush.assert_awaited_once()

    async def test_save_or_update_new_company(self):
        session = AsyncMock()
        session.begin_nested = MagicMock()
        session.begin_nested.return_value.__aenter__.return_value = AsyncMock()
        session.begin_nested.return_value.__aexit__.return_value = AsyncMock()

        repo = CompanyRepository(session)
        repo.get_by_name = AsyncMock(return_value=None)

        incoming = Company(name="New Startup", vector_context="")

        result = await repo.save_or_update(incoming, generate_embedding=False)

        assert result is incoming
        session.add.assert_called_with(incoming)
        session.flush.assert_awaited_once()


@pytest.mark.asyncio
class TestJobRepositoryBehavior:
    @pytest.mark.parametrize("value", ["", "   ", None])
    async def test_returns_none_for_blank_url(self, value):
        session = AsyncMock()
        repo = JobRepository(session)

        job = await repo.get_by_url(value)

        assert job is None
        session.exec.assert_not_called()

    async def test_trims_url_and_returns_first_match(self):
        session = AsyncMock()
        expected_job = MagicMock(spec=Job)
        session.exec.return_value = FakeResult(expected_job)
        repo = JobRepository(session)

        job = await repo.get_by_url("  https://jobs.example/123  ")

        assert job is expected_job
        session.exec.assert_awaited_once()

    async def test_returns_none_when_session_has_no_match(self):
        session = AsyncMock()
        session.exec.return_value = FakeResult(None)
        repo = JobRepository(session)

        job = await repo.get_by_url("https://jobs.example/123")

        assert job is None

    @pytest.mark.parametrize("hash_val", ["", "   ", None])
    async def test_returns_none_for_blank_content_hash(self, hash_val):
        session = AsyncMock()
        repo = JobRepository(session)

        job = await repo.get_by_content_hash(hash_val)

        assert job is None
        session.exec.assert_not_called()

    async def test_get_by_content_hash_returns_match(self):
        session = AsyncMock()
        expected_job = MagicMock(spec=Job)
        session.exec.return_value = FakeResult(expected_job)
        repo = JobRepository(session)

        job = await repo.get_by_content_hash("hash123")

        assert job is expected_job
        session.exec.assert_awaited_once()

    async def test_get_open_jobs_batch(self):
        session = AsyncMock()
        jobs_list = [MagicMock(spec=Job), MagicMock(spec=Job)]
        session.exec.return_value = FakeResult(jobs_list)
        repo = JobRepository(session)

        result = await repo.get_open_jobs_batch(limit=10, offset=5)

        assert result == jobs_list
        session.exec.assert_awaited_once()

    async def test_get_all_urls(self):
        session = AsyncMock()
        urls = ["http://a.com", "http://b.com"]
        session.exec.return_value = FakeResult(urls)
        repo = JobRepository(session)

        result = await repo.get_all_urls()

        assert result == urls
        session.exec.assert_awaited_once()

    async def test_drop_job(self):
        session = AsyncMock()
        repo = JobRepository(session)
        job = MagicMock(spec=Job)

        await repo.drop(job)

        session.delete.assert_called_once_with(job)
        session.flush.assert_awaited_once()

    async def test_save_or_update_missing_url_raises(self):
        session = AsyncMock()
        repo = JobRepository(session)
        job = MagicMock(spec=Job)
        job.url = None

        with pytest.raises(ValueError) as exc:
            await repo.save_or_update(job)
        assert "Job URL is required" in str(exc.value)

    async def test_save_or_update_existing_job_by_url(self):
        session = AsyncMock()
        repo = JobRepository(session)

        existing = Job(
            url="http://job.com/1",
            title="Old Title",
            status=JobStatus.OPEN,
            min_salary=10,
            max_salary=20,
            vector_context="",
            source=CrawlWebsite.ITVIEC,
        )
        repo.get_by_url = AsyncMock(return_value=existing)

        incoming = Job(
            url="http://job.com/1",
            title="New Title",
            status=JobStatus.OPEN,
            min_salary=15,
            max_salary=25,
            vector_context="",
            source=CrawlWebsite.ITVIEC,
        )

        result = await repo.save_or_update(incoming, generate_embedding=False)

        assert result is existing
        assert existing.title == "New Title"
        assert existing.min_salary == 15
        assert existing.max_salary == 25
        session.add.assert_called_with(existing)
        session.flush.assert_awaited_once()

    async def test_save_or_update_reopen_closed_job_same_source(self):
        session = AsyncMock()
        repo = JobRepository(session)

        existing_closed = Job(
            url="http://itviec.com/old",
            content_hash="hash_abc",
            source=CrawlWebsite.ITVIEC,
            status=JobStatus.CLOSED,
            title="Backend Dev",
            min_salary=10,
            max_salary=20,
            vector_context="",
        )

        repo.get_by_url = AsyncMock(return_value=None)
        repo.get_by_content_hash = AsyncMock(return_value=existing_closed)

        incoming = Job(
            url="http://itviec.com/new-link",
            content_hash="hash_abc",
            source=CrawlWebsite.ITVIEC,
            status=JobStatus.OPEN,
            title="Backend Dev Senior",
            min_salary=30,
            max_salary=40,
            vector_context="",
        )

        result = await repo.save_or_update(incoming, generate_embedding=False)

        assert result is existing_closed
        assert existing_closed.status == JobStatus.OPEN
        assert existing_closed.url == "http://itviec.com/new-link"
        assert existing_closed.title == "Backend Dev Senior"
        assert existing_closed.min_salary == 30
        session.add.assert_called_with(existing_closed)
        session.flush.assert_awaited_once()

    async def test_save_or_update_skip_duplicate_content_hash_if_open(self):
        session = AsyncMock()
        repo = JobRepository(session)

        existing_open = Job(
            url="http://itviec.com/original",
            content_hash="hash_abc",
            source=CrawlWebsite.ITVIEC,
            status=JobStatus.OPEN,
            title="Backend Dev",
            min_salary=10,
            max_salary=20,
            vector_context="",
        )

        repo.get_by_url = AsyncMock(return_value=None)
        repo.get_by_content_hash = AsyncMock(return_value=existing_open)

        incoming = Job(
            url="http://topdev.com/duplicate",
            content_hash="hash_abc",
            source=CrawlWebsite.TOPDEV,
            status=JobStatus.OPEN,
            title="Backend Dev",
            min_salary=10,
            max_salary=20,
            vector_context="",
        )

        result = await repo.save_or_update(incoming, generate_embedding=False)

        assert result is existing_open
        session.add.assert_not_called()
        session.flush.assert_not_called()

    async def test_save_or_update_new_job(self):
        session = AsyncMock()
        session.begin_nested = MagicMock()
        session.begin_nested.return_value.__aenter__.return_value = AsyncMock()
        session.begin_nested.return_value.__aexit__.return_value = AsyncMock()

        repo = JobRepository(session)
        repo.get_by_url = AsyncMock(return_value=None)
        repo.get_by_content_hash = AsyncMock(return_value=None)

        incoming = Job(
            url="http://job.com/new",
            title="New Job",
            status=JobStatus.OPEN,
            min_salary=10,
            max_salary=20,
            vector_context="",
            source=CrawlWebsite.ITVIEC,
        )

        result = await repo.save_or_update(incoming, generate_embedding=False)

        assert result is incoming
        session.add.assert_called_with(incoming)
        session.flush.assert_awaited_once()
