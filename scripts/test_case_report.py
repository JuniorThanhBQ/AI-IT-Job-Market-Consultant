from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx
import pandas as pd
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_CASE_FILE = PROJECT_ROOT / "docs" / "testing" / "test-case-report.xlsx"

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


class TestCaseParser:
    REQUIRED_COLUMNS = {
        "Test case ID",
        "Test case name",
        "Test case procedure",
        "Expected results",
        "Actual results",
        "Status",
        "AI test results",
        "AI Status",
        "Reference",
        "Note",
    }

    COLUMN_MAPPING = {
        "Test case ID": "test_case_id",
        "Test case name": "name",
        "Test case procedure": "procedure",
        "Expected results": "expected_result",
        "Actual results": "actual_result",
        "Status": "status",
        "AI test results": "ai_result",
        "AI Status": "ai_status",
        "Reference": "reference",
        "Note": "note",
    }

    def parse(self, file_path: str | Path) -> list[TestCase]:
        results: list[TestCase] = []

        with pd.ExcelFile(file_path) as excel:
            sheets = self._find_test_sheets(excel)

            for sheet_name in sheets:
                header_row = self._find_header_row(excel, sheet_name)
                df = pd.read_excel(excel, sheet_name=sheet_name, header=header_row)
                self._validate_columns(df, sheet_name)
                df = self._normalize(df)
                for row in df.to_dict(orient="records"):
                    results.append(TestCase(**row, sheet=sheet_name))

        return results

    def _find_test_sheets(self, excel: pd.ExcelFile) -> list[str]:
        sheets = [
            sheet
            for sheet in excel.sheet_names
            if sheet.strip().lower().startswith("test")
        ]

        if not sheets:
            raise ValueError(
                f"No sheet starting with 'test' found. "
                f"Available sheets: {excel.sheet_names}"
            )

        return sheets

    def _find_header_row(self, excel: pd.ExcelFile, sheet_name: str) -> int:
        raw = pd.read_excel(excel, sheet_name=sheet_name, header=None)

        for idx, row in raw.iterrows():
            cell_values = set(str(v).strip() for v in row if pd.notna(v))
            if self.REQUIRED_COLUMNS.issubset(cell_values):
                return int(str(idx))

        raise ValueError(
            f"Sheet '{sheet_name}': could not find a header row containing "
            f"all required columns: {sorted(self.REQUIRED_COLUMNS)}"
        )

    def _validate_columns(self, df: pd.DataFrame, sheet_name: str) -> None:
        missing = self.REQUIRED_COLUMNS - set(df.columns)

        if missing:
            raise ValueError(
                f"Sheet '{sheet_name}' is missing required columns: {sorted(missing)}"
            )

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns=self.COLUMN_MAPPING)

        text_columns = [
            "test_case_id",
            "name",
            "procedure",
            "expected_result",
            "actual_result",
            "status",
            "ai_result",
            "ai_status",
            "reference",
            "note",
        ]

        df = df[text_columns]

        for column in text_columns:
            df[column] = df[column].fillna("").astype(str).str.strip()

        return df


class GitHubClient:
    def __init__(self, token: str, owner: str, repo: str) -> None:
        self._owner = owner
        self._repo = repo
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self._client = httpx.Client(headers=self._headers, timeout=30)

    def list_issues(self, state: str = "open") -> list[dict]:
        issues: list[dict] = []
        page = 1

        while True:
            response = self._client.get(
                f"{GITHUB_API}/repos/{self._owner}/{self._repo}/issues",
                params={"state": state, "per_page": 100, "page": page},
            )
            response.raise_for_status()
            batch = response.json()

            if not batch:
                break

            issues.extend(batch)
            page += 1

        return issues

    def create_issue(self, title: str, body: str, labels: list[str]) -> dict:
        response = self._client.post(
            f"{GITHUB_API}/repos/{self._owner}/{self._repo}/issues",
            json={"title": title, "body": body, "labels": labels},
        )
        response.raise_for_status()
        return response.json()

    def close_issue(self, issue_number: int) -> None:
        response = self._client.patch(
            f"{GITHUB_API}/repos/{self._owner}/{self._repo}/issues/{issue_number}",
            json={"state": "closed", "state_reason": "completed"},
        )
        response.raise_for_status()

    def reopen_issue(self, issue_number: int) -> None:
        response = self._client.patch(
            f"{GITHUB_API}/repos/{self._owner}/{self._repo}/issues/{issue_number}",
            json={"state": "open"},
        )
        response.raise_for_status()

    def close(self) -> None:
        self._client.close()


