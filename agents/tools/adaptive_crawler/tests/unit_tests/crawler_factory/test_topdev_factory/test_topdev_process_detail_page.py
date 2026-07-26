import json
import pytest
from bs4 import BeautifulSoup
from unittest.mock import AsyncMock, MagicMock, patch

from agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page import (
    process_detail_page,
)


class TestTopDevProcessDetailPage:
    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobAdapter"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_valid_json_ld(
        self, mock_repo_cls, mock_adapter, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo
        mock_adapter.to_job.return_value = MagicMock()

        ld_json = {
            "@context": "http://schema.org",
            "@type": "JobPosting",
            "title": "Senior Data Engineer",
            "hiringOrganization": {"name": "DataCorp"},
            "skills": ["Python", "Spark", "SQL"],
            "jobLocation": [{"address": {"addressRegion": "Hanoi"}}],
            "baseSalary": {"value": {"value": "2000 USD"}},
            "validThrough": "2026-12-31T00:00:00",
            "description": "<div><strong>Great Job</strong></div>",
            "jobBenefits": ["Health Care", "Free Lunch"],
        }

        html = f"""
        <html>
            <head>
                <script type="application/ld+json">{json.dumps(ld_json)}</script>
            </head>
            <body></body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://topdev.vn/detail-jobs/data-1", factory
        )

        mock_repo.save_or_update.assert_awaited_once()
        raw_data = mock_adapter.to_job.call_args[0][0]

        assert raw_data["title"] == "Senior Data Engineer"
        assert raw_data["company"] == "DataCorp"
        assert raw_data["skills"] == ["Python", "Spark", "SQL"]
        assert raw_data["location"] == "Hanoi"
        assert raw_data["salary"] == "2000 USD"
        assert raw_data["job_overview"]["valid_through"] == "2026-12-31T00:00:00"
        assert raw_data["description"] == "Great Job"
        assert raw_data["benefits"] == ["Health Care", "Free Lunch"]

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobAdapter"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_missing_title_aborts(
        self, mock_repo_cls, mock_adapter, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        html = """
        <html>
            <body>
                <div class="job-description">We are hiring but forgot the title!</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://topdev.vn/detail-jobs/no-title", factory
        )

        mock_context.log.warning.assert_called_once()
        mock_adapter.to_job.assert_not_called()

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobAdapter"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_missing_description_aborts(
        self, mock_repo_cls, mock_adapter, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        html = """
        <html>
            <body>
                <h1>Software Engineer</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://topdev.vn/detail-jobs/no-desc", factory
        )

        mock_context.log.warning.assert_called_once()
        mock_adapter.to_job.assert_not_called()

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobAdapter"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_extracts_industry_successful(
        self, mock_repo_cls, mock_adapter, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo
        mock_adapter.to_job.return_value = MagicMock()

        html = """
        <html>
            <body>
                <h1>Backend Developer</h1>
                <div class="font-sans relative h-fit">
                    <a href="/companies/tech-corp">
                        <span class="text-brand-500 font-semibold">Tech Corp</span>
                    </a>
                    <div class="flex items-center justify-between gap-1">
                        <span class="text-sm text-text-700">Industry</span>
                        <span class="text-sm font-semibold text-text-700">Sản xuất</span>
                    </div>
                    <div class="flex items-center justify-between gap-1">
                        <span class="text-sm text-text-700">Size</span>
                        <span class="text-sm font-semibold text-text-700">100-499 Employees</span>
                    </div>
                </div>
                <div class="job-description">We are hiring!</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://topdev.vn/detail-jobs/backend-1", factory
        )

        mock_context.add_requests.assert_awaited_once()
        reqs = mock_context.add_requests.call_args[0][0]
        assert reqs[0].url == "https://topdev.vn/companies/tech-corp"
        assert reqs[0].label == "company"

        mock_repo.save_or_update.assert_awaited_once()
        raw_data = mock_adapter.to_job.call_args[0][0]
        assert raw_data["title"] == "Backend Developer"
        assert raw_data["company"] == "Tech Corp"
        assert raw_data["company_industry"] == "Sản xuất"
        assert raw_data["company_size"] == "100-499"
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobAdapter"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_graceful_if_no_company_link(
        self, mock_repo_cls, mock_adapter, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo
        mock_adapter.to_job.return_value = MagicMock()

        html = """
        <html>
            <body>
                <h1>Backend Developer</h1>
                <div class="job-description">We are hiring!</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://topdev.vn/detail-jobs/backend-2", factory
        )

        mock_context.add_requests.assert_not_awaited()
        raw_data = mock_adapter.to_job.call_args[0][0]
        assert raw_data["company"] == "Unknown Company"

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobAdapter"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_complex_roles_and_vietnamese_nice_to_have(
        self, mock_repo_cls, mock_adapter, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo
        mock_adapter.to_job.return_value = MagicMock()

        html = """
        <html>
            <body>
                <h1>Business Analyst</h1>
                <div class="job-description">We are hiring!</div>

                <span class="flex items-center gap-1 font-semibold text-[#3659B3]">
                    <div class="inline-flex">1</div>Your role & responsibilities
                </span>
                <div class="mt-2">
                    <div class="prose-ul">
                        <p><strong>1. Junior</strong></p>
                        <ul>
                            <li>Nắm vững tính năng phần mềm.</li>
                            <li>Nghiên cứu thị trường.</li>
                        </ul>
                    </div>
                </div>

                <span class="mt-4 flex items-center gap-1 font-semibold text-[#3659B3]">
                    <div class="inline-flex">2</div>Your skills & qualifications
                </span>
                <div class="mt-2">
                    <div class="prose-ul text-text-900 bg-[#F5F5F5] px-2 py-4 text-sm">
                        <p><strong>Yêu cầu bắt buộc</strong></p>
                        <ul>
                            <li>Từ 2 năm kinh nghiệm BA.</li>
                        </ul>
                        <p><strong>Điểm cộng lớn</strong></p>
                        <ul>
                            <li>Đã từng làm sản phẩm ERP.</li>
                        </ul>
                    </div>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://topdev.vn/detail-jobs/ba-1", factory
        )

        raw_data = mock_adapter.to_job.call_args[0][0]

        assert len(raw_data["responsibilities"]) == 2
        assert raw_data["responsibilities"][0] == "Nắm vững tính năng phần mềm."
        assert raw_data["responsibilities"][1] == "Nghiên cứu thị trường."

        assert "Từ 2 năm kinh nghiệm BA." in raw_data["requirements"]
        assert "Đã từng làm sản phẩm ERP." not in raw_data["requirements"]

        assert len(raw_data["nice_to_have"]) == 1
        assert raw_data["nice_to_have"][0] == "Đã từng làm sản phẩm ERP."

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobAdapter"
    )
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_nice_to_have_header_fallback(
        self, mock_repo_cls, mock_adapter, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo
        mock_adapter.to_job.return_value = MagicMock()

        html = """
        <html>
            <body>
                <h1>DevOps Engineer</h1>
                <div class="job-description">Join our infra team.</div>
                <div>
                    <span class="font-bold">Nice to have:</span>
                    <ul>
                        <li>Kubernetes certification</li>
                        <li>AWS solutions architect</li>
                    </ul>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_detail_page(
            mock_context, soup, "https://topdev.vn/detail-jobs/devops-1", factory
        )

        raw_data = mock_adapter.to_job.call_args[0][0]
        assert len(raw_data["nice_to_have"]) == 2
        assert raw_data["nice_to_have"][0] == "Kubernetes certification"
        assert raw_data["nice_to_have"][1] == "AWS solutions architect"

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_updater_marks_closed_on_404(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_existing_job = MagicMock()
        mock_repo.get_by_url = AsyncMock(return_value=mock_existing_job)

        mock_context.request.label = "updater_detail"
        mock_context.http_response.status_code = 404
        mock_context._page = None

        soup = BeautifulSoup("<html></html>", "html.parser")
        url = "https://topdev.vn/detail-jobs/expired-1"

        await process_detail_page(mock_context, soup, url, factory)

        mock_repo.get_by_url.assert_awaited_once_with(url)
        assert mock_existing_job.status == "Closed"
        session.add.assert_called_once_with(mock_existing_job)
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_updater_marks_closed_on_expired_text(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_existing_job = MagicMock()
        mock_repo.get_by_url = AsyncMock(return_value=mock_existing_job)

        mock_context.request.label = "updater_detail"
        mock_context.http_response.status_code = 200
        mock_context._page = None

        html = (
            "<html><body><h1>Tin tuyển dụng này đã ngưng nhận hồ sơ</h1></body></html>"
        )
        soup = BeautifulSoup(html, "html.parser")
        url = "https://topdev.vn/detail-jobs/expired-2"

        await process_detail_page(mock_context, soup, url, factory)

        mock_repo.get_by_url.assert_awaited_once_with(url)
        assert mock_existing_job.status == "Closed"
        session.add.assert_called_once_with(mock_existing_job)
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_detail_page.JobRepository"
    )
    async def test_process_detail_page_updater_marks_closed_on_url_redirect(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_existing_job = MagicMock()
        mock_repo.get_by_url = AsyncMock(return_value=mock_existing_job)

        mock_context.request.label = "updater_detail"
        mock_context.http_response.status_code = 200
        mock_context._page = True

        mock_page = MagicMock()
        mock_page.url = "https://topdev.vn/"
        mock_context.page = mock_page

        html = "<html><body>Trang chủ TopDev</body></html>"
        soup = BeautifulSoup(html, "html.parser")
        url = "https://topdev.vn/detail-jobs/expired-3"

        await process_detail_page(mock_context, soup, url, factory)

        mock_repo.get_by_url.assert_awaited_once_with(url)
        assert mock_existing_job.status == "Closed"
        session.add.assert_called_once_with(mock_existing_job)
        session.commit.assert_awaited_once()
