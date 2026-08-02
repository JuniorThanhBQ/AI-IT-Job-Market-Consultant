from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from app.core.enums import (
    JobStatus,
    CrawlWebsite,
)
from app.modules.company.models import Company
from app.modules.job.models import Job, Skills
from app.utils.text_parser import (
    clean_html_text,
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
)
from app.utils.topdev_utils import (
    map_working_model,
    map_seniority_level,
    clean_job_description,
)
from app.utils.itviec_utils import (
    map_company_type,
    map_currency,
    map_country,
    map_working_hours,
    process_job_vector_context,
)
from .base_adapter import JobAdapterBase


def adapter_topdev_company(raw_data: dict[str, Any]) -> Company:
    overview_data = raw_data.get("job_overview")
    if not isinstance(overview_data, dict):
        overview_data = {}

    comp_info = raw_data.get("company_info")
    if not isinstance(comp_info, dict):
        comp_info = {}

    title = (
        overview_data.get("title") or raw_data.get("title") or "Unknown Title"
    ).strip()
    url = (overview_data.get("job_url") or raw_data.get("url") or "").strip()

    scraped_company = (comp_info.get("name") or raw_data.get("company") or "").strip()
    company_name = resolve_company_name(scraped_company, title, url, "topdev")

    company_industry = (
        comp_info.get("industry")
        or raw_data.get("company_industry")
        or "Information Technology"
    ).strip()
    raw_comp_type = comp_info.get("type") or "Product"
    company_type = map_company_type(raw_comp_type)
    company_size = (
        comp_info.get("size") or raw_data.get("company_size") or "50-150 employees"
    ).strip()
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

    raw_comp_country = (
        comp_info.get("country") or raw_data.get("company_country") or "Vietnam"
    )
    company_country = map_country(raw_comp_country)

    company_addresses = comp_info.get("addresses") or []
    if not company_addresses:
        flat_addr = raw_data.get("company_address")
        if flat_addr:
            company_addresses = [flat_addr]

    benefits_list = raw_data.get("benefits") or []
    benefits = [b.strip() for b in benefits_list if b]
    slogan = raw_data.get("slogan") or comp_info.get("slogan") or None

    parts = []
    if company_name:
        parts.append(f"Company Name: {company_name}.")
    if company_type:
        parts.append(f"Type: {company_type}.")
    if company_industry:
        parts.append(f"Industry: {company_industry}.")
    if company_size:
        parts.append(f"Size: {company_size}.")
    if company_country:
        parts.append(f"Country: {company_country}.")
    if company_location:
        parts.append(f"Location: {company_location}.")
    if company_desc:
        parts.append(f"Description: {company_desc}.")
    comp_vector_context = " ".join(parts)

    return Company(
        name=company_name,
        industry=company_industry,
        size=company_size,
        location=company_location,
        description=company_desc,
        website=company_web,
        company_type=company_type,
        country=company_country,
        addresses=company_addresses,
        working_days=None,
        vector_context=comp_vector_context,
        benefits=benefits,
        slogan=slogan,
    )


def adapter_topdev(raw_data: dict[str, Any]) -> Job:
    overview_data = raw_data.get("job_overview")
    if not isinstance(overview_data, dict):
        overview_data = {}

    details_data = raw_data.get("job_details")
    if not isinstance(details_data, dict):
        details_data = {}

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
    job_desc = clean_job_description(job_desc)

    required_qualifications = parse_to_list(qualifications.get("required") or [])
    if not required_qualifications:
        flat_reqs = raw_data.get("requirements") or ""
        required_qualifications = parse_to_list(flat_reqs)

    nice_to_have = parse_to_list(qualifications.get("preferred") or [])
    nice_to_have_key = parse_to_list(qualifications.get("key_competencies") or [])
    if not nice_to_have_key:
        nice_to_have_key = parse_to_list(raw_data.get("nice_to_have") or [])
    nice_to_have = nice_to_have_key + nice_to_have
    domains = parse_to_list(details_data.get("skills") or raw_data.get("skills") or [])

    now = datetime.now(timezone.utc)
    expired_date = (now + timedelta(days=30)).replace(tzinfo=None)
    valid_through = overview_data.get("valid_through")
    if valid_through:
        try:
            expired_date = datetime.strptime(valid_through, "%Y-%m-%d")
        except Exception:
            pass

    raw_salary = (
        overview_data.get("salary") or raw_data.get("salary") or "Negotiable"
    ).strip()
    min_salary, max_salary, parsed_curr_str = JobAdapterBase.parse_salary(raw_salary)
    currency = map_currency(parsed_curr_str)

    working_hours_raw = (
        details_data.get("employment_type")
        or raw_data.get("working_hours")
        or "Fulltime"
    ).strip()
    working_hours = map_working_hours(working_hours_raw)

    raw_work_model = (
        details_data.get("work_type") or raw_data.get("working_model") or "Trực tiếp"
    )
    working_model = map_working_model(raw_work_model)
    url = (overview_data.get("job_url") or raw_data.get("url") or "").strip()

    company_obj = adapter_topdev_company(raw_data)

    raw_skills = details_data.get("skills") or raw_data.get("skills") or []
    skills = [
        Skills(
            name=s.strip(),
            category=JobAdapterBase.classify_skill_category(clean_html_text(s)),
        )
        for s in raw_skills
        if s.strip()
    ]

    content_hash = JobAdapterBase.calculate_content_hash(
        title, company_obj.name, job_desc, company_obj.location
    )

    skills_str = ", ".join([s.name for s in skills])
    domains_str = ", ".join(domains)
    resp_str = "\n".join(responsibilities)
    req_str = "\n".join(required_qualifications)
    nice_str = "\n".join(nice_to_have)

    seniority = map_seniority_level(
        title, details_data.get("level") or raw_data.get("seniority") or ""
    )

    job_vector_context = process_job_vector_context(
        title=title,
        company_name=company_obj.name,
        location=company_obj.location,
        seniority=seniority,
        min_sal=min_salary,
        max_sal=max_salary,
        currency=currency,
        working_hours=working_hours,
        working_model=working_model,
        domains_str=domains_str,
        resp_str=resp_str,
        req_str=req_str,
        nice_str=nice_str,
        job_desc=job_desc,
        skills_str=skills_str,
    )

    return Job(
        title=title,
        job_description=job_desc,
        created_date=now,
        expired_date=expired_date,
        updated_date=now,
        seniority=seniority,
        min_salary=Decimal(str(min_salary)),
        max_salary=Decimal(str(max_salary)),
        currency=currency,
        working_hours=working_hours,
        working_model=working_model,
        status=JobStatus.OPEN,
        content_hash=content_hash,
        responsibilities=responsibilities,
        required_qualifications=required_qualifications,
        nice_to_have=nice_to_have,
        domains=domains,
        vector_context=job_vector_context,
        source=CrawlWebsite.TOPDEV,
        url=url,
        company=company_obj,
        skills=skills,
    )
