from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from app.core.enums import Currency, JobStatus
from app.modules.company.models import Company
from app.modules.job.models import Job
from tools.crawler_update_tool.updater_services import check_url_status, process_job


class MockResponse:
    def __init__(self, status: int):
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


class MockRepo:
    def __init__(self):
        self.drop = AsyncMock()
        self.session = MagicMock()
        self.session.delete = AsyncMock()
        self.session.flush = AsyncMock()


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_check_url_status_success(mock_sleep: AsyncMock):
    mock_session = MagicMock()
    mock_session.get.return_value = MockResponse(status=200)
    status = await check_url_status(mock_session, "https://example.com/jobs/1")
    assert status == 200


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_check_url_status_client_error(mock_sleep: AsyncMock):
    mock_session = MagicMock()
    mock_session.get.side_effect = aiohttp.ClientError("Connection refused")
    status = await check_url_status(mock_session, "https://example.com/jobs/error")
    assert status == 0


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_check_url_status_timeout(mock_sleep: AsyncMock):
    mock_session = MagicMock()
    mock_session.get.side_effect = TimeoutError("Timeout occurred")
    status = await check_url_status(mock_session, "https://example.com/jobs/timeout")
    assert status == 0


@pytest.mark.asyncio
async def test_process_job_garbage_unknown_company():
    company = Company(name="Unknown Company")
    job = Job(
        title="Unknown Title",
        job_description="",
        company=company,
        url="https://example.com/job/garbage",
    )
    repo = MockRepo()
    mock_session = MagicMock()
    result = await process_job(job, mock_session, repo)
    assert result is True
    repo.drop.assert_awaited_once_with(job)
    repo.session.delete.assert_awaited_once_with(company)
    repo.session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_job_garbage_other_company():
    company = Company(name="Another Corp")
    job = Job(
        title="404 - Trang bạn đang tìm kiếm",
        job_description="Standard description",
        company=company,
        url="https://example.com/job/garbage2",
    )
    repo = MockRepo()
    mock_session = MagicMock()
    result = await process_job(job, mock_session, repo)
    assert result is True
    repo.drop.assert_awaited_once_with(job)
    repo.session.delete.assert_not_called()


@pytest.mark.asyncio
async def test_process_job_duplicate_description():
    company = Company(name="Repetitive Corp")
    job = Job(
        title="Software Engineer",
        job_description=(
            "Scale search on a scale. "
            "Scale search on a scale. "
            "Scale search on a scale. "
            "Scale search on a scale."
        ),
        company=company,
        url="https://example.com/job/dup",
    )
    repo = MockRepo()
    mock_session = MagicMock()
    result = await process_job(job, mock_session, repo)
    assert result is True
    repo.drop.assert_awaited_once_with(job)


@pytest.mark.asyncio
async def test_process_job_missing_url():
    company = Company(name="Valid Corp")
    job = Job(
        title="Senior Developer",
        job_description="Full stack dev role",
        company=company,
        url="",
        status=JobStatus.OPEN,
    )
    repo = MockRepo()
    mock_session = MagicMock()
    result = await process_job(job, mock_session, repo)
    assert result is True
    assert job.status == JobStatus.CLOSED


@pytest.mark.asyncio
async def test_process_job_expired_date():
    company = Company(name="Valid Corp")
    past_date = datetime.now(UTC) - timedelta(days=2)
    job = Job(
        title="Senior Developer",
        job_description="Full stack dev role",
        company=company,
        url="https://example.com/job/expired",
        expired_date=past_date,
        status=JobStatus.OPEN,
    )
    repo = MockRepo()
    mock_session = MagicMock()
    result = await process_job(job, mock_session, repo)
    assert result is True
    assert job.status == JobStatus.CLOSED
    mock_session.get.assert_not_called()


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_process_job_url_closed_404(mock_sleep: AsyncMock):
    company = Company(name="Valid Corp")
    future_date = datetime.now(UTC) + timedelta(days=10)
    job = Job(
        title="Senior Developer",
        job_description="Full stack dev role",
        company=company,
        url="https://example.com/job/404",
        expired_date=future_date,
        status=JobStatus.OPEN,
    )
    repo = MockRepo()
    mock_session = MagicMock()
    mock_session.get.return_value = MockResponse(status=404)
    result = await process_job(job, mock_session, repo)
    assert result is True
    assert job.status == JobStatus.CLOSED


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_process_job_url_blocked_403(mock_sleep: AsyncMock):
    company = Company(name="Valid Corp")
    future_date = datetime.now(UTC) + timedelta(days=10)
    job = Job(
        title="Senior Developer",
        job_description="Full stack dev role",
        company=company,
        url="https://example.com/job/403",
        expired_date=future_date,
        status=JobStatus.OPEN,
    )
    repo = MockRepo()
    mock_session = MagicMock()
    mock_session.get.return_value = MockResponse(status=403)
    result = await process_job(job, mock_session, repo)
    assert result is False
    assert job.status == JobStatus.OPEN


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_process_job_salary_normalization_vnd_to_usd(mock_sleep: AsyncMock):
    company = Company(name="Valid Corp")
    future_date = datetime.now(UTC) + timedelta(days=10)
    job = Job(
        title="Senior Developer",
        job_description="Full stack dev role",
        company=company,
        url="https://example.com/job/salary",
        expired_date=future_date,
        min_salary=2000,
        max_salary=3500,
        currency=Currency.VND,
        status=JobStatus.OPEN,
    )
    repo = MockRepo()
    mock_session = MagicMock()
    mock_session.get.return_value = MockResponse(status=200)
    result = await process_job(job, mock_session, repo)
    assert result is True
    assert job.currency == Currency.USD


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_process_job_valid_unchanged(mock_sleep: AsyncMock):
    company = Company(name="Valid Corp")
    future_date = datetime.now(UTC) + timedelta(days=10)
    job = Job(
        title="Senior Developer",
        job_description="Full stack dev role",
        company=company,
        url="https://example.com/job/valid",
        expired_date=future_date,
        min_salary=30000000,
        max_salary=50000000,
        currency=Currency.VND,
        status=JobStatus.OPEN,
    )
    repo = MockRepo()
    mock_session = MagicMock()
    mock_session.get.return_value = MockResponse(status=200)
    result = await process_job(job, mock_session, repo)
    assert result is False
    assert job.status == JobStatus.OPEN
    assert job.currency == Currency.VND
