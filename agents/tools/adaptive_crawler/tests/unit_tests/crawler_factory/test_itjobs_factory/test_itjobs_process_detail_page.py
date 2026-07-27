import pytest
from bs4 import BeautifulSoup
from unittest.mock import AsyncMock, MagicMock, patch

from agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_process_detail_page import (
    process_detail_page,
)


class TestProcessDetailPage:
    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_process_detail_page.JobRepository"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_process_detail_page.JobAdapter"
    )
    async def test_process_detail_page_valid_html(
        self, mock_job_adapter, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save = AsyncMock()
        mock_repo_cls.return_value = mock_repo

        mock_job_adapter.to_job.return_value = MagicMock()
        mock_context.request.label = "detail"

        html = """
        <html>
            <div class="jp_company-right">
                <h1>FPT Software</h1>
                <p>Quy mô công ty: 1000+</p>
                <p>Hanoi, Vietnam</p>
            </div>
            <div id="business-profile">
                <div class="jp_skills_slider_wrapper">
                    <h2>Innovate Future</h2>
                    <p>Good company</p>
                </div>
            </div>
            <div class="jp_job_post_detail_cont">
                <h3>Senior Backend Engineer</h3>
                <li><i class="fa-map-marker"></i><span>Hanoi</span></li>
                <li><i class="fa-usd"></i><span>$2000 - $3000</span></li>
                <li><i class="fa-clock-o"></i><span>Full-time</span></li>
                <li><i class="fa-suitcase"></i><span>Senior</span></li>
            </div>
            <div class="jp_job_post_side_img">
                <ul>
                    <i class="fa-list-alt"></i><span>Outsource</span>
                </ul>
            </div>
            <div class="job-description-section">
                <div class="jp_overview_wrapper">Develop backend systems</div>
            </div>
            <div class="job-requirement-section">
                <div class="jp_overview_wrapper">5+ years in Python</div>
            </div>
            <div class="jp_job_post_keyword_wrapper">
                <a>Python,</a><a>Docker</a>
            </div>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://itjobs.com.vn/job/1", factory
        )

        mock_job_adapter.to_job.assert_called_once()
        raw_data = mock_job_adapter.to_job.call_args[0][0]

        assert raw_data["title"] == "Senior Backend Engineer"
        assert raw_data["company"] == "FPT Software"
        assert raw_data["company_size"] == "1000+"
        assert raw_data["salary"] == "$2000 - $3000"
        assert raw_data["company_type"] == "Outsource"
        assert raw_data["skills"] == ["Python", "Docker"]

        mock_repo.save.assert_called_once()
        session.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_updater_not_found_closes_job(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_context.request.label = "updater_detail"
        mock_context.http_response.status_code = 404
        mock_context._page = None

        mock_job = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_by_url = AsyncMock(return_value=mock_job)
        mock_repo_cls.return_value = mock_repo

        soup = BeautifulSoup("<html></html>", "html.parser")

        await process_detail_page(
            mock_context, soup, "https://itjobs.com.vn/job/99", factory
        )

        mock_repo.get_by_url.assert_called_once_with("https://itjobs.com.vn/job/99")
        assert mock_job.status == "Closed"
        session.add.assert_called_once_with(mock_job)
        session.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itjobs_factory.itjobs_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_updater_expired_text_closes_job(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_context.request.label = "updater_detail"
        mock_context.http_response.status_code = 200
        mock_context._page = None

        mock_job = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_by_url = AsyncMock(return_value=mock_job)
        mock_repo_cls.return_value = mock_repo

        soup = BeautifulSoup("<html><body>Hết hạn</body></html>", "html.parser")

        await process_detail_page(
            mock_context, soup, "https://itjobs.com.vn/job/99", factory
        )

        mock_repo.get_by_url.assert_called_once()
        assert mock_job.status == "Closed"

    @pytest.mark.asyncio
    async def test_process_detail_page_updater_empty_extraction_skips(
        self, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_context.request.label = "updater_detail"
        mock_context.http_response.status_code = 200
        mock_context._page = None

        html = """<html><div class="jp_company-right"></div></html>"""
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://itjobs.com.vn/job/88", factory
        )

        mock_context.log.warning.assert_called_with(
            "New parsed data is null/empty for URL https://itjobs.com.vn/job/88 due to extraction error. Keeping old record."
        )
