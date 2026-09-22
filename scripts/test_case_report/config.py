from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_CASE_FILE = PROJECT_ROOT / "docs/testing/test-case-report.xlsx"
GITHUB_API = "https://api.github.com"
ISSUE_TITLE_PREFIX = "[BUG]"
ISSUE_LABELS = ["Type: Bug", "Priority: Critical", "Status: Available"]


@dataclass
class TestCase:
    test_case_id: str
    name: str
    procedure: str
    expected_result: str
    actual_result: str
    status: str
    ai_result: str
    ai_status: str
    reference: str
    note: str
    sheet: str = ""
