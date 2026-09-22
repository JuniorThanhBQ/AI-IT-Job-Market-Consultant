from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.modules.job.models import Job
from sqlalchemy.exc import SQLAlchemyError
from tools.crawler_update_tool.job_updater import update_jobs_workflow


class MockAsyncContextManager:
    def __init__(self, target):
        self.target = target

    async def __aenter__(self):
        return self.target

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


@pytest.mark.asyncio
@patch("tools.crawler_update_tool.job_updater.process_job")
@patch("tools.crawler_update_tool.job_updater.JobRepository")
@patch("tools.crawler_update_tool.job_updater.aiohttp.ClientSession")
@patch("tools.crawler_update_tool.job_updater.async_sessionmaker")
@patch("tools.crawler_update_tool.job_updater.create_async_engine")
async def test_update_jobs_workflow_300_samples_in_batches_of_50(
    mock_create_engine: MagicMock,
    mock_sessionmaker: MagicMock,
    mock_client_session_class: MagicMock,
    mock_repo_class: MagicMock,
    mock_process_job_fn: AsyncMock,
):
    batch_size = 50
    sample_batches = []
    for batch_index in range(6):
        batch = [
            Job(id=batch_index * batch_size + item_index + 1, title="Test Job")
            for item_index in range(batch_size)
        ]
        sample_batches.append(batch)
    sample_batches.append([])
    mock_db_session = MagicMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.rollback = AsyncMock()
    mock_session_factory = MagicMock(
        return_value=MockAsyncContextManager(mock_db_session)
    )
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()
    mock_http_session = MagicMock()
    mock_client_session = MagicMock(
        return_value=MockAsyncContextManager(mock_http_session)
    )

    batch_call_counter = 0

    async def mock_get_open_jobs_batch(limit: int = 50, offset: int = 0):
        nonlocal batch_call_counter
        batch_to_return = sample_batches[batch_call_counter]
        batch_call_counter += 1
        return batch_to_return

    async def mock_process_job(job, session, repo):
        return job.id % 2 == 0

    mock_create_engine.return_value = mock_engine
    mock_sessionmaker.return_value = mock_session_factory
    mock_client_session_class.return_value = mock_client_session()
    mock_process_job_fn.side_effect = mock_process_job
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_open_jobs_batch = AsyncMock(
        side_effect=mock_get_open_jobs_batch
    )
    mock_repo_class.return_value = mock_repo_instance

    result = await update_jobs_workflow()

    assert result["status"] == "success"
    assert result["modified_jobs_count"] == 150
    assert len(result["modified_job_ids"]) == 150
    assert mock_db_session.commit.await_count == 6
    assert mock_engine.dispose.await_count == 1


@pytest.mark.asyncio
@patch("tools.crawler_update_tool.job_updater.process_job")
@patch("tools.crawler_update_tool.job_updater.JobRepository")
@patch("tools.crawler_update_tool.job_updater.aiohttp.ClientSession")
@patch("tools.crawler_update_tool.job_updater.async_sessionmaker")
@patch("tools.crawler_update_tool.job_updater.create_async_engine")
async def test_update_jobs_workflow_no_modifications(
    mock_create_engine: MagicMock,
    mock_sessionmaker: MagicMock,
    mock_client_session_class: MagicMock,
    mock_repo_class: MagicMock,
    mock_process_job_fn: AsyncMock,
):
    mock_db_session = MagicMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.rollback = AsyncMock()
    mock_session_factory = MagicMock(
        return_value=MockAsyncContextManager(mock_db_session)
    )
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()
    mock_http_session = MagicMock()
    mock_client_session = MagicMock(
        return_value=MockAsyncContextManager(mock_http_session)
    )
    batch_calls = 0

    async def mock_get_open_jobs_batch(limit: int = 50, offset: int = 0):
        nonlocal batch_calls
        if batch_calls == 0:
            batch_calls += 1
            return [Job(id=1, title="Test Job")]
        return []

    async def mock_process_job(job, session, repo):
        return False

    mock_create_engine.return_value = mock_engine
    mock_sessionmaker.return_value = mock_session_factory
    mock_client_session_class.return_value = mock_client_session()
    mock_process_job_fn.side_effect = mock_process_job
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_open_jobs_batch = AsyncMock(
        side_effect=mock_get_open_jobs_batch
    )
    mock_repo_class.return_value = mock_repo_instance

    result = await update_jobs_workflow()

    assert result["status"] == "success"
    assert result["modified_jobs_count"] == 0
    assert result["modified_job_ids"] == []
    mock_db_session.commit.assert_not_called()
    assert mock_engine.dispose.await_count == 1


@pytest.mark.asyncio
@patch("tools.crawler_update_tool.job_updater.process_job")
@patch("tools.crawler_update_tool.job_updater.JobRepository")
@patch("tools.crawler_update_tool.job_updater.aiohttp.ClientSession")
@patch("tools.crawler_update_tool.job_updater.async_sessionmaker")
@patch("tools.crawler_update_tool.job_updater.create_async_engine")
async def test_update_jobs_workflow_commit_error_rolls_back(
    mock_create_engine: MagicMock,
    mock_sessionmaker: MagicMock,
    mock_client_session_class: MagicMock,
    mock_repo_class: MagicMock,
    mock_process_job_fn: AsyncMock,
):
    mock_db_session = MagicMock()
    mock_db_session.commit = AsyncMock(side_effect=SQLAlchemyError("DB error"))
    mock_db_session.rollback = AsyncMock()
    mock_session_factory = MagicMock(
        return_value=MockAsyncContextManager(mock_db_session)
    )
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()
    mock_http_session = MagicMock()
    mock_client_session = MagicMock(
        return_value=MockAsyncContextManager(mock_http_session)
    )

    batch_calls = 0

    async def mock_get_open_jobs_batch(limit: int = 50, offset: int = 0):
        nonlocal batch_calls
        if batch_calls == 0:
            batch_calls += 1
            return [Job(id=1, title="Test Job")]
        return []

    async def mock_process_job(job, session, repo):
        return True

    mock_create_engine.return_value = mock_engine
    mock_sessionmaker.return_value = mock_session_factory
    mock_client_session_class.return_value = mock_client_session()
    mock_process_job_fn.side_effect = mock_process_job
    mock_repo_instance = MagicMock()
    mock_repo_instance.get_open_jobs_batch = AsyncMock(
        side_effect=mock_get_open_jobs_batch
    )
    mock_repo_class.return_value = mock_repo_instance
    result = await update_jobs_workflow()

    assert result["status"] == "success"
    mock_db_session.rollback.assert_awaited_once()
    assert mock_engine.dispose.await_count == 1


@pytest.mark.asyncio
@patch("tools.crawler_update_tool.job_updater.create_async_engine")
@patch("tools.crawler_update_tool.job_updater.async_sessionmaker")
async def test_update_jobs_workflow_fatal_exception_handling(
    mock_sessionmaker: MagicMock,
    mock_create_engine: MagicMock,
):
    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()
    mock_create_engine.return_value = mock_engine
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__.side_effect = RuntimeError(
        "Fatal startup failure inside try"
    )
    mock_sessionmaker.return_value = MagicMock(return_value=mock_context_manager)
    with pytest.raises(RuntimeError):
        await update_jobs_workflow()

    assert mock_engine.dispose.await_count == 1
