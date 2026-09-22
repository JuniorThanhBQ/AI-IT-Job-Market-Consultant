import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tools.crawl4ai_crawler.crawler import run_crawl4ai_main


class MockAsyncContextManager:
    def __init__(self, target):
        self.target = target

    async def __aenter__(self):
        return self.target

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


class MockRunResult:
    def __init__(self, extracted_content: str | None):
        self.extracted_content = extracted_content


@pytest.mark.asyncio
@patch("tools.crawl4ai_crawler.crawler.JobRepository")
@patch("tools.crawl4ai_crawler.crawler.crawl4ai_adapter")
@patch("tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
@patch("tools.crawl4ai_crawler.crawler.async_sessionmaker")
@patch("tools.crawl4ai_crawler.crawler.create_async_engine")
async def test_run_crawl4ai_main_full_flow(
    mock_create_engine: MagicMock,
    mock_sessionmaker: MagicMock,
    mock_web_crawler_class: MagicMock,
    mock_adapter: MagicMock,
    mock_repo_class: MagicMock,
):
    mock_conn = MagicMock()
    mock_conn.execute = AsyncMock()
    mock_conn.run_sync = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dialect.name = "postgresql"
    mock_engine.begin.return_value = MockAsyncContextManager(mock_conn)
    mock_engine.dispose = AsyncMock()
    mock_create_engine.return_value = mock_engine
    mock_db_session = MagicMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.rollback = AsyncMock()
    mock_sessionmaker.return_value = MagicMock(
        return_value=MockAsyncContextManager(mock_db_session)
    )

    mock_repo = MagicMock()
    mock_repo.save_or_update = AsyncMock()
    mock_repo_class.return_value = mock_repo
    mock_adapter.return_value = MagicMock()
    list_payload = json.dumps([{"url": "/job/101"}, {"url": "/job/102"}])
    detail_payload = json.dumps([{"title": "Backend Engineer", "salary": "2000 USD"}])
    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(
        side_effect=[
            MockRunResult(extracted_content=list_payload),
            MockRunResult(extracted_content=detail_payload),
            MockRunResult(extracted_content=detail_payload),
        ]
    )
    mock_web_crawler_class.return_value = MockAsyncContextManager(mock_crawler)

    await run_crawl4ai_main()
    assert mock_conn.execute.await_count == 1
    assert mock_conn.run_sync.await_count == 1
    assert mock_crawler.arun.await_count == 3
    assert mock_repo.save_or_update.await_count == 2
    assert mock_db_session.commit.await_count == 2
    assert mock_engine.dispose.await_count == 1


@pytest.mark.asyncio
@patch("tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
@patch("tools.crawl4ai_crawler.crawler.async_sessionmaker")
@patch("tools.crawl4ai_crawler.crawler.create_async_engine")
async def test_run_crawl4ai_main_empty_list_result(
    mock_create_engine: MagicMock,
    mock_sessionmaker: MagicMock,
    mock_web_crawler_class: MagicMock,
):
    mock_conn = MagicMock()
    mock_conn.execute = AsyncMock()
    mock_conn.run_sync = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dialect.name = "sqlite"
    mock_engine.begin.return_value = MockAsyncContextManager(mock_conn)
    mock_engine.dispose = AsyncMock()
    mock_create_engine.return_value = mock_engine
    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(return_value=MockRunResult(extracted_content=None))
    mock_web_crawler_class.return_value = MockAsyncContextManager(mock_crawler)

    await run_crawl4ai_main()
    assert mock_conn.execute.await_count == 0
    assert mock_crawler.arun.await_count == 1
    assert mock_engine.dispose.await_count == 1


@pytest.mark.asyncio
@patch("tools.crawl4ai_crawler.crawler.JobRepository")
@patch("tools.crawl4ai_crawler.crawler.crawl4ai_adapter")
@patch("tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
@patch("tools.crawl4ai_crawler.crawler.async_sessionmaker")
@patch("tools.crawl4ai_crawler.crawler.create_async_engine")
async def test_run_crawl4ai_main_db_save_error_rolls_back(
    mock_create_engine: MagicMock,
    mock_sessionmaker: MagicMock,
    mock_web_crawler_class: MagicMock,
    mock_adapter: MagicMock,
    mock_repo_class: MagicMock,
):
    mock_conn = MagicMock()
    mock_conn.execute = AsyncMock()
    mock_conn.run_sync = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dialect.name = "postgresql"
    mock_engine.begin.return_value = MockAsyncContextManager(mock_conn)
    mock_engine.dispose = AsyncMock()
    mock_create_engine.return_value = mock_engine
    mock_db_session = MagicMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.rollback = AsyncMock()
    mock_sessionmaker.return_value = MagicMock(
        return_value=MockAsyncContextManager(mock_db_session)
    )
    mock_repo = MagicMock()
    mock_repo.save_or_update = AsyncMock(
        side_effect=RuntimeError("DB constraint error")
    )
    mock_repo_class.return_value = mock_repo
    mock_adapter.return_value = MagicMock()
    list_payload = json.dumps([{"url": "/job/201"}])
    detail_payload = json.dumps({"title": "DevOps Engineer", "salary": "3000 USD"})
    mock_crawler = MagicMock()
    mock_crawler.arun = AsyncMock(
        side_effect=[
            MockRunResult(extracted_content=list_payload),
            MockRunResult(extracted_content=detail_payload),
        ]
    )
    mock_web_crawler_class.return_value = MockAsyncContextManager(mock_crawler)
    await run_crawl4ai_main()
    mock_db_session.rollback.assert_awaited_once()
    assert mock_engine.dispose.await_count == 1
