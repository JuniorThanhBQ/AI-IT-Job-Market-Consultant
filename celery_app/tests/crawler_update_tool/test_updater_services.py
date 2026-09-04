from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.core.enums import Currency, JobStatus
from tools.crawler_update_tool.updater_services import (
    check_url_status,
    process_job,
    update_embeddings,
)


@pytest.mark.asyncio
class TestCheckUrlStatus:
    @patch(
        "tools.crawler_update_tool.updater_services.asyncio.sleep",
        new_callable=AsyncMock,
    )
    async def test_check_url_status_success(self, mock_sleep):
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_session.get.return_value.__aenter__.return_value = mock_response

        status = await check_url_status(mock_session, "http://test.com")
        assert status == 200
        mock_sleep.assert_called_once()

    @patch(
        "tools.crawler_update_tool.updater_services.asyncio.sleep",
        new_callable=AsyncMock,
    )
    async def test_check_url_status_exception(self, mock_sleep):
        mock_session = AsyncMock()
        mock_session.get.side_effect = Exception("Connection Timeout")

        status = await check_url_status(mock_session, "http://error.com")
        assert status == 0


@pytest.mark.asyncio
class TestUpdateEmbeddings:
    @patch(
        "tools.crawler_update_tool.updater_services.generate_embedding_async",
        new_callable=AsyncMock,
    )
    async def test_no_vector_context(self, mock_generate):
        mock_job = MagicMock()
        mock_job.vector_context = None
        mock_job.company = MagicMock()
        mock_job.company.vector_context = None

        is_modified = await update_embeddings(mock_job, MagicMock())
        assert is_modified is False
        mock_generate.assert_not_called()

    @patch(
        "tools.crawler_update_tool.updater_services.generate_embedding_async",
        new_callable=AsyncMock,
    )
    async def test_generate_new_embedding(self, mock_generate):
        mock_generate.return_value = MagicMock(token_used=10, latency=0.5, log="ok")

        mock_job = MagicMock()
        mock_job.vector_context = "test context"
        mock_job.embedding = None
        mock_job.updated_date = datetime.now(UTC)
        mock_job.company = None

        is_modified = await update_embeddings(mock_job, MagicMock())
        assert is_modified is True
        mock_generate.assert_called_once()
        assert mock_job.embedding is not None

    @patch(
        "tools.crawler_update_tool.updater_services.generate_embedding_async",
        new_callable=AsyncMock,
    )
    async def test_skip_update_if_recent(self, mock_generate):
        now = datetime.now(UTC)
        mock_job = MagicMock()
        mock_job.vector_context = "test context"
        mock_job.updated_date = now
        mock_job.embedding = MagicMock()
        mock_job.embedding.updated_date = now - timedelta(hours=12)
        mock_job.company = None

        is_modified = await update_embeddings(mock_job, MagicMock())
        assert is_modified is False
        mock_generate.assert_not_called()

    @patch(
        "tools.crawler_update_tool.updater_services.generate_embedding_async",
        new_callable=AsyncMock,
    )
    async def test_trigger_update_if_old(self, mock_generate):
        now = datetime.now(UTC)
        mock_generate.return_value = "new_vector_data"

        mock_job = MagicMock()
        mock_job.vector_context = "test context"
        mock_job.updated_date = now
        mock_job.embedding = MagicMock()
        mock_job.embedding.updated_date = now - timedelta(hours=25)
        mock_job.company = None

        is_modified = await update_embeddings(mock_job, MagicMock())
        assert is_modified is True
        mock_generate.assert_called_once()
        assert mock_job.embedding.embedding == "new_vector_data"

    @patch(
        "tools.crawler_update_tool.updater_services.generate_embedding_async",
        new_callable=AsyncMock,
    )
    async def test_update_exception_handling(self, mock_generate):
        mock_generate.side_effect = Exception("API limit reached")

        mock_job = MagicMock()
        mock_job.vector_context = "context"
        mock_job.embedding = None
        mock_job.company = None

        is_modified = await update_embeddings(mock_job, MagicMock())
        assert is_modified is False


