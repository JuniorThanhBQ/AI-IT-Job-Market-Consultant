import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from tools.crawler_update_tool.job_updater import update_jobs_workflow


@pytest.mark.asyncio
class TestUpdateJobsWorkflow:
    @patch("tools.crawler_update_tool.job_updater.generate_session_fingerprint")
    @patch("tools.crawler_update_tool.job_updater.create_async_engine")
    @patch("tools.crawler_update_tool.job_updater.async_sessionmaker")
    @patch("tools.crawler_update_tool.job_updater.aiohttp.ClientSession")
    @patch("tools.crawler_update_tool.job_updater.JobRepository")
    @patch("tools.crawler_update_tool.job_updater.process_job", new_callable=AsyncMock)
    async def test_workflow_no_jobs(
        self,
        mock_process,
        mock_repo_class,
        mock_client,
        mock_sessionmaker,
        mock_engine,
        mock_fingerprint,
    ):
        mock_fingerprint.return_value = {"extra_http_headers": {}}
        mock_engine.return_value.dispose = AsyncMock()
        mock_db_session = AsyncMock()
        mock_sessionmaker.return_value = MagicMock(return_value=mock_db_session)
        mock_db_session.__aenter__.return_value = mock_db_session

        mock_repo_instance = MagicMock()
        mock_repo_instance.get_open_jobs_batch = AsyncMock(return_value=[])
        mock_repo_class.return_value = mock_repo_instance

        result = await update_jobs_workflow()

        assert result["status"] == "success"
        assert result["modified_jobs_count"] == 0
        assert result["modified_job_ids"] == []
        mock_process.assert_not_called()
        mock_db_session.commit.assert_not_called()

    @patch("tools.crawler_update_tool.job_updater.generate_session_fingerprint")
    @patch("tools.crawler_update_tool.job_updater.create_async_engine")
    @patch("tools.crawler_update_tool.job_updater.async_sessionmaker")
    @patch("tools.crawler_update_tool.job_updater.aiohttp.ClientSession")
    @patch("tools.crawler_update_tool.job_updater.JobRepository")
    @patch("tools.crawler_update_tool.job_updater.process_job", new_callable=AsyncMock)
    async def test_workflow_with_modifications(
        self,
        mock_process,
        mock_repo_class,
        mock_client,
        mock_sessionmaker,
        mock_engine,
        mock_fingerprint,
    ):
        mock_fingerprint.return_value = {"extra_http_headers": {}}
        mock_engine.return_value.dispose = AsyncMock()
        mock_db_session = AsyncMock()
        mock_sessionmaker.return_value = MagicMock(return_value=mock_db_session)
        mock_db_session.__aenter__.return_value = mock_db_session

        mock_job_1 = MagicMock(id=1)
        mock_job_2 = MagicMock(id=2)
        mock_job_3 = MagicMock(id=3)

        mock_repo_instance = MagicMock()
        mock_repo_instance.get_open_jobs_batch = AsyncMock(
            side_effect=[[mock_job_1, mock_job_2, mock_job_3], []]
        )
        mock_repo_class.return_value = mock_repo_instance

        mock_process.side_effect = [True, False, Exception("Process Error")]

        result = await update_jobs_workflow()

        assert result["status"] == "success"
        assert result["modified_jobs_count"] == 1
        assert result["modified_job_ids"] == [1]
        assert mock_process.call_count == 3
        mock_db_session.commit.assert_called_once()

    @patch("tools.crawler_update_tool.job_updater.generate_session_fingerprint")
    @patch("tools.crawler_update_tool.job_updater.create_async_engine")
    @patch("tools.crawler_update_tool.job_updater.async_sessionmaker")
    @patch("tools.crawler_update_tool.job_updater.aiohttp.ClientSession")
    @patch("tools.crawler_update_tool.job_updater.JobRepository")
    @patch("tools.crawler_update_tool.job_updater.process_job", new_callable=AsyncMock)
    async def test_workflow_commit_failure(
        self,
        mock_process,
        mock_repo_class,
        mock_client,
        mock_sessionmaker,
        mock_engine,
        mock_fingerprint,
    ):
        mock_fingerprint.return_value = {"extra_http_headers": {}}
        mock_engine.return_value.dispose = AsyncMock()
        mock_db_session = AsyncMock()
        mock_sessionmaker.return_value = MagicMock(return_value=mock_db_session)
        mock_db_session.__aenter__.return_value = mock_db_session
        mock_db_session.commit.side_effect = Exception("DB Integrity Error")

        mock_job = MagicMock(id=99)
        mock_repo_instance = MagicMock()
        mock_repo_instance.get_open_jobs_batch = AsyncMock(side_effect=[[mock_job], []])
        mock_repo_class.return_value = mock_repo_instance
        mock_process.return_value = True

        result = await update_jobs_workflow()

        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_called_once()
        assert result["modified_jobs_count"] == 1

    @patch("tools.crawler_update_tool.job_updater.create_async_engine")
    async def test_workflow_global_exception(self, mock_engine):
        mock_engine.side_effect = Exception("Fatal Engine Error")
        with pytest.raises(Exception) as exc:
            await update_jobs_workflow()
        assert "Fatal Engine Error" in str(exc.value)
