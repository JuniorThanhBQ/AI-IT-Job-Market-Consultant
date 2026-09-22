from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tools.adaptive_crawler.crawler import main, run_crawler_for_site


class MockAsyncContextManager:
    def __init__(self, target):
        self.target = target

    async def __aenter__(self):
        return self.target

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


class FakeCrawlerFactory:
    pass


class FailedCrawlerFactory:
    pass


@pytest.mark.asyncio
async def test_run_crawler_for_site_success() -> None:
    mock_session_factory = MagicMock()
    mock_storage_client = MagicMock()
    mock_event_manager = MagicMock()
    mock_crawler = MagicMock()
    mock_crawler.run = AsyncMock()

    mock_factory = MagicMock()
    mock_factory.__class__.__name__ = "ITViecCrawlerFactory"
    mock_factory.create_crawler = AsyncMock(return_value=mock_crawler)

    urls = ["https://itviec.com/it-jobs"]
    await run_crawler_for_site(
        mock_session_factory,
        mock_factory,
        urls,
        mock_storage_client,
        mock_event_manager,
    )

    mock_factory.create_crawler.assert_awaited_once_with(
        mock_session_factory,
        storage_client=mock_storage_client,
        event_manager=mock_event_manager,
    )
    mock_crawler.run.assert_awaited_once_with(urls)


@pytest.mark.asyncio
@patch("tools.adaptive_crawler.crawler.logger")
@patch("tools.adaptive_crawler.crawler.asyncio.wait_for")
async def test_run_crawler_for_site_timeout(
    mock_wait_for: MagicMock,
    mock_logger: MagicMock,
) -> None:
    mock_session_factory = MagicMock()
    mock_storage_client = MagicMock()
    mock_event_manager = MagicMock()
    mock_crawler = MagicMock()
    mock_factory = MagicMock()
    mock_factory.__class__.__name__ = "TopDevCrawlerFactory"
    mock_factory.create_crawler = AsyncMock(return_value=mock_crawler)
    mock_wait_for.side_effect = TimeoutError()

    await run_crawler_for_site(
        mock_session_factory,
        mock_factory,
        ["https://topdev.vn"],
        mock_storage_client,
        mock_event_manager,
    )

    mock_logger.error.assert_called_once()
    assert "[topdev]" in mock_logger.error.call_args[0][0]


@pytest.mark.asyncio
@patch(
    "tools.adaptive_crawler.crawler.CRAWLERS",
    {FakeCrawlerFactory: ["https://example.com"]},
)
@patch("tools.adaptive_crawler.crawler.run_crawler_for_site")
@patch("tools.adaptive_crawler.crawler.create_async_engine")
@patch("tools.adaptive_crawler.crawler.LocalEventManager")
@patch("tools.adaptive_crawler.crawler.RedisStorageClient")
@patch("tools.adaptive_crawler.crawler.check_redis_connection")
async def test_main_success_postgresql(
    mock_check_redis: MagicMock,
    mock_redis_client_cls: MagicMock,
    mock_event_mgr_cls: MagicMock,
    mock_create_engine: MagicMock,
    mock_run_crawler: MagicMock,
) -> None:
    mock_check_redis.return_value = None
    mock_event_mgr = MockAsyncContextManager(MagicMock())
    mock_event_mgr_cls.from_config.return_value = mock_event_mgr
    mock_conn = MagicMock()
    mock_conn.execute = AsyncMock()
    mock_conn.run_sync = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dialect.name = "postgresql"
    mock_engine.begin.return_value = MockAsyncContextManager(mock_conn)
    mock_engine.dispose = AsyncMock()
    mock_create_engine.return_value = mock_engine

    await main()

    mock_check_redis.assert_awaited_once()
    mock_conn.execute.assert_awaited_once()
    mock_conn.run_sync.assert_awaited_once()
    mock_run_crawler.assert_awaited_once()
    mock_engine.dispose.assert_awaited_once()


@pytest.mark.asyncio
@patch("tools.adaptive_crawler.crawler.CRAWLERS", {})
@patch("tools.adaptive_crawler.crawler.run_crawler_for_site")
@patch("tools.adaptive_crawler.crawler.create_async_engine")
@patch("tools.adaptive_crawler.crawler.LocalEventManager")
@patch("tools.adaptive_crawler.crawler.RedisStorageClient")
@patch("tools.adaptive_crawler.crawler.check_redis_connection")
async def test_main_non_postgresql(
    mock_check_redis: MagicMock,
    mock_redis_client_cls: MagicMock,
    mock_event_mgr_cls: MagicMock,
    mock_create_engine: MagicMock,
    mock_run_crawler: MagicMock,
) -> None:
    mock_check_redis.return_value = None
    mock_event_mgr = MockAsyncContextManager(MagicMock())
    mock_event_mgr_cls.from_config.return_value = mock_event_mgr
    mock_conn = MagicMock()
    mock_conn.execute = AsyncMock()
    mock_conn.run_sync = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dialect.name = "sqlite"
    mock_engine.begin.return_value = MockAsyncContextManager(mock_conn)
    mock_engine.dispose = AsyncMock()
    mock_create_engine.return_value = mock_engine

    await main()

    mock_conn.execute.assert_not_awaited()
    mock_conn.run_sync.assert_awaited_once()
    mock_engine.dispose.assert_awaited_once()


@pytest.mark.asyncio
@patch(
    "tools.adaptive_crawler.crawler.CRAWLERS",
    {FailedCrawlerFactory: ["https://failed.com"]},
)
@patch("tools.adaptive_crawler.crawler.logger")
@patch("tools.adaptive_crawler.crawler.run_crawler_for_site")
@patch("tools.adaptive_crawler.crawler.create_async_engine")
@patch("tools.adaptive_crawler.crawler.LocalEventManager")
@patch("tools.adaptive_crawler.crawler.RedisStorageClient")
@patch("tools.adaptive_crawler.crawler.check_redis_connection")
async def test_main_crawler_site_error_handled(
    mock_check_redis: MagicMock,
    mock_redis_client_cls: MagicMock,
    mock_event_mgr_cls: MagicMock,
    mock_create_engine: MagicMock,
    mock_run_crawler: MagicMock,
    mock_logger: MagicMock,
) -> None:
    mock_check_redis.return_value = None
    mock_event_mgr = MockAsyncContextManager(MagicMock())
    mock_event_mgr_cls.from_config.return_value = mock_event_mgr
    mock_conn = MagicMock()
    mock_conn.execute = AsyncMock()
    mock_conn.run_sync = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dialect.name = "postgresql"
    mock_engine.begin.return_value = MockAsyncContextManager(mock_conn)
    mock_engine.dispose = AsyncMock()
    mock_create_engine.return_value = mock_engine
    mock_run_crawler.side_effect = RuntimeError("Crawler error occurred")

    await main()

    mock_run_crawler.assert_awaited_once()
    mock_logger.error.assert_called_once()
    assert "Crawl failed for FailedCrawlerFactory" in mock_logger.error.call_args[0][0]
    mock_engine.dispose.assert_awaited_once()
