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
    map_seniority_level,
    map_working_hours,
    map_working_model,
    process_job_vector_context,
)
from utils.text_parser import (
    clean_html_text,
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
)

from .base_adapter import JobAdapterBase


def adapter_itjobs_company(raw_data: dict[str, Any]) -> Company:
    comp_data = raw_data.get("company")
    if not isinstance(comp_data, dict):
        comp_data = {}

    scraped_company = (comp_data.get("name") or raw_data.get("company") or "").strip()
    title = (
        raw_data.get("job", {}).get("title") or raw_data.get("title") or ""
    ).strip()
    url = (
        raw_data.get("job", {}).get("apply_url") or raw_data.get("url") or ""
    ).strip()
    company_name = resolve_company_name(scraped_company, title, url, "itjobs")

    company_industry = "Information Technology"
    company_size = (
        comp_data.get("size") or raw_data.get("company_size") or "25-99"
    ).strip()
    company_location = (
        raw_data.get("job", {}).get("location") or raw_data.get("location") or "Vietnam"
    ).strip()
    raw_comp_desc = (
        comp_data.get("company_description")
        or raw_data.get("company_description")
        or ""
    )
    company_desc = clean_html_text(raw_comp_desc).strip()
    company_web = ""

    raw_comp_type = comp_data.get("type") or raw_data.get("company_type") or "Product"
    company_type = map_company_type(raw_comp_type)

    raw_comp_country = (
        comp_data.get("country") or raw_data.get("company_country") or "Vietnam"
    )
    company_country = map_country(raw_comp_country)

    company_address = comp_data.get("address") or raw_data.get("company_address")
    company_addresses = [company_address] if company_address else []

    slogan = raw_data.get("company_slogan") or ""

    raw_benefits = raw_data.get("benefits") or []
    benefits = [clean_html_text(b).strip() for b in raw_benefits if clean_html_text(b)]

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


def adapter_itjobs(raw_data: dict[str, Any]) -> Job:
    job_data = raw_data.get("job")
    if not isinstance(job_data, dict):
        job_data = {}

    requirements_data = raw_data.get("requirements")
    if not isinstance(requirements_data, dict):
        requirements_data = {}

    title = (job_data.get("title") or raw_data.get("title") or "Unknown Title").strip()

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

    general_reqs = parse_to_list(requirements_data.get("general") or [])
    tech_stack = parse_to_list(requirements_data.get("tech_stack") or [])
    if not general_reqs and not tech_stack:
        flat_reqs = raw_data.get("requirements") or ""
        required_qualifications = parse_to_list(flat_reqs)
    else:
        required_qualifications = general_reqs + tech_stack

    now = datetime.now(UTC)
    expired_date = (now + timedelta(days=30)).replace(tzinfo=None)

    raw_salary = (
        job_data.get("salary") or raw_data.get("salary") or "Thỏa Thuận"
    ).strip()
    min_salary, max_salary, parsed_curr_str = JobAdapterBase.parse_salary(raw_salary)
    currency = map_currency(parsed_curr_str)

    raw_seniority = (
        job_data.get("experience_level") or raw_data.get("seniority") or "Junior/Middle"
    ).strip()
    seniority = map_seniority_level(title, raw_seniority)

    working_hours_raw = (
        job_data.get("type") or raw_data.get("working_hours") or "Toàn thời gian"
    ).strip()
    working_hours = map_working_hours(working_hours_raw)

    working_model = map_working_model("On-site")

    url = (job_data.get("apply_url") or raw_data.get("url") or "").strip()
    if url and not url.startswith("http"):
        url = f"https://itjobs.com.vn{url}"

    company_obj = adapter_itjobs_company(raw_data)

    raw_skills = raw_data.get("technical_skills_tags") or raw_data.get("skills") or []
    skills = JobAdapterBase.process_skills(raw_skills)

    content_hash = JobAdapterBase.calculate_content_hash(
        title, company_obj.name, job_desc, company_obj.location
    )

    skills_str, resp_str = (
        ", ".join([s.name for s in skills]),
        "\n".join(responsibilities),
    )
    req_str = "\n".join(required_qualifications)

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
        domains_str="",
        resp_str=resp_str,
        req_str=req_str,
        nice_str="",
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
        responsibilities=[],
        required_qualifications=required_qualifications,
        nice_to_have=[],
        domains=[],
        vector_context=job_vector_context,
        source=CrawlWebsite.ITJOBS,
        url=url,
        company=company_obj,
        skills=skills,
    )
