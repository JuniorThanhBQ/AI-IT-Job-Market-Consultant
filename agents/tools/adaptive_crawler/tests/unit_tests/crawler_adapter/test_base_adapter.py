from unittest.mock import patch


from agents.tools.adaptive_crawler.crawler_adapter.base_adapter import JobAdapterBase


class TestJobAdapterBase:
    @patch(
        "agents.tools.adaptive_crawler.crawler_adapter.base_adapter._get_skill_taxonomy"
    )
    def test_classify_skill_category_match(self, mock_get_taxonomy):
        mock_get_taxonomy.return_value = {
            "Programming": ["python", "java", "c++"],
            "Database": ["sql", "mongodb"],
        }

        assert JobAdapterBase.classify_skill_category("Python") == "Programming"
        assert JobAdapterBase.classify_skill_category("SQL Server") == "Database"

    @patch(
        "agents.tools.adaptive_crawler.crawler_adapter.base_adapter._get_skill_taxonomy"
    )
    def test_classify_skill_category_fallback(self, mock_get_taxonomy):
        mock_get_taxonomy.return_value = {"Programming": ["python"]}

        result = JobAdapterBase.classify_skill_category("Unknown Skill")

        assert result == "Technical"

    def test_calculate_content_hash_consistency(self):
        title, comp, desc, loc = "Dev", "TechCorp", "<p>Code</p>", "HCM"

        hash1 = JobAdapterBase.calculate_content_hash(title, comp, desc, loc)
        hash2 = JobAdapterBase.calculate_content_hash(title, comp, desc, loc)
        hash3 = JobAdapterBase.calculate_content_hash(title, comp, "Code", loc)

        assert hash1 == hash2
        assert hash1 == hash3
        assert isinstance(hash1, str)
        assert len(hash1) == 64

    def test_parse_salary_vnd_range(self):
        min_sal, max_sal, curr = JobAdapterBase.parse_salary(
            "20,000,000 - 30,000,000 VND"
        )

        assert min_sal == 20000000.0
        assert max_sal == 30000000.0
        assert curr == "VND"

    def test_parse_salary_usd_single_value(self):
        min_sal, max_sal, curr = JobAdapterBase.parse_salary("$1,500")

        assert min_sal == 1500.0
        assert max_sal == 1500.0
        assert curr == "USD"

    def test_parse_salary_no_digits(self):
        min_sal, max_sal, curr = JobAdapterBase.parse_salary("Negotiable")

        assert min_sal == 0.0
        assert max_sal == 0.0
        assert curr == "VND"
