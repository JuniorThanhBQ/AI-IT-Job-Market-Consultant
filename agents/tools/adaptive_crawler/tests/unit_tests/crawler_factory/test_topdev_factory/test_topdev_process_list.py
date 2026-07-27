import pytest
from bs4 import BeautifulSoup

from agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_list_page import (
    process_list_page,
)


class TestTopDevProcessListPage:
    @pytest.mark.asyncio
    async def test_process_list_page_enqueues_details_and_next_page(self, mock_context):
        html = """
        <html>
            <head>
                <title>Recruiting 163 positions for Software Developer [Update 25/7/2026].</title>
            </head>
            <body>
                <a class="line-clamp-3" href="/detail-jobs/backend-engineer-1">Backend Engineer 1</a>
                <a class="line-clamp-3" href="/detail-jobs/frontend-engineer-2">Frontend Engineer 2</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_list_page(mock_context, soup, "https://topdev.vn/jobs?page=1")

        # 2 detail pages + 1 next page (pagination) = 3 calls
        assert mock_context.add_requests.call_count == 3

        call_args_list = mock_context.add_requests.call_args_list
        # Check details
        reqs_0 = call_args_list[0][0][0]
        assert reqs_0[0].url == "https://topdev.vn/detail-jobs/backend-engineer-1"
        assert reqs_0[0].label == "detail"

        reqs_1 = call_args_list[1][0][0]
        assert reqs_1[0].url == "https://topdev.vn/detail-jobs/frontend-engineer-2"
        assert reqs_1[0].label == "detail"

        # Check pagination: 163 jobs / 2 enqueued = 82 pages. Current page 1 < 82, so page 2 enqueued.
        reqs_pagination = call_args_list[2][0][0]
        assert "page=2" in reqs_pagination[0].url
        assert reqs_pagination[0].label == "list"

    @pytest.mark.asyncio
    async def test_process_list_page_does_not_enqueue_beyond_max_page(
        self, mock_context
    ):
        html = """
        <html>
            <head>
                <title>Recruiting 163 positions for Software Developer [Update 25/7/2026].</title>
            </head>
            <body>
                <a class="line-clamp-3" href="/detail-jobs/backend-engineer-1">Backend Engineer 1</a>
                <a class="line-clamp-3" href="/detail-jobs/frontend-engineer-2">Frontend Engineer 2</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        # Since total_jobs = 163 and enqueued = 2, max_page = 82.
        # If current page is 82, we should not enqueue page 83.
        await process_list_page(mock_context, soup, "https://topdev.vn/jobs?page=82")

        # Only the 2 detail page calls, no next page enqueued.
        assert mock_context.add_requests.call_count == 2

    @pytest.mark.asyncio
    async def test_process_list_page_fallback_to_default_max_page(self, mock_context):
        # Title doesn't match Recruiting pattern
        html = """
        <html>
            <head>
                <title>Jobs in Vietnam</title>
            </head>
            <body>
                <a class="line-clamp-3" href="/detail-jobs/backend-engineer-1">Backend Engineer 1</a>
                <a class="line-clamp-3" href="/detail-jobs/frontend-engineer-2">Frontend Engineer 2</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        # Default max_page is 15. If page=14, we should enqueue page 15.
        await process_list_page(mock_context, soup, "https://topdev.vn/jobs?page=14")
        assert mock_context.add_requests.call_count == 3
        call_args_list = mock_context.add_requests.call_args_list
        reqs_pagination = call_args_list[2][0][0]
        assert "page=15" in reqs_pagination[0].url

        # Reset mock
        mock_context.add_requests.reset_mock()

        # If page=15, we should NOT enqueue page 16 (since 15 is max_page fallback).
        await process_list_page(mock_context, soup, "https://topdev.vn/jobs?page=15")
        assert mock_context.add_requests.call_count == 2
