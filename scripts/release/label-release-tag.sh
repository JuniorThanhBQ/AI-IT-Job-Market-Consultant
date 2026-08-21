#!/bin/bash
set -euo pipefail

if [ -z "${PR_NUMBER:-}" ]; then
  echo "Error: PR_NUMBER environment variable is not set." >&2
  exit 1
fi

REPO="${GITHUB_REPOSITORY:-}"
if [ -z "$REPO" ]; then
  echo "Error: GITHUB_REPOSITORY environment variable is not set." >&2
  exit 1
fi

echo "Fetching commits for PR #${PR_NUMBER} in repo ${REPO}..."
commits=$(gh pr view "$PR_NUMBER" --repo "$REPO" --json commits --jq '.commits[].message' 2>/dev/null || true)

if [ -z "$commits" ]; then
  echo "No commits found or unable to fetch commits."
  exit 0
fi

if echo "$commits" | grep -Ei "(Release|Tag):"; then
  echo "Matching commit message found. Adding 'Type: Release - Tag' label."
  gh pr edit "$PR_NUMBER" --repo "$REPO" --add-label "Type: Release - Tag"
else
  echo "No matching commit messages found."
fi
