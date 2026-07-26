import pytest
from unittest.mock import AsyncMock, patch

from agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory import (
    TopDevCrawlerFactory,
)


class TestTopDevCrawlerFactory:
    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.TopDevCrawlerFactory.apply_delay",
        new_callable=AsyncMock,
    )
    async def test_factory_empty_html_returns_early(
        self, mock_apply_delay, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = TopDevCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://topdev.vn/it-jobs"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(return_value=b"")

        await handler(mock_context)

        mock_context.log.warning.assert_called_with(
            "Empty content for URL: https://topdev.vn/it-jobs"
        )

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.process_detail_page"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.TopDevCrawlerFactory.apply_delay",
        new_callable=AsyncMock,
    )
    async def test_factory_routes_to_detail(
        self, mock_apply_delay, mock_process_detail, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = TopDevCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://topdev.vn/detail-jobs/python-developer-123"
        mock_context.request.label = "detail"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(
            return_value=b"<html><h1>Job Detail</h1></html>"
        )

        await handler(mock_context)

        mock_process_detail.assert_called_once()
        assert (
            mock_process_detail.call_args[0][2]
            == "https://topdev.vn/detail-jobs/python-developer-123"
        )

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.process_company_page"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.TopDevCrawlerFactory.apply_delay",
        new_callable=AsyncMock,
    )
    async def test_factory_routes_to_company(
        self, mock_apply_delay, mock_process_company, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = TopDevCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://topdev.vn/companies/tech-corp"
        mock_context.request.label = "company"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(
            return_value=b"<html><h1>Company</h1></html>"
        )

        await handler(mock_context)

        mock_process_company.assert_called_once()
        assert (
            mock_process_company.call_args[0][2]
            == "https://topdev.vn/companies/tech-corp"
        )

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.process_list_page"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.TopDevCrawlerFactory.apply_delay",
        new_callable=AsyncMock,
    )
    async def test_factory_routes_to_list(
        self, mock_apply_delay, mock_process_list, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = TopDevCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://topdev.vn/it-jobs"
        mock_context.request.label = "list"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(
            return_value=b"<html><h1>List</h1></html>"
        )

        await handler(mock_context)

        mock_process_list.assert_called_once()
        assert mock_process_list.call_args[0][2] == "https://topdev.vn/it-jobs"

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.process_detail_page"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.TopDevCrawlerFactory.apply_delay",
        new_callable=AsyncMock,
    )
    async def test_factory_with_playwright_page_waits_for_networkidle(
        self, mock_apply_delay, mock_process_detail, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = TopDevCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://topdev.vn/detail-jobs/python-developer-123"
        mock_context.request.label = "detail"

        mock_page = AsyncMock()
        mock_page.content = AsyncMock(
            side_effect=[
                "<html><body>Loading...</body></html>",
                "<html><body>Fully Loaded Data</body></html>",
            ]
        )
        mock_page.wait_for_load_state = AsyncMock()

        mock_context._page = True
        mock_context.page = mock_page

        await handler(mock_context)

        mock_page.wait_for_load_state.assert_awaited_once_with(
            "networkidle", timeout=15000
        )
        assert mock_page.content.call_count == 2
        mock_process_detail.assert_called_once()

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.process_detail_page"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_factory.TopDevCrawlerFactory.apply_delay",
        new_callable=AsyncMock,
    )
    async def test_factory_with_playwright_page_handles_timeout_error(
        self, mock_apply_delay, mock_process_detail, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = TopDevCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://topdev.vn/detail-jobs/python-developer-123"
        mock_context.request.label = "detail"

        mock_page = AsyncMock()
        mock_page.content = AsyncMock(
            return_value="<html><body>Initial Data</body></html>"
        )
        mock_page.wait_for_load_state = AsyncMock(
            side_effect=Exception("Timeout exceeded")
        )

        mock_context._page = True
        mock_context.page = mock_page

        await handler(mock_context)

        mock_page.wait_for_load_state.assert_awaited_once_with(
            "networkidle", timeout=15000
        )
        assert mock_page.content.call_count == 1
        mock_context.log.warning.assert_called_with(
            "Timeout/Error waiting for page load, falling back to initial HTML: Timeout exceeded"
        )
        mock_process_detail.assert_called_once()
