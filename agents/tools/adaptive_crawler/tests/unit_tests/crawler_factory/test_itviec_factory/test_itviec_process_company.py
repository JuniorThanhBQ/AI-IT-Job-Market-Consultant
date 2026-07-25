import pytest
from bs4 import BeautifulSoup
from unittest.mock import AsyncMock, MagicMock, patch

from app.modules.company.models import Company
from agents.tools.adaptive_crawler.crawler_factory.itviec_factory.itviec_process_company_page import (
    process_company_page,
)


class TestProcessCompanyPage:
    @pytest.mark.asyncio
    @patch(
        "agents.tools.adaptive_crawler.crawler_factory.itviec_factory.itviec_process_company_page.CompanyRepository"
    )
    async def test_process_company_page_success(
        self, mock_repo_cls, mock_context, mock_session_factory
    ):
        factory, session = mock_session_factory
        mock_repo = MagicMock()
        mock_repo.save_or_update = AsyncMock()
        mock_repo_cls.return_value = mock_repo

        html = """
        <html>
            <h1>Tech Giant Vietnam</h1>
            <div>
                <h2>General information</h2>
                <div>
                    <div class="row">
                        <div class="normal-text">Company type</div>
                        <div class="normal-text">Product</div>
                    </div>
                    <div class="row">
                        <div class="normal-text">Company industry</div>
                        <div>Software</div>
                    </div>
                </div>
            </div>
            <h2 class="title">Company overview</h2>
            <div class="paragraph">
                Great Slogan
                We build awesome software.
            </div>
            <h2>You will love working here</h2>
            <ul><li>Free lunch</li><li>Health care</li></ul>
            <div class="location"><span class="text-break">Ho Chi Minh</span></div>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")

        await process_company_page(
            mock_context, soup, "https://itviec.com/companies/tech-giant", factory
        )

        mock_repo.save_or_update.assert_called_once()
        saved_company = mock_repo.save_or_update.call_args[0][0]
        assert isinstance(saved_company, Company)
        assert saved_company.name == "Tech Giant Vietnam"
        assert saved_company.industry == "Software"
        assert saved_company.slogan == "Great Slogan"
        assert saved_company.description == "We build awesome software."
        assert saved_company.location == "Ho Chi Minh"
        assert len(saved_company.benefits) == 2
        assert saved_company.benefits[0].name == "Free lunch"

    @pytest.mark.asyncio
    async def test_process_company_page_missing_name(
        self, mock_context, mock_session_factory
    ):
        factory, _ = mock_session_factory
        html = "<html><body>No header here</body></html>"
        soup = BeautifulSoup(html, "html.parser")

        await process_company_page(
            mock_context, soup, "https://itviec.com/companies/ghost", factory
        )

        mock_context.log.warning.assert_called_with(
            "No company name found at URL: https://itviec.com/companies/ghost"
        )
        factory.assert_not_called()
