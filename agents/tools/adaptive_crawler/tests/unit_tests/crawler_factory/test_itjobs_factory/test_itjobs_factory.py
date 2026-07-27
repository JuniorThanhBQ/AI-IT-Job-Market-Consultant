import pytest
from unittest.mock import AsyncMock, patch

from agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_factory import (
    ITJobsCrawlerFactory,
)


class TestITJobsCrawlerFactory:
    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_factory.process_detail_page"
    )
    async def test_factory_routes_to_detail(
        self, mock_process_detail, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = ITJobsCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://itjobs.com.vn/job/python-dev-1"
        mock_context.request.label = "detail"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(
            return_value=b"<html><h1>Job</h1></html>"
        )

        await handler(mock_context)

        mock_process_detail.assert_called_once()
        assert (
            mock_process_detail.call_args[0][2]
            == "https://itjobs.com.vn/job/python-dev-1"
        )

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_factory.process_company_page"
    )
    async def test_factory_routes_to_company(
        self, mock_process_company, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = ITJobsCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://itjobs.com.vn/company/tech-corp"
        mock_context.request.label = "company"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(
            return_value=b"<html><h1>Company</h1></html>"
        )

        await handler(mock_context)

        mock_process_company.assert_called_once()
        assert (
            mock_process_company.call_args[0][2]
            == "https://itjobs.com.vn/company/tech-corp"
        )

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_factory.process_list_page"
    )
    async def test_factory_routes_to_list(
        self, mock_process_list, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = ITJobsCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://itjobs.com.vn/search"
        mock_context.request.label = "list"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(
            return_value=b"<html><ul>Jobs</ul></html>"
        )

        await handler(mock_context)

        mock_process_list.assert_called_once()
        assert mock_process_list.call_args[0][2] == "https://itjobs.com.vn/search"

    @pytest.mark.asyncio
    async def test_factory_empty_html_returns_early(
        self, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        crawler_factory = ITJobsCrawlerFactory()
        handler = crawler_factory.get_handler(factory)

        mock_context.request.url = "https://itjobs.com.vn"
        mock_context._page = None
        mock_context.http_response.read = AsyncMock(return_value=b"")

        await handler(mock_context)

        mock_context.log.warning.assert_called_with(
            "Empty content for URL: https://itjobs.com.vn"
        )
