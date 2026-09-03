# ADR-07: Decision on Input Security Validation Framework and Code Formatting Exclusion for Models

## Status
Accepted

## Context
FastAPI application accepts user-submitted profiles, biographies, career goals, and chat queries. This exposes the backend database and internal shell systems to cross-site scripting (XSS), SQL injection (SQLi), and command injection attacks. To prevent malicious input, it need a centralized input security validation framework.

At the same time, the project use SQLModel/SQLAlchemy for database models. In SQLModel, establishing relationships between models requires using quoted string type annotations to prevent circular import loops. However, our code formatting tool (Ruff) automatically cleans type annotations at lint/format time, resolving quotes and breaking the lazy-loaded registry at runtime, which crashes the server.

## Decision
1. **Security Validation Wrapper:** Implement custom validation types `SafeStr` and `SafeEmailStr` using regex filters and the `email-validator` library. Substitute standard `str` and `EmailStr` validations in all Pydantic schemas with these new types.
2. **Ruff Model Exclusion:** Update the `pyproject.toml` tool configuration to completely exclude `**/models.py` files from formatting checks.

## Rationale
1. **Centralized Security Enforcement:** Wrapping the validation directly into Pydantic input types ensures that FastAPI sanitizes all incoming requests automatically before they reach any services or controllers.
2. **Registry Protection:** Excluding SQLModel files from Ruff formatting preserves the quotes around lazy relationship annotations. This keeps the SQLModel runtime registry intact and avoids server crashes without sacrificing overall codebase formatting.

## Consequences
### Positive
* **Automatic Threat Mitigation:** Input fields are validated by default, blocking SQLi and XSS payloads at the API gateway layer.
* **Stable Model Registry:** SQLModel relationships can use Python's delayed evaluations safely without being formatted away.

### Negative
* **Manual Regex Maintenance:** The validation depends on static regex filters which must be updated as new injection payloads are discovered.
* **Lax Formatting on Models:** Code styling issues inside `models.py` files will not be caught automatically by Ruff, requiring developers to format them manually.

## Decision Date
22/08/2026
