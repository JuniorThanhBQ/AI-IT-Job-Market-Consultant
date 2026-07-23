from datetime import datetime, timedelta
from typing import Any

from app.modules.company.models import Company, CompanyBenefit
from app.modules.job.models import Job, Skills
from app.utils.text_parser import (
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
    clean_html_text,
)
from .base_adapter import JobAdapterBase


def from_fptjobs(raw_data: dict[str, Any]) -> Job:
    title = (raw_data.get("title") or "Unknown Title").strip()
    url = (raw_data.get("url") or "").strip()

    raw_desc = raw_data.get("description") or ""
    job_desc = clean_html_text(resolve_job_description(raw_desc, [], None))

    requirements = parse_to_list(raw_data.get("requirements") or "")
    benefits_list = parse_to_list(raw_data.get("benefits") or [])
    benefits = [CompanyBenefit(name=b) for b in benefits_list if b]

    domains = raw_data.get("domains") or ["Telecom", "IT Services"]
    skills = [
        Skills(name=s.strip(), category="Technical") for s in raw_data.get("skills", [])
    ]

    raw_salary = (raw_data.get("salary") or "Negotiable").strip()
    min_salary, max_salary, currency = JobAdapterBase.parse_salary(raw_salary)

    company_location = (raw_data.get("location") or "Vietnam").strip()
    working_hours = (raw_data.get("working_hours") or "FULL_TIME").strip()
    working_model = "At office"

    now = datetime.utcnow()
    expired_date = now + timedelta(days=30)
    valid_through = raw_data.get("expired_date")
    if valid_through:
        try:
            if "-" in valid_through:
                expired_date = datetime.strptime(valid_through[:10], "%Y-%m-%d")
            elif "/" in valid_through:
                expired_date = datetime.strptime(valid_through[:10], "%d/%m/%Y")
        except Exception:
            pass

    scraped_company = (raw_data.get("company") or "FPT Telecom").strip()
    company_name = resolve_company_name(scraped_company, title, url, "fptjobs")
    raw_comp_desc = (
        raw_data.get("company_desc")
        or f"{company_name} is a leading telecom and IT services provider in Vietnam."
    )
    company_desc = clean_html_text(raw_comp_desc).strip()

    comp_vector_context = (
        f"Company Name: {company_name}. Industry: Telecommunications. "
        f"Location: {company_location}. Description: {company_desc}."
    )

    company_obj = Company(
        name=company_name,
        industry="Telecommunications",
        size="1000+ employees",
        location=company_location,
        description=company_desc,
        website="https://fptjobs.com",
        company_type="Corporate",
        country="Vietnam",
        addresses=[company_location],
        vector_context=comp_vector_context,
        benefits=benefits,
    )

    content_hash = JobAdapterBase.calculate_content_hash(
        title, company_name, job_desc, company_location
    )

    domains_str = ", ".join(domains)
    req_str = "\n".join(requirements)

    job_vector_context = (
        f"Job Title: {title}. Company: {company_name}. Location: {company_location}. "
        f"Salary: {min_salary}-{max_salary} {currency}. Working Hours: {working_hours}. "
        f"Domains: {domains_str}. Required Qualifications: {req_str}. "
        f"General Description: {job_desc}."
    )

    return Job(
        title=title,
        job_description=job_desc,
        created_date=now,
        expired_date=expired_date,
        updated_date=now,
        seniority="Junior/Middle",
        min_salary=min_salary,
        max_salary=max_salary,
        currency=currency,
        working_hours=working_hours,
        working_model=working_model,
        status="Open",
        content_hash=content_hash,
        responsibilities=[],
        required_qualifications=requirements,
        nice_to_have=[],
        domains=domains,
        vector_context=job_vector_context,
        source="fptjobs",
        url=url,
        company=company_obj,
        skills=skills,
    )
