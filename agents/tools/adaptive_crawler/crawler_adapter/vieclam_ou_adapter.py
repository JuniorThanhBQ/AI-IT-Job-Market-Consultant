from datetime import datetime, timedelta
from typing import Any

from app.modules.company.models import Company, CompanyBenefit
from app.modules.job.models import Job
from app.utils.text_parser import (
    clean_html_text,
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
)

from .base_adapter import JobAdapterBase


def from_vieclam_ou(raw_data: dict[str, Any]) -> Job:
    title = (raw_data.get("title") or "Unknown Title").strip()
    scraped_company = (raw_data.get("company") or "").strip()
    url = (raw_data.get("url") or "").strip()

    raw_desc = raw_data.get("description")
    if isinstance(raw_desc, list):
        responsibilities = parse_to_list(raw_desc)
    else:
        desc_str = (raw_desc or "").strip()
        responsibilities = parse_to_list(desc_str)

    job_desc = clean_html_text(
        resolve_job_description(
            raw_data.get("description") if isinstance(raw_desc, str) else None,
            responsibilities,
            None,
        )
    )

    flat_reqs = raw_data.get("requirements") or ""
    required_qualifications = parse_to_list(flat_reqs)

    now = datetime.utcnow()
    expired_date = now + timedelta(days=30)
    exp_str = raw_data.get("expired_date")
    if exp_str:
        try:
            expired_date = datetime.strptime(exp_str, "%d/%m/%Y")
        except ValueError:
            pass

    raw_salary = (raw_data.get("salary") or "Thỏa Thuận").strip()
    min_salary, max_salary, currency = JobAdapterBase.parse_salary(raw_salary)

    seniority = (raw_data.get("seniority") or "Nhân viên").strip()
    working_hours = (raw_data.get("working_hours") or "Toàn thời gian").strip()
    working_model = "On-site"

    if url and not url.startswith("http"):
        url = f"https://vieclam.ou.edu.vn{url}"

    company_name = resolve_company_name(scraped_company, title, url, "vieclam_ou")

    company_industry = (raw_data.get("industry") or "Khác").strip()
    company_size = "Unknown"
    company_location = (raw_data.get("location") or "Vietnam").strip()
    raw_comp_desc = raw_data.get("company_desc") or raw_data.get("description") or ""
    company_desc = clean_html_text(raw_comp_desc).strip()
    company_web = ""

    company_type = "Unknown"
    company_country = "Vietnam"
    company_address = ""

    benefits_list = raw_data.get("benefits") or []
    benefits = [CompanyBenefit(name=b) for b in benefits_list if b]

    skills = []

    content_hash = JobAdapterBase.calculate_content_hash(
        title, company_name, job_desc, company_location
    )

    comp_vector_context = (
        f"Company Name: {company_name}. Slogan: None. Type: {company_type}. "
        f"Industry: {company_industry}. Size: {company_size}. Country: {company_country}. "
        f"Location: {company_location}. Working Days: . Overtime Policy: . "
        f"Description: {company_desc}."
    )

    skills_str = ", ".join([s.name for s in skills])
    resp_str = "\n".join(responsibilities)
    req_str = "\n".join(required_qualifications)

    job_vector_context = (
        f"Job Title: {title}. Company: {company_name}. Location: {company_location}. Seniority: {seniority}. "
        f"Salary: {min_salary}-{max_salary} {currency}. "
        f"Working Hours: {working_hours}. Working Model: {working_model}. "
        f"Domains: . Responsibilities: {resp_str}. Required Qualifications: {req_str}. "
        f"Nice to Have: . General Description: {job_desc}. Skills: {skills_str}."
    )

    company_obj = Company(
        name=company_name,
        industry=company_industry,
        size=company_size,
        location=company_location,
        description=company_desc,
        website=company_web,
        company_type=company_type,
        country=company_country,
        addresses=[company_address] if company_address else [],
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
        seniority=seniority,
        min_salary=min_salary,
        max_salary=max_salary,
        currency=currency,
        working_hours=working_hours,
        working_model=working_model,
        status="Open",
        content_hash=content_hash,
        responsibilities=responsibilities,
        required_qualifications=required_qualifications,
        nice_to_have=[],
        domains=[],
        vector_context=job_vector_context,
        source="vieclam_ou",
        url=url,
        company=company_obj,
        skills=skills,
    )
