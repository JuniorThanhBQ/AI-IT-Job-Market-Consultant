# ADR-04: Software Quality Assurance based on SAST, CI/CD, and Automated Testing

## Status
Approved

## Context
With only a single developer, manual validation of all components such as job crawlers, the AI Agent, and the frontend is inefficient and prone to human error. Additionally, the system also stores sensitive user profiles and processes unstructured recruitment data. Therefore, the project requires an automated process to verify database health, enforce security standards, and run test suites before any code is merged or deployed.

## Decision
Standardize code quality control by integrating Static Application Security Testing tools such as Bandit, ESLint, Semgrep, SonarCloud, and Zizmor, automated testing with pytest and Playwright, and a structured CI/CD pipeline through GitHub Actions to run checks automatically on every commit and pull request.

## Rationale
1. **Automation Saves Time:** Running automated tests and code checks in a CI/CD pipeline saves manual verification time.
2. **Early Bug and Security Detection:** SAST tools scan for security vulnerabilities and configurations statically, catching issues before code reaches staging or production.
3. **Ensures Workflow Integrity:** Incorporating tools like `zizmor` audits the GitHub Actions workflows themselves, preventing insecure runner settings or dangerous workflow triggers.
4. **Enforces Quality Standards:** Automated linters verify that coding patterns remain clean and uniform, keeping technical debt low.

## Consequences
### Positive
* **High Software Reliability:** Automatically executing tests on all PRs catches regressions before code can impact active staging or production environments.
* **Proactive Security Posture:** Integrates static scanners to block credential leaks, outdated dependencies, and dangerous code patterns early in the development lifecycle.
* **Rapid Feedback Loop:** The developer receives immediate feedback directly inside GitHub if a commit breaks syntax, style, or existing functionality.

### Negative
* **Pipeline Maintenance Overhead:** Setting up and managing multiple workflows and scanners requires initial planning and ongoing maintenance to keep dependencies updated.
* **Increased Build Duration:** Running multiple test suites and security scans on every push increases build times and consumes GitHub Actions runner minutes.
* **Handling False Positives:** Dealing with false alerts requires manual triage and adding skip annotations like `# nosemgrep`.

## Decision Date
Approved on 18/07/2026
