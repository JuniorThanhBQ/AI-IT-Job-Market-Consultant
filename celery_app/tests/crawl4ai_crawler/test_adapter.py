from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from tools.crawl4ai_crawler.adapter import (
    crawl4ai_adapter,
    crawl4ai_adapter_company,
)


class TestCompanyAdapter:
    @patch("tools.crawl4ai_crawler.adapter.map_company_type", return_value="Product")
    @patch("tools.crawl4ai_crawler.adapter.map_country", return_value="Vietnam")
    @patch(
        "tools.crawl4ai_crawler.adapter.JobAdapterBase.build_company_vector_context",
        return_value="company_vector",
    )
    def test_company_adapter_empty_data(self, mock_vector, mock_country, mock_type):
        raw_data = {}
        company = crawl4ai_adapter_company(raw_data)

        assert company.name == "Unknown Company"
        assert company.location == "Vietnam"
        assert company.industry == "Information Technology"
        assert company.benefits == []
        assert company.vector_context == "company_vector"

    @patch(
        "tools.crawl4ai_crawler.adapter.map_company_type", return_value="Outsourcing"
    )
    @patch("tools.crawl4ai_crawler.adapter.map_country", return_value="Vietnam")
    @patch(
        "tools.crawl4ai_crawler.adapter.parse_to_list",
        side_effect=[["Benefit 1", "Benefit 2"]],
    )
    @patch(
        "tools.crawl4ai_crawler.adapter.clean_html_text",
        side_effect=lambda x: x.strip(),
    )
    @patch("tools.crawl4ai_crawler.adapter.JobAdapterBase.build_company_vector_context")
    def test_company_adapter_with_list_benefits(
        self, mock_vector, mock_clean, mock_parse, mock_country, mock_type
    ):
        raw_data = {
            "company_name": " Test Corp ",
            "location": " Hanoi ",
            "benefits": ["Benefit 1", "Benefit 2"],
        }

        company = crawl4ai_adapter_company(raw_data)

        assert company.name == "Test Corp"
        assert company.location == "Hanoi"
        assert company.benefits == ["Benefit 1", "Benefit 2"]
        mock_parse.assert_called_once_with(["Benefit 1", "Benefit 2"])

    @patch("tools.crawl4ai_crawler.adapter.map_company_type", return_value="Product")
    @patch("tools.crawl4ai_crawler.adapter.map_country", return_value="Vietnam")
    @patch(
        "tools.crawl4ai_crawler.adapter.parse_to_list", side_effect=[["Benefit String"]]
    )
    @patch(
        "tools.crawl4ai_crawler.adapter.clean_html_text",
        side_effect=lambda x: x.strip(),
    )
    @patch("tools.crawl4ai_crawler.adapter.JobAdapterBase.build_company_vector_context")
    def test_company_adapter_with_string_benefits(
        self, mock_vector, mock_clean, mock_parse, mock_country, mock_type
    ):
        raw_data = {"benefits": "Benefit String"}

        company = crawl4ai_adapter_company(raw_data)

        assert company.benefits == ["Benefit String"]
        mock_parse.assert_called_once_with("Benefit String")


