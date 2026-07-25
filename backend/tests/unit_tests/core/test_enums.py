from app.core.enums import Currency, JobStatus, SeniorityLevel


class TestEnums:
    def test_job_status_values(self):
        assert JobStatus.OPEN == "Open"
        assert JobStatus.CLOSED == "Closed"
        assert isinstance(JobStatus.OPEN, str)

    def test_seniority_level_values(self):
        assert SeniorityLevel.SENIOR == "Senior"
        assert SeniorityLevel.UNKNOWN == "Unknown"

    def test_currency_values(self):
        assert Currency.VND == "VND"
        assert Currency.USD == "USD"
