from __future__ import annotations

from scripts.test_case_report.config import (
    ISSUE_LABELS,
    ISSUE_TITLE_PREFIX,
    TestCase,
)
from scripts.test_case_report.core.github_client import GitHubClient
from scripts.test_case_report.utils import (
    build_issue_body,
    build_issue_title,
)


class BugReporter:
    def __init__(self, github: GitHubClient) -> None:
        self.gh = github

    @staticmethod
    def extract_testcase_id(title: str) -> str:
        if not title.startswith(ISSUE_TITLE_PREFIX):
            return ""
        remainder = title[len(ISSUE_TITLE_PREFIX) :].strip()
        return remainder.split(" - ")[0].strip()

    def bugreporter_create_issue(self, testcase: TestCase) -> None:
        title = build_issue_title(testcase)
        body = build_issue_body(testcase)
        issue = self.gh.create_issue(title, body, ISSUE_LABELS)
        print(f"CREATED #{issue['number']} {title}")

    def run(self, test_cases: list[TestCase]) -> None:
        created = reopened = skipped = closed = 0
        open_issues = self.gh.list_issues(state="open")
        closed_issues = self.gh.list_issues(state="closed")

        open_by_id: dict[str, dict] = {}
        closed_by_id: dict[str, dict] = {}

        for issue in open_issues:
            testcase_id = self.extract_testcase_id(issue["title"])
            if testcase_id:
                open_by_id[testcase_id] = issue

        for issue in closed_issues:
            testcase_id = self.extract_testcase_id(issue["title"])
            if testcase_id:
                closed_by_id[testcase_id] = issue

        failed = [
            testcase for testcase in test_cases if testcase.status.lower() == "fail"
        ]
        passed = [
            testcase for testcase in test_cases if testcase.status.lower() == "pass"
        ]
        for testcase in failed:
            if testcase.test_case_id in open_by_id:
                print(f"Already open: {testcase.test_case_id}")
                skipped += 1
                continue

            if testcase.test_case_id in closed_by_id:
                issue = closed_by_id[testcase.test_case_id]
                self.gh.reopen_issue(issue["number"])
                print(f"REOPEN #{issue['number']}: {testcase.test_case_id}")
                reopened += 1
                continue

            self.bugreporter_create_issue(testcase)
            created += 1

        for testcase in passed:
            if testcase.test_case_id in open_by_id:
                issue = open_by_id[testcase.test_case_id]
                self.gh.close_issue(issue["number"])
                print(f"CLOSED: #{issue['number']} {testcase.test_case_id}")
                closed += 1
