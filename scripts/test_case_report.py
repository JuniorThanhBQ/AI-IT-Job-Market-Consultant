from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.test_case_report.config import (
    PROJECT_ROOT,
    TEST_CASE_FILE,
)
from scripts.test_case_report.core import BugReporter, GitHubClient
from scripts.test_case_report.utils import TestCaseParser


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Environment variable '{name}' is not set.")
        sys.exit(1)
    return value


if __name__ == "__main__":
    load_dotenv(PROJECT_ROOT / ".env")
    token = require_env("GITHUB_TOKEN")
    owner = require_env("GITHUB_owner")
    repo = require_env("GITHUB_repo")
    gh = GitHubClient(token=token, owner=owner, repo=repo)
    parser = TestCaseParser()
    test_cases = parser.parse(TEST_CASE_FILE)

    try:
        reporter = BugReporter(github=gh)
        reporter.run(test_cases)
    finally:
        gh.close()
