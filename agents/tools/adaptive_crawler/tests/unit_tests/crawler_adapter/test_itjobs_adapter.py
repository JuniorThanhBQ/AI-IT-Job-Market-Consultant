from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from app.core.enums import CompanyType, Currency, SeniorityLevel, WorkingModel
from app.modules.job.models import Job
from app.modules.company.models import Company

from agents.tools.adaptive_crawler.crawler_adapter.itjobs_adapter import (
    _map_working_model,
    _map_seniority_level,
    _map_company_type,
    _map_currency,
    adapter_itjobs,
)


class TestITJobsMappers:
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


class TestAdapterITJobs:
    @patch("agents.tools.adaptive_crawler.crawler_adapter.itjobs_adapter.datetime")
    @patch(
        "agents.tools.adaptive_crawler.crawler_adapter.itjobs_adapter.JobAdapterBase.classify_skill_category",
        return_value="Technical",
    )
    def test_adapter_itjobs_happy_path(self, mock_classify, mock_datetime):
        mock_now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        raw_data = {
            "title": "Frontend Engineer",
            "url": "https://itjobs.com.vn/job/1",
            "company": {
                "name": "Global Tech",
                "type": "Outsource",
                "size": "100-500",
                "company_description": "<p>A great place to work</p>",
            },
            "job": {
                "location": "Hanoi",
                "salary": "$1500 - $2500",
                "experience_level": "Senior",
                "type": "Full-time",
            },
            "requirements": {
                "general": ["3+ years React"],
                "tech_stack": ["React", "TypeScript"],
            },
            "description": ["Build UI components"],
            "technical_skills_tags": ["React", "JavaScript"],
        }

        job = adapter_itjobs(raw_data)

        assert isinstance(job, Job)
        assert job.title == "Frontend Engineer"
        assert job.source == "itjobs"
        assert job.min_salary == 1500.0
        assert job.max_salary == 2500.0
        assert job.currency == Currency.USD
        assert job.working_model == WorkingModel.ONSITE
        assert job.seniority == SeniorityLevel.SENIOR
        assert job.expired_date == (mock_now + timedelta(days=30)).replace(tzinfo=None)

        assert len(job.skills) == 2
        assert job.skills[0].name == "React"

        assert isinstance(job.company, Company)
        assert job.company.name == "Global Tech"
        assert job.company.company_type == CompanyType.OUTSOURCING
        assert job.company.size == "100-500"

    @patch("agents.tools.adaptive_crawler.crawler_adapter.itjobs_adapter.datetime")
    def test_adapter_itjobs_missing_data_fallbacks(self, mock_datetime):
        mock_now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        raw_data = {}

        job = adapter_itjobs(raw_data)

        assert job.title == "Unknown Title"
        assert job.company.name == "Unspecified Employer (Itjobs)"
        assert job.company.company_type == CompanyType.PRODUCT
        assert job.min_salary == 0.0
        assert job.max_salary == 0.0
        assert job.currency == Currency.VND
        assert job.working_model == WorkingModel.ONSITE
        assert job.seniority == SeniorityLevel.JUNIOR
        assert job.expired_date == (mock_now + timedelta(days=30)).replace(tzinfo=None)
