from decimal import Decimal


def build_company_vector_context(
    *,
    name: str,
    slogan: str | None = None,
    company_type: str | None = None,
    industry: str | None = None,
    size: str | None = None,
    country: str | None = None,
    location: str | None = None,
    description: str | None = None,
    working_days: str | None = None,
    overtime_policy: str | None = None,
) -> str:
    parts: list[str] = []
    if name:
        parts.append(f"Company Name: {name}.")
    if slogan:
        parts.append(f"Slogan: {slogan}.")
    if company_type:
        parts.append(f"Type: {company_type}.")
    if industry:
        parts.append(f"Industry: {industry}.")
    if size:
        parts.append(f"Size: {size}.")
    if country:
        parts.append(f"Country: {country}.")
    if location:
        parts.append(f"Location: {location}.")
    if working_days:
        parts.append(f"Working Days: {working_days}.")
    if overtime_policy:
        parts.append(f"Overtime Policy: {overtime_policy}.")
    if description:
        parts.append(f"Description: {description}.")
    return " ".join(parts)


def build_job_vector_context(
    *,
    title: str,
    company_name: str | None = None,
    location: str | None = None,
    seniority: str | None = None,
    min_salary: Decimal | float | None = None,
    max_salary: Decimal | float | None = None,
    currency: str | None = None,
    working_hours: str | None = None,
    working_model: str | None = None,
    domains: list[str] | None = None,
    responsibilities: list[str] | None = None,
    required_qualifications: list[str] | None = None,
    nice_to_have: list[str] | None = None,
    skills: list[str] | None = None,
    job_description: str | None = None,
) -> str:
    parts: list[str] = []
    if title:
        parts.append(f"Job Title: {title}.")
    if company_name:
        parts.append(f"Company: {company_name}.")
    if location:
        parts.append(f"Location: {location}.")
    if seniority:
        parts.append(f"Seniority: {seniority}.")
    if min_salary is not None and max_salary is not None:
        parts.append(f"Salary: {min_salary}-{max_salary} {currency or ''}.".strip())
    if working_hours:
        parts.append(f"Working Hours: {working_hours}.")
    if working_model:
        parts.append(f"Working Model: {working_model}.")
    if domains:
        parts.append(f"Domains: {', '.join(domains)}.")
    if responsibilities:
        parts.append(f"Responsibilities: {' '.join(responsibilities[:10])}.")
    if required_qualifications:
        parts.append(
            f"Required Qualifications: {' '.join(required_qualifications[:10])}."
        )
    if nice_to_have:
        parts.append(f"Nice to Have: {' '.join(nice_to_have[:10])}.")
    if skills:
        parts.append(f"Skills: {', '.join(skills)}.")
    if job_description:
        parts.append(f"Description: {job_description[:500]}.")
    return " ".join(parts)
