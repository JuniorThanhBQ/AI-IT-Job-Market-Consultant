import pytest
from bs4 import BeautifulSoup

from agents.tools.adaptive_crawler.crawler_factory.itviec_factory.itviec_process_list_page import (
    process_list_page,
)


class TestProcessListPage:
    @pytest.mark.asyncio
    async def test_process_list_page_enqueues_details_and_next_page(self, mock_context):
        html = """
        <html>
            <h1>100 IT Jobs</h1>
            <h3 data-search--job-selection-target='jobTitle'>
                <a href="/it-jobs/backend-engineer-123">Backend Engineer</a>
            </h3>
            <h3 data-search--job-selection-target='jobTitle'>
                <a href="/it-jobs/frontend-engineer-456?utm=abc">Frontend Engineer</a>
            </h3>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_list_page(mock_context, soup, "https://itviec.com/it-jobs?page=1")

        assert mock_context.add_requests.call_count == 3

        call_args_list = mock_context.add_requests.call_args_list
        reqs_0 = call_args_list[0][0][0]
        assert reqs_0[0].url == "https://itviec.com/it-jobs/backend-engineer-123"
        assert reqs_0[0].label == "detail"

        reqs_pagination = call_args_list[2][0][0]
        assert "page=2" in reqs_pagination[0].url
        assert reqs_pagination[0].label == "list"
