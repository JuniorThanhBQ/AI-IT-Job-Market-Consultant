from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.enums import (
    CrawlWebsite,
)
from app.modules.company.models import Company
from app.modules.job.models import Job
from utils.itviec_utils import (
    map_company_type,
    map_country,
    map_currency,
    map_working_hours,
    process_job_vector_context,
)
from utils.text_parser import (
    clean_html_text,
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
)
from utils.topdev_utils import (
    clean_job_description,
    map_seniority_level,
    map_working_model,
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

    comp_vector_context = JobAdapterBase.build_company_vector_context(
        name=company_name,
        slogan=slogan,
        company_type=company_type,
        industry=company_industry,
        size=company_size,
        country=company_country,
        location=company_location,
        description=company_desc,
    )

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

    now = datetime.now(UTC)
    expired_date = (now + timedelta(days=30)).replace(tzinfo=None)
    valid_through = overview_data.get("valid_through")
    if valid_through:
        try:
            expired_date = datetime.strptime(valid_through, "%Y-%m-%d")
        except Exception:
            expired_date = (now + timedelta(days=30)).replace(tzinfo=None)

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
    skills = JobAdapterBase.process_skills(raw_skills)

    content_hash = JobAdapterBase.calculate_content_hash(
        title, company_obj.name, job_desc, company_obj.location
    )

    skills_str, domains_str = ", ".join([s.name for s in skills]), ", ".join(domains)
    resp_str, req_str, nice_str = (
        "\n".join(responsibilities),
        "\n".join(required_qualifications),
        "\n".join(nice_to_have),
    )

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

    return JobAdapterBase.build_job(
        title=title,
        job_desc=job_desc,
        expired_date=expired_date,
        seniority=seniority,
        min_salary=min_salary,
        max_salary=max_salary,
        currency=currency,
        working_hours=working_hours,
        working_model=working_model,
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
