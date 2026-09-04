from __future__ import annotations

import httpx

from scripts.test_case_report.config import GITHUB_API


class GitHubClient:
    def __init__(self, token: str, owner: str, repo: str) -> None:
        self.owner = owner
        self.repo = repo
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.client = httpx.Client(headers=self.headers, timeout=30)

    def list_issues(self, state: str = "open") -> list[dict]:
        issues: list[dict] = []
        page = 1

        while True:
            response = self.client.get(
                f"{GITHUB_API}/repos/{self.owner}/{self.repo}/issues",
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
        response = self.client.post(
            f"{GITHUB_API}/repos/{self.owner}/{self.repo}/issues",
            json={"title": title, "body": body, "labels": labels},
        )
        response.raise_for_status()
        return response.json()

    def close_issue(self, issue_number: int) -> None:
        response = self.client.patch(
            f"{GITHUB_API}/repos/{self.owner}/{self.repo}/issues/{issue_number}",
            json={"state": "closed", "state_reason": "completed"},
        )
        response.raise_for_status()

    def reopen_issue(self, issue_number: int) -> None:
        response = self.client.patch(
            f"{GITHUB_API}/repos/{self.owner}/{self.repo}/issues/{issue_number}",
            json={"state": "open"},
        )
        response.raise_for_status()

    def close(self) -> None:
        self.client.close()
