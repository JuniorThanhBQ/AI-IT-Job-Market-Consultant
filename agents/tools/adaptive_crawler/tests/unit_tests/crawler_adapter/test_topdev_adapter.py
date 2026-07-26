from datetime import datetime, timedelta
from unittest.mock import patch

from app.core.enums import Currency, SeniorityLevel, WorkingModel, CompanyType
from app.modules.job.models import Job
from app.modules.company.models import Company

from agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter import (
    _map_company_type,
    _map_working_model,
    _map_seniority_level,
    _map_currency,
    adapter_topdev,
)


class TestTopDevMappers:
    def test_map_company_type(self):
        assert _map_company_type("Outsourcing Company") == CompanyType.OUTSOURCING
        assert _map_company_type("IT Outsource") == CompanyType.OUTSOURCING
        assert _map_company_type("Consulting Group") == CompanyType.CONSULTING
        assert _map_company_type("Digital Agency") == CompanyType.AGENCY
        assert _map_company_type("Product Based") == CompanyType.PRODUCT
        assert _map_company_type("Unknown Type") == CompanyType.PRODUCT
        assert _map_company_type("") == CompanyType.PRODUCT
        assert _map_company_type(None) == CompanyType.PRODUCT

    def test_map_working_model(self):
        assert _map_working_model("Hybrid") == WorkingModel.HYBRID
        assert _map_working_model("Linh hoạt") == WorkingModel.HYBRID
        assert _map_working_model("Remote") == WorkingModel.REMOTE
        assert _map_working_model("Làm việc từ xa") == WorkingModel.REMOTE
        assert _map_working_model("Office") == WorkingModel.ONSITE
        assert _map_working_model("Onsite") == WorkingModel.ONSITE
        assert _map_working_model("Trực tiếp") == WorkingModel.ONSITE
        assert _map_working_model("Tại văn phòng") == WorkingModel.ONSITE
        assert _map_working_model("Unknown") == WorkingModel.ONSITE
        assert _map_working_model("") == WorkingModel.ONSITE
        assert _map_working_model(None) == WorkingModel.ONSITE

    def test_map_seniority_level(self):
        assert _map_seniority_level("Senior Python Dev") == SeniorityLevel.SENIOR
        assert _map_seniority_level("Developer", "Senior") == SeniorityLevel.SENIOR
        assert (
            _map_seniority_level("Backend Developer", "Junior") == SeniorityLevel.JUNIOR
        )
        assert _map_seniority_level("Junior Developer") == SeniorityLevel.JUNIOR
        assert _map_seniority_level("Thực tập sinh IT") == SeniorityLevel.INTERN
        assert _map_seniority_level("Data Intern") == SeniorityLevel.INTERN
        assert _map_seniority_level("Fresher Java") == SeniorityLevel.FRESHER
        assert _map_seniority_level("Tech Lead") == SeniorityLevel.LEAD
        assert _map_seniority_level("Project Manager") == SeniorityLevel.MANAGER
        assert _map_seniority_level("Quản lý dự án") == SeniorityLevel.MANAGER
        assert (
            _map_seniority_level("Director of Engineering") == SeniorityLevel.DIRECTOR
        )
        assert _map_seniority_level("Giám đốc khối IT") == SeniorityLevel.DIRECTOR
        assert _map_seniority_level("Chief Executive") == SeniorityLevel.EXECUTIVE
        assert _map_seniority_level("Just a Dev") == SeniorityLevel.MID
        assert _map_seniority_level("", "") == SeniorityLevel.MID

    def test_map_currency(self):
        assert _map_currency("USD") == Currency.USD
        assert _map_currency("$") == Currency.USD
        assert _map_currency("EUR") == Currency.EUR
        assert _map_currency("€") == Currency.EUR
        assert _map_currency("JPY") == Currency.JPY
        assert _map_currency("¥") == Currency.JPY
        assert _map_currency("SGD") == Currency.SGD
        assert _map_currency("VND") == Currency.VND
        assert _map_currency("VNĐ") == Currency.VND
        assert _map_currency("") == Currency.VND
        assert _map_currency(None) == Currency.VND


