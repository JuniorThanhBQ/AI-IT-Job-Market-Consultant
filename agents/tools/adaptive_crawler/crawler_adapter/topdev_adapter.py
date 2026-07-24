from datetime import datetime, timedelta
from typing import Any

from app.modules.company.models import Company, CompanyBenefit
from app.modules.job.models import Job, Skills
from app.utils.text_parser import (
    clean_html_text,
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
)

from .base_adapter import JobAdapterBase


def from_topdev(raw_data: dict[str, Any]) -> Job:
    overview_data = raw_data.get("job_overview")
    if not isinstance(overview_data, dict):
        overview_data = {}

    details_data = raw_data.get("job_details")
    if not isinstance(details_data, dict):
        details_data = {}

    comp_info = raw_data.get("company_info")
    if not isinstance(comp_info, dict):
        comp_info = {}

    qualifications = raw_data.get("qualifications")
    if not isinstance(qualifications, dict):
        qualifications = {}

    title = (
        overview_data.get("title") or raw_data.get("title") or "Unknown Title"
    ).strip()

    raw_desc = raw_data.get("description")

    responsibilities = parse_to_list(raw_data.get("responsibilities") or [])
    if not responsibilities:
        responsibilities = parse_to_list(raw_desc or [])

    job_desc = clean_html_text(
        resolve_job_description(
            raw_desc if isinstance(raw_desc, str) else None, responsibilities, None
        )
    )

    required_qualifications = parse_to_list(qualifications.get("required") or [])
    if not required_qualifications:
        flat_reqs = raw_data.get("requirements") or ""
        required_qualifications = parse_to_list(flat_reqs)

    preferred_list = parse_to_list(qualifications.get("preferred") or [])
    nice_to_have = parse_to_list(qualifications.get("key_competencies") or [])
    if not nice_to_have:
        nice_to_have = parse_to_list(raw_data.get("nice_to_have") or [])
    nice_to_have = nice_to_have + preferred_list
    domains = parse_to_list(details_data.get("skills") or raw_data.get("skills") or [])

    now = datetime.utcnow()
    expired_date = now + timedelta(days=30)
    valid_through = overview_data.get("valid_through")
    if valid_through:
        try:
            expired_date = datetime.strptime(valid_through, "%Y-%m-%d")
        except Exception:
            pass

    raw_salary = (
        overview_data.get("salary") or raw_data.get("salary") or "Negotiable"
    ).strip()
    min_salary, max_salary, currency = JobAdapterBase.parse_salary(raw_salary)

    working_hours = (
        details_data.get("employment_type")
        or raw_data.get("working_hours")
        or "Fulltime"
    ).strip()
    working_model = (
        details_data.get("work_type") or raw_data.get("working_model") or "Trực tiếp"
    ).strip()
    url = (overview_data.get("job_url") or raw_data.get("url") or "").strip()

    scraped_company = (comp_info.get("name") or raw_data.get("company") or "").strip()
    company_name = resolve_company_name(scraped_company, title, url, "topdev")

    company_industry = (comp_info.get("industry") or "Information Technology").strip()
    company_size = "50-150 employees"
    company_location = (
        overview_data.get("location") or raw_data.get("location") or "Vietnam"
    ).strip()
    raw_comp_desc = (
        comp_info.get("description")
        or raw_data.get("description")
        or f"{company_name} is an active employer in the IT market."
    )
    company_desc = clean_html_text(raw_comp_desc).strip()
    company_web = (comp_info.get("profile_url") or "").strip()

    company_country = (
        comp_info.get("country") or raw_data.get("company_country") or "Vietnam"
    )
    company_addresses = comp_info.get("addresses") or []
    if not company_addresses:
        flat_addr = raw_data.get("company_address")
        if flat_addr:
            company_addresses = [flat_addr]

    benefits_list = raw_data.get("benefits") or []
    benefits = [CompanyBenefit(name=b) for b in benefits_list if b]

    raw_skills = details_data.get("skills") or raw_data.get("skills") or []
    skills = [
        Skills(name=s.strip(), category="Technical") for s in raw_skills if s.strip()
    ]

    content_hash = JobAdapterBase.calculate_content_hash(
        title, company_name, job_desc, company_location
    )

    comp_vector_context = (
        f"Company Name: {company_name}. Slogan: None. Type: None. "
        f"Industry: {company_industry}. Size: {company_size}. Country: {company_country}. "
        f"Location: {company_location}. Working Days: . Overtime Policy: . "
        f"Description: {company_desc}."
    )

    skills_str = ", ".join([s.name for s in skills])
    domains_str = ", ".join(domains)
    resp_str = "\n".join(responsibilities)
    req_str = "\n".join(required_qualifications)
    nice_str = "\n".join(nice_to_have)

    job_vector_context = (
        f"Job Title: {title}. Company: {company_name}. Location: {company_location}. "
        f"Seniority: {details_data.get('level')}. "
        f"Salary: {min_salary}-{max_salary} {currency}. Working Hours: {working_hours}. Working Model: {working_model}. "
        f"Domains: {domains_str}. Responsibilities: {resp_str}. Required Qualifications: {req_str}. "
        f"Nice to Have: {nice_str}. General Description: {job_desc}. Skills: {skills_str}."
    )

    company_obj = Company(
        name=company_name,
        industry=company_industry,
        size=company_size,
        location=company_location,
        description=company_desc,
        website=company_web,
        company_type=None,
        country=company_country,
        addresses=company_addresses,
        working_days=None,
        vector_context=comp_vector_context,
        benefits=benefits,
    )

    return Job(
        title=title,
        job_description=job_desc,
        created_date=now,
        expired_date=expired_date,
        updated_date=now,
        seniority=(
            details_data.get("level") or raw_data.get("seniority") or "Junior/Middle"
        ).strip(),
        min_salary=min_salary,
        max_salary=max_salary,
        currency=currency,
        working_hours=working_hours,
        working_model=working_model,
        status=overview_data.get("status") or raw_data.get("status") or "Open",
        content_hash=content_hash,
        responsibilities=responsibilities,
        required_qualifications=required_qualifications,
        nice_to_have=nice_to_have,
        domains=domains,
        vector_context=job_vector_context,
        source="topdev",
        url=url,
        company=company_obj,
        skills=skills,
    )