def _build_issue_title(test_case: TestCase) -> str:
    return f"{ISSUE_TITLE_PREFIX} {test_case.test_case_id} - {test_case.name}"


def _build_issue_body(test_case: TestCase) -> str:
    return (
        f"## Bug Report\n\n"
        f"**Test Case ID:** `{test_case.test_case_id}`  \n"
        f"**Sheet:** `{test_case.sheet}`  \n"
        f"**Reference:** {test_case.reference or '_N/A_'}  \n\n"
        f"### Procedure\n{test_case.procedure or '_N/A_'}\n\n"
        f"### Expected Result\n{test_case.expected_result or '_N/A_'}\n\n"
        f"### Actual Result\n{test_case.actual_result or '_N/A_'}\n\n"
        f"### AI Test Result\n{test_case.ai_result or '_N/A_'}  \n"
        f"**AI Status:** `{test_case.ai_status or 'N/A'}`\n\n"
        f"### Note\n{test_case.note or '_N/A_'}\n"
    )


class BugReporter:
    def __init__(self, github: GitHubClient) -> None:
        self._gh = github

    def run(self, test_cases: list[TestCase]) -> None:
        print("Fetching existing GitHub issues …")
        open_issues = self._gh.list_issues(state="open")
        closed_issues = self._gh.list_issues(state="closed")

        open_by_id: dict[str, dict] = {}
        closed_by_id: dict[str, dict] = {}

        for issue in open_issues:
            tc_id = self._extract_tc_id(issue["title"])
            if tc_id:
                open_by_id[tc_id] = issue

        for issue in closed_issues:
            tc_id = self._extract_tc_id(issue["title"])
            if tc_id:
                closed_by_id[tc_id] = issue

        failed = [tc for tc in test_cases if tc.status.lower() == "fail"]
        passed = [tc for tc in test_cases if tc.status.lower() == "pass"]

        created = reopened = skipped = closed = 0

        print(f"Found {len(failed)} failing and {len(passed)} passing test cases.\n")

        for tc in failed:
            if tc.test_case_id in open_by_id:
                print(f"  ⏭ SKIP  (already open) {tc.test_case_id}")
                skipped += 1
                continue

            if tc.test_case_id in closed_by_id:
                issue = closed_by_id[tc.test_case_id]
                self._gh.reopen_issue(issue["number"])
                print(
                    f"  ↺ REOPEN #{issue['number']} (still failing) {tc.test_case_id}"
                )
                reopened += 1
                continue

            title = _build_issue_title(tc)
            body = _build_issue_body(tc)
            issue = self._gh.create_issue(title, body, ISSUE_LABELS)
            print(f"  ✓ CREATED #{issue['number']} {title}")
            created += 1

        for tc in passed:
            if tc.test_case_id in open_by_id:
                issue = open_by_id[tc.test_case_id]
                self._gh.close_issue(issue["number"])
                print(f"  ✓ CLOSED  #{issue['number']} (now passing) {tc.test_case_id}")
                closed += 1

        print(
            f"\nDone — {created} created, {reopened} reopened, {closed} closed, {skipped} skipped."
        )

    @staticmethod
    def _extract_tc_id(title: str) -> str:
        if not title.startswith(ISSUE_TITLE_PREFIX):
            return ""
        remainder = title[len(ISSUE_TITLE_PREFIX) :].strip()
        return remainder.split(" - ")[0].strip()


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"ERROR: environment variable '{name}' is not set.")
        sys.exit(1)
    return value


if __name__ == "__main__":
    load_dotenv(PROJECT_ROOT / ".env")

    token = _require_env("GITHUB_TOKEN")
    owner = _require_env("GITHUB_OWNER")
    repo = _require_env("GITHUB_REPO")

    parser = TestCaseParser()
    test_cases = parser.parse(TEST_CASE_FILE)

    gh = GitHubClient(token=token, owner=owner, repo=repo)
    try:
        reporter = BugReporter(github=gh)
        reporter.run(test_cases)
    finally:
        gh.close()
