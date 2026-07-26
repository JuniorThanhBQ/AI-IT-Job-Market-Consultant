import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from bs4 import BeautifulSoup

from agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_company_page import (
    process_company_page,
)


class TestTopDevProcessCompanyPage:
    @pytest.mark.asyncio
    async def test_process_company_page_missing_name(
        self, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        html = "<html><body>No name span here</body></html>"
        soup = BeautifulSoup(html, "html.parser")

        await process_company_page(
            mock_context, soup, "https://topdev.vn/companies/ghost", factory
        )

        mock_context.log.warning.assert_called_with(
            "Company profile has no name: https://topdev.vn/companies/ghost"
        )

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_company_page.CompanyRepository"
    )
    async def test_process_company_page_full_extraction(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo

        html = """
        <html>
            <body>
                <span class="block text-xl font-semibold">Tech Corp</span>
                <div>
                   <span class="flex text-sm text-text-400">
                      <svg></svg>
                      Ho Chi Minh City
                   </span>
                </div>
                <div>
                   <span>Country</span>
                   <span class="font-semibold text-text-700">Vietnam</span>
                </div>
                <div>
                   <span>Industry</span>
                   <span class="font-semibold text-text-700">IT</span>
                   <span class="font-semibold text-text-700">Software</span>
                </div>
                <div>
                   <span>Size</span>
                   <span class="font-semibold text-text-700">100-500</span>
                </div>
                <div>
                   <span>Company overview</span>
                   <div class="text-gray-700">
                      <p>We build software.</p>
                      <p>For everyone.</p>
                   </div>
                </div>
                <div>
                   <span>Benefits</span>
                   <ul>
                      <li>Free snacks</li>
                      <li>Health insurance</li>
                   </ul>
                </div>
                <a href="https://techcorp.com">
                   <span>Company Website</span>
                </a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_company_page(
            mock_context, soup, "https://topdev.vn/companies/tech-corp", factory
        )

        mock_repo.save_or_update.assert_awaited_once()
        saved_company = mock_repo.save_or_update.call_args[0][0]

        assert saved_company.name == "Tech Corp"
        assert saved_company.location == "Ho Chi Minh City"
        assert saved_company.country == "Vietnam"
        assert saved_company.industry == "IT, Software"
        assert saved_company.size == "100-500"
        assert saved_company.description == "We build software.\n\nFor everyone."
        assert len(saved_company.benefits) == 2
        assert saved_company.benefits[0].name == "Free snacks"
        assert saved_company.benefits[1].name == "Health insurance"
        assert saved_company.website == "https://techcorp.com"

        session.commit.assert_awaited_once()
        mock_context.log.info.assert_any_call(
            "Successfully saved company information for: Tech Corp"
        )

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_company_page.CompanyRepository"
    )
    async def test_process_company_page_description_without_paragraphs(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo

        html = """
        <html>
            <body>
                <span class="block text-xl font-semibold">Basic Corp</span>
                <div>
                   <span>Company overview</span>
                   <div class="text-gray-700">
                      Simple description text without p tags.
                   </div>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_company_page(
            mock_context, soup, "https://topdev.vn/companies/basic-corp", factory
        )

        saved_company = mock_repo.save_or_update.call_args[0][0]
        assert saved_company.description == "Simple description text without p tags."

    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.topdev_factory.topdev_process_company_page.CompanyRepository"
    )
    async def test_process_company_page_partial_missing_data(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo

        html = """
        <html>
            <body>
                <span class="block text-xl font-semibold">Minimal Corp</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_company_page(
            mock_context, soup, "https://topdev.vn/companies/minimal-corp", factory
        )

        saved_company = mock_repo.save_or_update.call_args[0][0]

        assert saved_company.name == "Minimal Corp"
        assert saved_company.location == "Vietnam"
        assert saved_company.country == "Unknown"
        assert saved_company.industry == "Unknown"
        assert saved_company.size == "Unknown"
        assert saved_company.description == ""
        assert len(saved_company.benefits) == 0
        assert saved_company.website == ""
