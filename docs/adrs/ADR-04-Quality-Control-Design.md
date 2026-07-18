# ADR-04: Software Quality Assurance based on SAST, CI/CD, and Automated Testing

## Status
Approved

## Context
With only a single developer working under a strict 10-week timeline, manual validation of all components such as job crawlers, multi-agent, and frontend is highly inefficient and prone to human error. Additionally, because the system stores sensitive user profiles and processes unstructured recruitments data. Therefore, the project requires an automated process to verify database health, enforce security standards, and run test suites before any code is merged or deployed.

## Decision
Standardize code quality control by integrating Static Application Security Testing (SAST) tools such as Bandit, ESLint, Semgrep, SonarCloud, and Zizmor, automated unit testing with pytest, and a structured CI/CD pipeline through GitHub Actions to run checks automatically on every commit and pull request.

## Rationale
1. **Automation Saves Time:** Running automated tests and code checks in a CI/CD pipeline saves valuable manual verification time, allowing the solo developer to focus on feature delivery.
2. **Early Bug and Security Detection:** SAST tools (like Semgrep, Bandit, and Trivy) scan for security vulnerabilities and configurations statically, catching issues before code reaches staging or production.
3. **Ensures Workflow Integrity:** Incorporating tools like `zizmor` audits the GitHub Actions workflows themselves, preventing insecure runner settings or dangerous workflow triggers.
4. **Enforces Quality Standards:** Automated linters (ESLint, Pylint) verify that coding patterns remain clean and uniform, keeping technical debt low.

## Consequences
### Positive
* **High Software Reliability:** Automatically executing tests on all PRs catches regressions before code can impact active staging or production environments.
* **Proactive Security Posture:** Integrates static scanners to block credential leaks, outdated dependencies, and dangerous code patterns early in the development lifecycle.
* **Rapid Feedback Loop:** The developer receives immediate feedback directly inside GitHub if a commit breaks syntax, style, or existing functionality.

### Negative
* **Pipeline Maintenance Overhead:** Setting up and managing multiple workflows and scanners requires initial planning and ongoing maintenance to keep dependencies updated.
* **Increased Build Duration:** Running multiple test suites and security scans on every push increases build times and consumes GitHub Actions runner minutes.
* **Handling False Positives:** Dealing with false alerts (e.g. secret scanners matching commit hashes or Nginx host mappings) requires manual triage and adding skip annotations like `# nosemgrep`.

## Decision Date
Approved on 18/07/2026