class TestJobAdapter:
    @patch("tools.crawl4ai_crawler.adapter.datetime")
    @patch("tools.crawl4ai_crawler.adapter.crawl4ai_adapter_company")
    @patch("tools.crawl4ai_crawler.adapter.JobAdapterBase")
    @patch(
        "tools.crawl4ai_crawler.adapter.process_job_vector_context",
        return_value="job_vector",
    )
    @patch("tools.crawl4ai_crawler.adapter.map_currency", return_value="USD")
    @patch("tools.crawl4ai_crawler.adapter.map_seniority_level", return_value="Junior")
    @patch("tools.crawl4ai_crawler.adapter.map_working_model", return_value="On-site")
    @patch("tools.crawl4ai_crawler.adapter.map_working_hours", return_value="Full-time")
    @patch(
        "tools.crawl4ai_crawler.adapter.clean_html_text",
        side_effect=lambda x: str(x).strip() if x else "",
    )
    @patch("tools.crawl4ai_crawler.adapter.parse_to_list", return_value=[])
    def test_job_adapter_empty_data(
        self,
        mock_parse,
        mock_clean,
        mock_hours,
        mock_model,
        mock_seniority,
        mock_currency,
        mock_vector,
        mock_base,
        mock_company_adapter,
        mock_dt,
    ):
        mock_dt.now.return_value = datetime(2023, 1, 1, tzinfo=UTC)
        mock_base.parse_salary.return_value = (0, 0, "Thỏa Thuận")
        mock_base.process_skills.return_value = []
        mock_base.calculate_content_hash.return_value = "hash123"
        mock_company_mock = MagicMock()
        mock_company_mock.name = "Unknown Company"
        mock_company_adapter.return_value = mock_company_mock

        mock_job_instance = MagicMock()
        mock_base.build_job.return_value = mock_job_instance

        raw_data = {}
        source_url = "http://source.com"

        result = crawl4ai_adapter(raw_data, source_url)

        assert result == mock_job_instance
        mock_base.parse_salary.assert_called_once_with("Thỏa Thuận")
        build_job_kwargs = mock_base.build_job.call_args[1]
        assert build_job_kwargs["title"] == "Unknown Title"
        assert build_job_kwargs["url"] == "http://source.com"
        assert build_job_kwargs["expired_date"] == datetime(2023, 1, 31)

    @patch("tools.crawl4ai_crawler.adapter.datetime")
    @patch("tools.crawl4ai_crawler.adapter.crawl4ai_adapter_company")
    @patch("tools.crawl4ai_crawler.adapter.JobAdapterBase")
    @patch("tools.crawl4ai_crawler.adapter.process_job_vector_context")
    @patch("tools.crawl4ai_crawler.adapter.map_currency")
    @patch("tools.crawl4ai_crawler.adapter.map_seniority_level")
    @patch("tools.crawl4ai_crawler.adapter.map_working_model")
    @patch("tools.crawl4ai_crawler.adapter.map_working_hours")
    @patch("tools.crawl4ai_crawler.adapter.clean_html_text", return_value="Clean Text")
    @patch("tools.crawl4ai_crawler.adapter.parse_to_list")
    def test_job_adapter_valid_data(
        self,
        mock_parse,
        mock_clean,
        mock_hours,
        mock_model,
        mock_seniority,
        mock_currency,
        mock_vector,
        mock_base,
        mock_company_adapter,
        mock_dt,
    ):
        mock_dt.now.return_value = datetime(2023, 1, 1, tzinfo=UTC)
        mock_base.parse_salary.return_value = (1000, 2000, "USD")

        mock_skill = MagicMock()
        mock_skill.name = "Python"
        mock_base.process_skills.return_value = [mock_skill]
        mock_parse.side_effect = [["Req 1"], ["Python"]]

        mock_company_mock = MagicMock()
        mock_company_mock.name = "Real Corp"
        mock_company_adapter.return_value = mock_company_mock

        raw_data = {
            "title": " Backend Dev ",
            "description": "<html>Desc</html>",
            "location": "HCM",
            "salary": "1000-2000",
            "requirements": ["Req 1"],
            "skills": ["Python"],
            "nice_to_have": ["Docker"],
            "apply_url": "http://apply.com",
        }

        crawl4ai_adapter(raw_data, "http://source.com")

        mock_base.parse_salary.assert_called_once_with("1000-2000")
        build_job_kwargs = mock_base.build_job.call_args[1]
        assert build_job_kwargs["title"] == "Backend Dev"
        assert build_job_kwargs["url"] == "http://apply.com"
        assert build_job_kwargs["min_salary"] == 1000
        assert build_job_kwargs["max_salary"] == 2000
        assert build_job_kwargs["required_qualifications"] == ["Req 1"]
        assert build_job_kwargs["nice_to_have"] == ["Clean Text"]
        assert build_job_kwargs["skills"] == [mock_skill]