@pytest.mark.asyncio
class TestProcessJob:
    async def test_delete_unknown_job(self):
        mock_repo = AsyncMock()
        mock_job = MagicMock()
        mock_job.title = "Unknown Title"
        mock_job.job_description = ""
        mock_job.company.name = "Unknown Company"

        result = await process_job(mock_job, AsyncMock(), mock_repo)
        assert result is True
        mock_repo.drop.assert_called_once_with(mock_job)
        mock_repo.session.delete.assert_called_once_with(mock_job.company)
        mock_repo.session.flush.assert_called_once()

    async def test_close_job_with_no_url(self):
        mock_job = MagicMock()
        mock_job.title = "Valid Title"
        mock_job.url = None

        result = await process_job(mock_job, AsyncMock(), AsyncMock())
        assert result is True
        assert mock_job.status == JobStatus.CLOSED

    @patch("tools.crawler_update_tool.updater_services.datetime")
    @patch(
        "tools.crawler_update_tool.updater_services.check_url_status",
        new_callable=AsyncMock,
    )
    @patch(
        "tools.crawler_update_tool.updater_services.update_embeddings",
        new_callable=AsyncMock,
    )
    async def test_job_expired_and_salary_conversion(
        self, mock_update_emb, mock_check_url, mock_dt
    ):
        fixed_now = datetime(2023, 1, 15)
        mock_dt.now.return_value = fixed_now
        mock_check_url.return_value = 200
        mock_update_emb.return_value = False

        mock_job = MagicMock()
        mock_job.title = "Developer"
        mock_job.url = "http://valid.com"
        mock_job.status = JobStatus.OPEN
        mock_job.expired_date = datetime(2023, 1, 10)
        mock_job.min_salary = 5000
        mock_job.max_salary = 8000
        mock_job.currency = Currency.VND

        result = await process_job(mock_job, AsyncMock(), AsyncMock())
        assert result is True
        assert mock_job.status == JobStatus.CLOSED
        assert mock_job.currency == Currency.USD

    @patch("tools.crawler_update_tool.updater_services.datetime")
    async def test_drop_closed_job_over_threshold(self, mock_dt):
        fixed_now = datetime(2023, 1, 15)
        mock_dt.now.return_value = fixed_now

        mock_repo = AsyncMock()
        mock_job = MagicMock()
        mock_job.title = "Closed Job"
        mock_job.url = "http://closed.com"
        mock_job.status = JobStatus.CLOSED
        mock_job.expired_date = datetime(2023, 1, 5)
        mock_job.min_salary = 0
        mock_job.max_salary = 0
        mock_job.currency = Currency.VND
        mock_job.company = None

        result = await process_job(mock_job, AsyncMock(), mock_repo)
        assert result is True
        mock_repo.drop.assert_called_once_with(mock_job)

    @patch(
        "tools.crawler_update_tool.updater_services.check_url_status",
        new_callable=AsyncMock,
    )
    @patch(
        "tools.crawler_update_tool.updater_services.update_embeddings",
        new_callable=AsyncMock,
    )
    async def test_url_status_404_closes_job(self, mock_update_emb, mock_check_url):
        mock_check_url.return_value = 404
        mock_update_emb.return_value = False

        mock_job = MagicMock()
        mock_job.title = "Valid Job"
        mock_job.url = "http://404.com"
        mock_job.status = JobStatus.OPEN
        mock_job.expired_date = None
        mock_job.min_salary = 0
        mock_job.max_salary = 0

        result = await process_job(mock_job, AsyncMock(), AsyncMock())
        assert result is True
        assert mock_job.status == JobStatus.CLOSED

    @patch(
        "tools.crawler_update_tool.updater_services.check_url_status",
        new_callable=AsyncMock,
    )
    @patch(
        "tools.crawler_update_tool.updater_services.update_embeddings",
        new_callable=AsyncMock,
    )
    async def test_url_status_rate_limit_ignored(self, mock_update_emb, mock_check_url):
        mock_check_url.return_value = 429
        mock_update_emb.return_value = False

        mock_job = MagicMock()
        mock_job.title = "Valid Job"
        mock_job.url = "http://blocked.com"
        mock_job.status = JobStatus.OPEN
        mock_job.expired_date = None
        mock_job.min_salary = 0
        mock_job.max_salary = 0

        result = await process_job(mock_job, AsyncMock(), AsyncMock())
        assert result is False
        assert mock_job.status == JobStatus.OPEN

    async def test_delete_job_due_to_placeholder_title(self):
        mock_repo = AsyncMock()
        mock_job = MagicMock()
        mock_job.title = "Trang bạn đang tìm kiếm"

        result = await process_job(mock_job, AsyncMock(), mock_repo)
        assert result is True
        mock_repo.drop.assert_called_once_with(mock_job)
        mock_repo.session.flush.assert_called_once()
