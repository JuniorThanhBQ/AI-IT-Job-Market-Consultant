import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agents.tools.adaptive_crawler.crawler import main, run_crawler_for_site


class TestRunCrawlerForSite:
    @patch("agents.tools.adaptive_crawler.crawler.SITE_CRAWL_TIMEOUT_SECONDS", 10.0)
    def test_run_crawler_for_site_success(self):
        mock_factory = AsyncMock()
        mock_factory.__class__.__name__ = "MockCrawlerFactory"
        mock_crawler = AsyncMock()
        mock_factory.create_crawler.return_value = mock_crawler

        urls = ["http://test.com"]

        async def _run():
            await run_crawler_for_site(
                session_factory=None,
                factory=mock_factory,
                urls=urls,
                storage_client=None,
                event_manager=None,
            )

        asyncio.run(_run())
        mock_factory.create_crawler.assert_awaited_once()
        mock_crawler.run.assert_awaited_once_with(urls)

    @patch("agents.tools.adaptive_crawler.crawler.SITE_CRAWL_TIMEOUT_SECONDS", 0.01)
    def test_run_crawler_for_site_handles_timeout(self, caplog):
        mock_factory = AsyncMock()
        mock_factory.__class__.__name__ = "MockCrawlerFactory"
        mock_crawler = AsyncMock()

        async def slow_run(*args, **kwargs):
            await asyncio.sleep(0.1)

        mock_crawler.run.side_effect = slow_run
        mock_factory.create_crawler.return_value = mock_crawler

        async def _run():
            await run_crawler_for_site(
                session_factory=None,
                factory=mock_factory,
                urls=["http://test.com"],
                storage_client=None,
                event_manager=None,
            )

        asyncio.run(_run())
        assert "Crawling timed out after" in caplog.text
        assert "[mock]" in caplog.text


class TestMainCrawlerLoop:
    @patch("agents.tools.adaptive_crawler.crawler.check_redis_connection")
    @patch("agents.tools.adaptive_crawler.crawler.RedisStorageClient")
    @patch("agents.tools.adaptive_crawler.crawler.LocalEventManager.from_config")
    @patch("agents.tools.adaptive_crawler.crawler.create_async_engine")
    @patch("agents.tools.adaptive_crawler.crawler.SQLModel.metadata.create_all")
    @patch("agents.tools.adaptive_crawler.crawler.run_crawler_for_site")
    @patch("agents.tools.adaptive_crawler.crawler.CRAWLERS")
    def test_main_executes_successfully(
        self,
        mock_crawlers_dict,
        mock_run_crawler,
        mock_db_create,
        mock_create_engine,
        mock_event_manager_factory,
        mock_storage_client,
        mock_check_redis,
    ):
        mock_engine = MagicMock()
        mock_engine.dialect.name = "postgresql"
        mock_engine.begin.return_value = AsyncMock()
        mock_engine.dispose = AsyncMock()
        mock_create_engine.return_value = mock_engine

        mock_event_manager_factory.return_value = AsyncMock()

        mock_factory_cls = MagicMock()
        mock_factory_instance = MagicMock()
        mock_factory_cls.return_value = mock_factory_instance

        mock_crawlers_dict.items.return_value = [
            (mock_factory_cls, ["http://fake.url"])
        ]

        asyncio.run(main())

        mock_check_redis.assert_awaited_once()
        mock_create_engine.assert_called_once()
        mock_engine.begin.assert_called_once()
        mock_factory_cls.assert_called_once()
        mock_run_crawler.assert_awaited_once()
        mock_engine.dispose.assert_awaited_once()

    @patch("agents.tools.adaptive_crawler.crawler.check_redis_connection")
    @patch("agents.tools.adaptive_crawler.crawler.RedisStorageClient")
    @patch("agents.tools.adaptive_crawler.crawler.LocalEventManager.from_config")
    @patch("agents.tools.adaptive_crawler.crawler.create_async_engine")
    @patch("agents.tools.adaptive_crawler.crawler.run_crawler_for_site")
    @patch("agents.tools.adaptive_crawler.crawler.CRAWLERS")
    def test_main_crawler_exception_does_not_halt_execution(
        self,
        mock_crawlers_dict,
        mock_run_crawler,
        mock_create_engine,
        mock_event_manager_factory,
        mock_storage,
        mock_check_redis,
        caplog,
    ):
        mock_engine = MagicMock()
        mock_engine.dialect.name = "postgresql"
        mock_engine.begin.return_value = AsyncMock()
        mock_engine.dispose = AsyncMock()
        mock_create_engine.return_value = mock_engine

        mock_event_manager_factory.return_value = AsyncMock()

        mock_factory_cls = MagicMock()
        mock_factory_cls.__name__ = "BadFactory"

        mock_crawlers_dict.items.return_value = [(mock_factory_cls, ["http://bad.url"])]
        mock_crawlers_dict.keys.return_value = [mock_factory_cls]
        mock_run_crawler.side_effect = Exception("Simulated fatal error")

        asyncio.run(main())

        assert "Crawl failed for BadFactory: Simulated fatal error" in caplog.text
        mock_engine.dispose.assert_awaited_once()
