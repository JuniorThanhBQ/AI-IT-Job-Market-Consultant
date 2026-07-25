from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from app.core.enums import CompanyType, Currency, SeniorityLevel, WorkingModel
from app.modules.job.models import Job
from app.modules.company.models import Company

from agents.tools.adaptive_crawler.crawler_adapter.itviec_adapter import (
    _map_working_model,
    _map_seniority_level,
    _map_company_type,
    _map_currency,
    adapter_itviec,
)


class TestITViecMappers:
    def test_map_working_model(self):
        assert _map_working_model("Hybrid at office") == WorkingModel.HYBRID
        assert _map_working_model("remote fully") == WorkingModel.REMOTE
        assert _map_working_model("Unknown") == WorkingModel.ONSITE

    def test_map_seniority_level(self):
        assert _map_seniority_level("Senior Python Dev") == SeniorityLevel.SENIOR
        assert (
            _map_seniority_level("Backend Developer", "Junior") == SeniorityLevel.JUNIOR
        )
        assert _map_seniority_level("Just a Dev") == SeniorityLevel.MID

    def test_map_company_type(self):
        assert _map_company_type("Outsourcing firm") == CompanyType.OUTSOURCING
        assert _map_company_type("Random") == CompanyType.PRODUCT

    def test_map_currency(self):
        assert _map_currency("USD") == Currency.USD
        assert _map_currency("€") == Currency.EUR
        assert _map_currency("VND") == Currency.VND


class TestAdapterITViec:
    @patch("agents.tools.adaptive_crawler.crawler_adapter.itviec_adapter.datetime")
    @patch(
        "agents.tools.adaptive_crawler.crawler_adapter.itviec_adapter.JobAdapterBase.classify_skill_category",
        return_value="Technical",
    )
    def test_adapter_itviec_happy_path(self, mock_classify, mock_datetime):
        mock_now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strptime.side_effect = datetime.strptime

        raw_data = {
            "title": "Backend Engineer",
            "url": "https://itviec.com/job/1",
            "company": {"name": "Tech Corp", "type": "Outsourcing"},
            "job_overview": {
                "location": "Ho Chi Minh",
                "salary": "$1,000 - $2,000",
                "work_model": "Hybrid",
                "skills": ["Python", "Django"],
            },
            "job_details": {
                "description": "<p>Write backend code.</p>",
                "requirements": ["3 years experience"],
            },
            "schema_data": {"validThrough": "2026-02-01T00:00:00Z"},
        }

        job = adapter_itviec(raw_data)

        assert isinstance(job, Job)
        assert job.title == "Backend Engineer"
        assert job.source == "itviec"
        assert job.min_salary == 1000.0
        assert job.max_salary == 2000.0
        assert job.currency == Currency.USD
        assert job.working_model == WorkingModel.HYBRID
        assert job.seniority == SeniorityLevel.MID
        assert job.expired_date == datetime(2026, 2, 1)

        assert len(job.skills) == 2
        assert job.skills[0].name == "Python"

        assert isinstance(job.company, Company)
        assert job.company.name == "Tech Corp"
        assert job.company.company_type == CompanyType.OUTSOURCING

    @patch("agents.tools.adaptive_crawler.crawler_adapter.itviec_adapter.datetime")
    def test_adapter_itviec_missing_data_fallbacks(self, mock_datetime):
        mock_now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        raw_data = {}

        job = adapter_itviec(raw_data)

        assert job.title == "Unknown Title"
        assert job.company.name == "Unspecified Employer (Itviec)"
        assert job.company.company_type == CompanyType.PRODUCT
        assert job.min_salary == 0.0
        assert job.max_salary == 0.0
        assert job.currency == Currency.VND
        assert job.working_model == WorkingModel.ONSITE
        assert job.seniority == SeniorityLevel.MID
        assert job.expired_date == mock_now + timedelta(days=30)
