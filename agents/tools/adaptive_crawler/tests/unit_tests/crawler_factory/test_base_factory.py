import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agents.tools.adaptive_crawler.crawler_factory.base_factory import (
    BaseCrawlerFactory,
)


class DummyCrawlerFactory(BaseCrawlerFactory):
    def get_handler(self, session_factory):
        return MagicMock()


class TestBaseCrawlerFactory:
    @pytest.fixture
    def factory(self):
        return DummyCrawlerFactory()

    @patch("agents.tools.adaptive_crawler.crawler_factory.base_factory.asyncio.sleep")
    @patch("agents.tools.adaptive_crawler.crawler_factory.base_factory.random.uniform")
    def test_apply_delay(self, mock_uniform, mock_sleep, factory):
        mock_uniform.return_value = 1.5

        async def _run():
            await factory.apply_delay()

        asyncio.run(_run())
        mock_uniform.assert_called_once()
        mock_sleep.assert_awaited_once_with(1.5)

    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.base_factory.generate_session_fingerprint"
    )
    def test_get_browser_context_options(self, mock_generate, factory):
        expected_options = {"mock": "data"}
        mock_generate.return_value = expected_options

        result = factory.get_browser_context_options()

        assert result == expected_options
        mock_generate.assert_called_once()

    def test_handle_error_logs_warning(self, factory):
        mock_context = MagicMock()
        mock_context.request.url = "http://test.com"
        error = Exception("Test error")

        async def _run():
            await factory.handle_error(mock_context, error)

        asyncio.run(_run())
        mock_context.log.warning.assert_called_once()
        log_message = mock_context.log.warning.call_args[0][0]
        assert "[DummyCrawlerFactory]" in log_message
        assert "http://test.com" in log_message
        assert "Test error" in log_message

    def test_handle_failed_request_logs_error(self, factory):
        mock_context = MagicMock()
        mock_context.request.url = "http://test.com"
        error = Exception("Fatal error")

        async def _run():
            await factory.handle_failed_request(mock_context, error)

        asyncio.run(_run())
        mock_context.log.error.assert_called_once()
        log_message = mock_context.log.error.call_args[0][0]
        assert "[DummyCrawlerFactory]" in log_message
        assert "http://test.com" in log_message
        assert "Fatal error" in log_message

    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.base_factory.AdaptivePlaywrightCrawler"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.base_factory.RequestQueue.open"
    )
    def test_create_crawler_initialization(self, mock_rq_open, mock_apc, factory):
        mock_rq = AsyncMock()
        mock_rq_open.return_value = mock_rq
        mock_crawler_instance = MagicMock()
        mock_apc.with_beautifulsoup_static_parser.return_value = mock_crawler_instance

        mock_session_factory = MagicMock()
        mock_storage = MagicMock()
        mock_event_manager = MagicMock()

        async def _run():
            return await factory.create_crawler(
                mock_session_factory, mock_storage, mock_event_manager
            )

        crawler = asyncio.run(_run())

        assert mock_rq_open.await_count == 2
        mock_rq.drop.assert_awaited_once()
        mock_apc.with_beautifulsoup_static_parser.assert_called_once()

        mock_crawler_instance.router.default_handler.assert_called_once()
        mock_crawler_instance.error_handler.assert_called_once_with(
            factory.handle_error
        )
        mock_crawler_instance.failed_request_handler.assert_called_once_with(
            factory.handle_failed_request
        )
        assert crawler == mock_crawler_instance

    @pytest.mark.parametrize(
        "max_concurrency_val, expected_desired",
        [
            (1, 1),
            (5, 4),
            (10, 9),
        ],
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.base_factory.AdaptivePlaywrightCrawler"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.base_factory.RequestQueue.open"
    )
    def test_create_crawler_concurrency_settings(
        self,
        mock_rq_open,
        mock_apc,
        max_concurrency_val,
        expected_desired,
        factory,
    ):
        mock_rq = AsyncMock()
        mock_rq_open.return_value = mock_rq
        mock_crawler_instance = MagicMock()
        mock_apc.with_beautifulsoup_static_parser.return_value = mock_crawler_instance

        mock_session_factory = MagicMock()
        mock_storage = MagicMock()
        mock_event_manager = MagicMock()

        with patch(
            "agents.tools.adaptive_crawler.crawler_factory.base_factory.MAX_CONCURRENCY",
            max_concurrency_val,
        ):

            async def _run():
                return await factory.create_crawler(
                    mock_session_factory, mock_storage, mock_event_manager
                )

            asyncio.run(_run())

        mock_apc.with_beautifulsoup_static_parser.assert_called_once()
        kwargs = mock_apc.with_beautifulsoup_static_parser.call_args.kwargs
        concurrency_settings = kwargs["concurrency_settings"]
        assert concurrency_settings.max_concurrency == max_concurrency_val
        assert concurrency_settings.desired_concurrency == expected_desired