class TestAdapterTopDev:
    @patch("agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter.datetime")
    def test_adapter_topdev_happy_path(self, mock_datetime):
        mock_now = datetime(2026, 1, 1)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.strptime.side_effect = datetime.strptime

        raw_data = {
            "title": "Backend Engineer",
            "url": "https://topdev.vn/detail-jobs/backend-engineer-1",
            "company": "Tech Corp",
            "salary": "$1,000 - $2,000",
            "skills": ["Python", "Django"],
            "description": "<p>Write backend code.</p>",
            "requirements": "3 years experience",
            "job_overview": {
                "location": "Ho Chi Minh",
                "valid_through": "2026-02-01",
            },
            "job_details": {
                "employment_type": "Fulltime",
                "work_type": "Hybrid",
                "level": "Junior",
            },
            "company_info": {
                "name": "Tech Corp",
                "industry": "IT Software",
                "country": "Vietnam",
                "type": "Outsource",
            },
            "benefits": ["Health Insurance", "Macbook Pro"],
        }

        job = adapter_topdev(raw_data)

        assert isinstance(job, Job)
        assert job.title == "Backend Engineer"
        assert job.source == "topdev"
        assert job.min_salary == 1000.0
        assert job.max_salary == 2000.0
        assert job.currency == Currency.USD
        assert job.working_model == WorkingModel.HYBRID
        assert job.seniority == SeniorityLevel.JUNIOR
        assert job.expired_date == datetime(2026, 2, 1)

        assert len(job.skills) == 2
        assert job.skills[0].name == "Python"
        assert job.skills[1].name == "Django"

        assert isinstance(job.company, Company)
        assert job.company.name == "Tech Corp"
        assert job.company.company_type == CompanyType.OUTSOURCING
        assert len(job.company.benefits) == 2
        assert job.company.benefits[0].name == "Health Insurance"

    @patch("agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter.datetime")
    def test_adapter_topdev_missing_data_fallbacks(self, mock_datetime):
        mock_now = datetime(2026, 1, 1)
        mock_datetime.utcnow.return_value = mock_now

        raw_data = {}

        job = adapter_topdev(raw_data)

        assert job.title == "Unknown Title"
        assert job.company.name == "Unspecified Employer (Topdev)"
        assert job.min_salary == 0.0
        assert job.max_salary == 0.0
        assert job.currency == Currency.VND
        assert job.working_model == WorkingModel.ONSITE
        assert job.seniority == SeniorityLevel.MID
        assert job.expired_date == mock_now + timedelta(days=30)
        assert job.company.company_type == CompanyType.PRODUCT
        assert len(job.skills) == 0
        assert len(job.responsibilities) == 0
        assert len(job.required_qualifications) == 0

    @patch("agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter.datetime")
    def test_adapter_topdev_invalid_nested_types(self, mock_datetime):
        mock_now = datetime(2026, 1, 1)
        mock_datetime.utcnow.return_value = mock_now

        raw_data = {
            "title": "Frontend Dev",
            "job_overview": "This is a string, not a dict",
            "job_details": ["list", "instead", "of", "dict"],
            "company_info": None,
            "qualifications": 12345,
            "salary": "30000000 - 40000000",
            "company_address": "123 Street",
        }

        job = adapter_topdev(raw_data)

        assert job.title == "Frontend Dev"
        assert job.min_salary == 30000000.0
        assert job.max_salary == 40000000.0
        assert job.currency == Currency.VND
        assert job.company.addresses == ["123 Street"]

    @patch("agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter.datetime")
    def test_adapter_topdev_date_parsing_fallback(self, mock_datetime):
        mock_now = datetime(2026, 1, 1)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.strptime.side_effect = ValueError("Invalid format")

        raw_data = {
            "title": "DevOps",
            "job_overview": {"valid_through": "Invalid-Date-Format"},
        }

        job = adapter_topdev(raw_data)

        assert job.expired_date == mock_now + timedelta(days=30)

    @patch("agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter.datetime")
    def test_adapter_topdev_responsibilities_fallback_from_desc(self, mock_datetime):
        mock_now = datetime(2026, 1, 1)
        mock_datetime.utcnow.return_value = mock_now

        raw_data = {
            "title": "QA Engineer",
            "description": "<ul><li>Test software</li><li>Write scripts</li></ul>",
            "responsibilities": None,
        }

        job = adapter_topdev(raw_data)

        assert len(job.responsibilities) > 0
        assert "Test software" in job.responsibilities

    @patch("agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter.datetime")
    def test_adapter_topdev_company_details_and_type(self, mock_datetime):
        mock_now = datetime(2026, 1, 1)
        mock_datetime.utcnow.return_value = mock_now

        raw_data = {
            "title": "UI Designer",
            "company_info": {
                "name": "Design Studio",
                "type": "Agency",
                "addresses": ["Hanoi", "Da Nang"],
                "profile_url": "https://designstudio.com",
            },
        }

        job = adapter_topdev(raw_data)

        assert job.company.name == "Design Studio"
        assert job.company.company_type == CompanyType.AGENCY
        assert job.company.addresses == ["Hanoi", "Da Nang"]
        assert job.company.website == "https://designstudio.com"

    @patch("agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter.datetime")
    def test_adapter_topdev_qualifications_merging(self, mock_datetime):
        mock_now = datetime(2026, 1, 1)
        mock_datetime.utcnow.return_value = mock_now

        raw_data = {
            "title": "System Admin",
            "qualifications": {
                "preferred": ["AWS Cert"],
                "key_competencies": ["Linux Pro"],
            },
            "nice_to_have": ["Docker"],
        }

        job = adapter_topdev(raw_data)

        assert len(job.nice_to_have) == 2
        assert "Linux Pro" in job.nice_to_have
        assert "AWS Cert" in job.nice_to_have
        assert "Docker" not in job.nice_to_have

        raw_data_fallback = {
            "title": "System Admin",
            "qualifications": {
                "preferred": ["AWS Cert"],
            },
            "nice_to_have": ["Docker"],
        }

        job_fallback = adapter_topdev(raw_data_fallback)

        assert len(job_fallback.nice_to_have) == 2
        assert "Docker" in job_fallback.nice_to_have
        assert "AWS Cert" in job_fallback.nice_to_have

    @patch("agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter.datetime")
    def test_adapter_topdev_flat_requirements_fallback(self, mock_datetime):
        mock_now = datetime(2026, 1, 1)
        mock_datetime.utcnow.return_value = mock_now

        raw_data = {
            "title": "Tester",
            "requirements": "<ul><li>Automation</li><li>Manual</li></ul>",
            "qualifications": {},
        }

        job = adapter_topdev(raw_data)

        assert len(job.required_qualifications) > 0
        assert "Automation" in job.required_qualifications
        assert "Manual" in job.required_qualifications

    @patch("agents.tools.adaptive_crawler.crawler_adapter.topdev_adapter.datetime")
    def test_adapter_topdev_working_hours_fallback(self, mock_datetime):
        mock_now = datetime(2026, 1, 1)
        mock_datetime.utcnow.return_value = mock_now

        raw_data = {
            "title": "Part Time Dev",
            "working_hours": "Part-time 20h/week",
            "job_details": {},
        }

        job = adapter_topdev(raw_data)

        assert job.working_hours == "Part-time 20h/week"
