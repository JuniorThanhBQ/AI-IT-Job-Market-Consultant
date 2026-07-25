import pytest
from unittest.mock import AsyncMock, patch

from agents.tools.adaptive_crawler.crawler_factory.itviec_factory.itviec_factory import (
    ITViecCrawlerFactory,
)


class TestITViecCrawlerFactory:
    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itviec_factory.itviec_factory.process_detail_page"
    )
    async def test_factory_routes_to_detail(
        self, mock_process_detail, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = ITViecCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://itviec.com/it-jobs/python-developer-12345"
        mock_context.request.label = "detail"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(
            return_value=b"<html><h1>Job</h1></html>"
        )

        await handler(mock_context)

        mock_process_detail.assert_called_once()
        assert (
            mock_process_detail.call_args[0][2]
            == "https://itviec.com/it-jobs/python-developer-12345"
        )

    @pytest.mark.asyncio
    async def test_factory_empty_html_returns_early(
        self, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = ITViecCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://itviec.com/it-jobs"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(return_value=b"")

        await handler(mock_context)

        mock_context.log.warning.assert_called_with(
            "Empty HTML content received for URL: https://itviec.com/it-jobs"
        )
