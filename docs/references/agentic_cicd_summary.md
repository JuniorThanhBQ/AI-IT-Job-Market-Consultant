# 🚀 CI/CD Pipeline Architecture & Workflows

This document outlines the CI/CD pipeline structure for the **AI-IT-Job-Market-Consultant** project. The project utilizes **14 GitHub Action workflows** organized into entrypoint deployment pipelines, an orchestrator workflow, and reusable sub-pipelines.

---

## 1. High-Level Branch Deployment Strategy
The pipeline triggers automatically based on the target branch of pushes and pull requests:

```mermaid
graph TD
    Develop["develop branch"]
    Release["release/* branches"]
    Main["main branch"]

    DeployDev["deploy-dev.yml (Dev Deployment)"]
    DeployStaging["deploy-staging.yml (Staging Deployment)"]
    DeployProd["deploy-production.yml (Production Deployment)"]
    AutoTag["auto-tag-version-workflow.yml (Auto Release & Tag)"]

    FullCI["full-ci-commit-workflow.yml (Common CI Orchestrator)"]

    TestStaging["test-staging (Docker Compose & Health Checks)"]
    DeployProdJob["deploy-production (Build & Push Docker Hub)"]

    Develop -->|Push / PR| DeployDev
    Release -->|Push| DeployStaging
    Main -->|Push / PR| DeployProd
    Main -->|Push| AutoTag

    DeployDev -->|Triggers| FullCI
    DeployStaging -->|Triggers| FullCI
    DeployProd -->|Triggers| FullCI

    FullCI -->|Needs Met| TestStaging
    FullCI -->|Needs Met| DeployProdJob
```

---

## 2. Reusable Orchestrator: Full CI Commit Workflow
The [full-ci-commit-workflow.yml](file:///C:/Users/Kisune_Alvarez/Desktop/MyProjects/AI-IT-Job-Market-Consultant/.github/workflows/full-ci-commit-workflow.yml) serves as a reusable gatekeeper that runs builds, linting, security, and tests sequentially.

```mermaid
graph TD
    Trigger_CI["Trigger: Push / PR / Call"]
    Job_Build["1. Build Stage (build-workflow.yml)"]
    Job_Lint["2. Lint Stage (lint-workflow.yml)"]
    Job_Security["3. Security Stage (security-workflow.yml)"]
    Job_Testing["4. Testing Stage (testing-workflow.yml)"]

    Trigger_CI --> Job_Build
    Job_Build --> Job_Lint
    Job_Lint --> Job_Security
    Job_Security --> Job_Testing
```

---

## 3. Sub-Workflow Details

### A. Build Stage (`build-workflow.yml`)
Runs Python and Node build validations in parallel.

```mermaid
graph TD
    Start_Build["Start Build Stage"]
    Build_Backend["Build Backend (Python 3.12, app compilation)"]
    Build_Frontend["Build Frontend (Node 20, npm run build)"]

    Start_Build --> Build_Backend
    Start_Build --> Build_Frontend
```

### B. Lint Stage (`lint-workflow.yml`)
Runs syntax, style, and configuration checks in parallel.

```mermaid
graph TD
    Start_Lint["Start Lint Stage"]
    Lint_Backend["Lint Backend (Pylint)"]
    Lint_Frontend["Lint Frontend (ESLint)"]
    Lint_Crawler["Lint Crawler (ESLint)"]
    Lint_Docker["Lint Docker Compose (validate & check compose file)"]

    Start_Lint --> Lint_Backend
    Start_Lint --> Lint_Frontend
    Start_Lint --> Lint_Crawler
    Start_Lint --> Lint_Docker
```

### C. Security Stage (`security-workflow.yml`)
A robust multi-tier scanning process enforcing quality and container gates.

```mermaid
graph TD
    Start_Sec["Start Security Stage"]
    Secret_Scan["Secret Scanning (Gitleaks)"]
    Bandit_Scan["Bandit Scanner (Backend Python)"]
    ESLint_Sec["ESLint Security Scanner (Frontend JS/TS)"]
    Semgrep_Scan["Semgrep Full-repo Scan (OWASP Top 10, Secrets, languages)"]
    CodeQL_Scan["CodeQL Scan (codeql.yml)"]
    Container_Sec["Container Security Scan (Trivy scan & gate)"]

    Start_Sec --> Secret_Scan
    Start_Sec --> Bandit_Scan
    Start_Sec --> ESLint_Sec

    Bandit_Scan --> Semgrep_Scan
    ESLint_Sec --> Semgrep_Scan
    Semgrep_Scan --> CodeQL_Scan
    CodeQL_Scan --> Container_Sec
```

### D. Testing Stage (`testing-workflow.yml`)
Verifies execution logic across python backend tests, frontend unit tests, and crawler playwright browser tests.

```mermaid
graph TD
    Start_Test["Start Testing Stage"]
    Test_Backend["Test Backend (Pytest / Unittest)"]
    Test_Frontend["Test Frontend (Jest / Vitest)"]
    Test_Crawler["Test Crawler (Playwright browsers)"]

    Start_Test --> Test_Backend
    Start_Test --> Test_Frontend
    Start_Test --> Test_Crawler
```

---

## 4. Utility & Automation Workflows
These workflows run independently for repository health, automation, and bookkeeping:

*   **[detect-conflicts.yml](file:///C:/Users/Kisune_Alvarez/Desktop/MyProjects/AI-IT-Job-Market-Consultant/.github/workflows/detect-conflicts.yml):** Runs on push and PR synchronize to detect and label merge conflicts.
*   **[labeler.yml](file:///C:/Users/Kisune_Alvarez/Desktop/MyProjects/AI-IT-Job-Market-Consultant/.github/workflows/labeler.yml):** Automatically labels PRs based on file changes and validates that at least one primary label is applied before merge.
*   **[latest-changes.yml](file:///C:/Users/Kisune_Alvarez/Desktop/MyProjects/AI-IT-Job-Market-Consultant/.github/workflows/latest-changes.yml):** Generates and appends release notes automatically to `release-notes.md` upon PR merges into `master`.
*   **[zizmor.yml](file:///C:/Users/Kisune_Alvarez/Desktop/MyProjects/AI-IT-Job-Market-Consultant/.github/workflows/zizmor.yml):** Runs a security audit lint on the GitHub Action workflows themselves to check for dangerous triggers and insecure steps.
