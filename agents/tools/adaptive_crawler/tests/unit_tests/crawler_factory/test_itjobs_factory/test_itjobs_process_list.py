import pytest
from bs4 import BeautifulSoup
from unittest.mock import AsyncMock

from agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_process_list_page import (
    process_list_page,
)


class TestProcessListPage:
    @pytest.mark.asyncio
    async def test_process_list_page_valid_anchors_enqueued(self, mock_context):
        mock_context._page = None
        html = """
        <html>
            <a class="jp_job_post_link" href="/job/backend-engineer-1">Backend</a>
            <a class="top-jobs__item" href="/job/frontend-engineer-2">Frontend</a>
            <a class="other" href="/companies">Companies</a>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_list_page(mock_context, soup, "https://itjobs.com.vn/search")

        assert mock_context.add_requests.call_count == 2
        calls = mock_context.add_requests.call_args_list

        req_1 = calls[0][0][0][0]
        assert req_1.url == "https://itjobs.com.vn/job/backend-engineer-1"
        assert req_1.label == "detail"

        req_2 = calls[1][0][0][0]
        assert req_2.url == "https://itjobs.com.vn/job/frontend-engineer-2"
        assert req_2.label == "detail"

    @pytest.mark.asyncio
    async def test_process_list_page_clicks_show_more_button(self, mock_context):
        mock_button = AsyncMock()
        mock_button.is_visible.return_value = True

        async def query_selector_mock(selector):
            if query_selector_mock.call_count < 2:
                query_selector_mock.call_count += 1
                return mock_button
            return None

        query_selector_mock.call_count = 0
        mock_context.page.query_selector = query_selector_mock

        mock_context.page.content = AsyncMock(
            return_value="""<html><a class="jp_job_post_link" href="/job/123">Job 123</a></html>"""
        )

        await process_list_page(
            mock_context,
            BeautifulSoup("", "html.parser"),
            "https://itjobs.com.vn/search",
        )

        assert mock_button.click.call_count == 2
        mock_context.page.content.assert_called_once()
        mock_context.add_requests.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_list_page_invalid_button_click_handled_gracefully(
        self, mock_context
    ):
        mock_context.page.query_selector.side_effect = Exception("Browser timeout")
        mock_context.page.content = AsyncMock(return_value="<html></html>")

        await process_list_page(
            mock_context,
            BeautifulSoup("", "html.parser"),
            "https://itjobs.com.vn/search",
        )

        mock_context.log.warning.assert_called_with(
            "Failed to click show more button: Browser timeout"
        )
        mock_context.add_requests.assert_not_called()
