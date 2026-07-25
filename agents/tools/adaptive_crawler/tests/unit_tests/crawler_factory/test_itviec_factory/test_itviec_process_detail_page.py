import json
import pytest
from bs4 import BeautifulSoup
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.enums import JobStatus
from agents.tools.adaptive_crawler.crawler_factory.itviec_factory.itviec_process_detail_page import (
    process_detail_page,
    parse_skills_paragraph,
)


class TestProcessDetailPage:
    def test_parse_skills_paragraph_segregation(self):
        html = """
        <div>
            <strong>Requirements:</strong>
            <ul><li>Python</li><li>Django</li></ul>
            <strong>Nice to have:</strong>
            <ul><li>Docker</li></ul>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div")

        reqs, nice = parse_skills_paragraph(div)

        assert reqs == ["Python", "Django"]
        assert nice == ["Docker"]

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itviec_factory.itviec_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_404_updates_status(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_context.http_response.status_code = 404

        mock_job = MagicMock()
        mock_job.status = JobStatus.OPEN
        mock_repo = MagicMock()
        mock_repo.get_by_url = AsyncMock(return_value=mock_job)
        mock_repo_cls.return_value = mock_repo

        soup = BeautifulSoup("<html></html>", "html.parser")

        await process_detail_page(
            mock_context, soup, "https://itviec.com/job/123", factory
        )

        mock_repo.get_by_url.assert_called_once_with("https://itviec.com/job/123")
        assert mock_job.status == JobStatus.CLOSED
        session.add.assert_called_once_with(mock_job)
        session.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itviec_factory.itviec_process_detail_page.adapter_itviec"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itviec_factory.itviec_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_success_extracts_schema(
        self, mock_repo_cls, mock_adapter, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo

        mock_job = MagicMock()
        mock_job.title = "Software Engineer"
        mock_adapter.return_value = mock_job

        schema = {
            "@type": "JobPosting",
            "title": "Backend Dev",
            "hiringOrganization": {"name": "Tech Corp"},
        }
        html = f"""
        <html>
            <script type="application/ld+json">{json.dumps(schema)}</script>
            <div class="row im-0 ip-0">
                <h1>Backend Dev</h1>
                <a class="text-it-black text-hover-red cursor-pointer" href="/companies/tech-corp">Tech Corp</a>
                <div class="row ipy-2">
                    <div class="text-dark-grey">Company type</div>
                    <div class="col text-end">Product</div>
                </div>
            </div>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://itviec.com/it-jobs/backend-dev-123", factory
        )

        mock_context.add_requests.assert_called_once()
        mock_adapter.assert_called_once()
        raw_data_passed = mock_adapter.call_args[0][0]
        assert raw_data_passed["title"] == "Backend Dev"
        assert raw_data_passed["company"]["type"] == "Product"

        mock_repo.save_or_update.assert_called_once_with(mock_job)
