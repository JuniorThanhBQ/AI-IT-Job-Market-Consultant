from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.enums import (
    CrawlWebsite,
)
from app.modules.company.models import Company
from app.modules.job.models import Job
from utils.text_parser import (
    clean_html_text,
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
)
from utils.itviec_utils import (
    map_working_model,
    map_seniority_level,
    map_company_type,
    map_currency,
    map_country,
    map_working_hours,
    process_job_vector_context,
)

from .base_adapter import JobAdapterBase


def adapter_itviec_company(raw_data: dict[str, Any]) -> Company:
    if (
        "company" in raw_data
        and isinstance(raw_data["company"], dict)
        and "name" in raw_data["company"]
    ):
        comp_data = raw_data["company"]
    else:
        comp_data = raw_data

    name = (comp_data.get("name") or "").strip()
    industry = (comp_data.get("industry") or "IT Services").strip()
    size = (comp_data.get("size") or "50-150 employees").strip()
    location = (comp_data.get("location") or "Vietnam").strip()
    description = (comp_data.get("description") or "").strip()
    website = (comp_data.get("website") or "").strip()
    slogan = (comp_data.get("slogan") or "").strip()
    raw_comp_type = comp_data.get("company_type") or comp_data.get("type") or "Product"
    company_type = map_company_type(raw_comp_type)
    company_country = map_country(comp_data.get("country") or "Vietnam")
    working_days = comp_data.get("working_days")
    overtime_policy = comp_data.get("overtime_policy")
    addresses = comp_data.get("addresses") or [location]

    raw_benefits = comp_data.get("benefits") or []
    benefits = []
    for b in raw_benefits:
        if isinstance(b, dict):
            val_raw = b.get("name")
            val = str(val_raw) if val_raw is not None else ""
        elif hasattr(b, "name"):
            val_raw = getattr(b, "name")
            val = str(val_raw) if val_raw is not None else ""
        else:
            val = str(b)
        cleaned = clean_html_text(val)
        if cleaned:
            benefits.append(cleaned)

    vector_context = comp_data.get(
        "vector_context"
    ) or JobAdapterBase.build_company_vector_context(
        name=name,
        slogan=slogan,
        company_type=company_type,
        industry=industry,
        size=size,
        country=company_country,
        location=location,
        description=description,
        working_days=working_days,
        overtime_policy=overtime_policy,
    )

    return Company(
        name=name,
        industry=industry,
        size=size,
        location=location,
        description=description,
        website=website,
        company_type=company_type,
        country=company_country,
        addresses=addresses,
        working_days=working_days,
        overtime_policy=overtime_policy,
        slogan=slogan,
        vector_context=vector_context,
        benefits=benefits,
    )


def adapter_itviec(raw_data: dict[str, Any]) -> Job:
    raw_company = raw_data.get("company")
    comp_data = raw_company if isinstance(raw_company, dict) else {}
    raw_overview = raw_data.get("job_overview")
    overview_data = raw_overview if isinstance(raw_overview, dict) else {}
    raw_details = raw_data.get("job_details")
    details_data = raw_details if isinstance(raw_details, dict) else {}
    raw_schema = raw_data.get("schema_data")
    schema_data = raw_schema if isinstance(raw_schema, dict) else {}

    title = (
        raw_data.get("title") or raw_data.get("job_title") or "Unknown Title"
    ).strip()
    url = (raw_data.get("url") or "").strip()

    scraped_comp_name = (comp_data.get("name") or raw_data.get("company") or "").strip()
    company_name = resolve_company_name(scraped_comp_name, title, url, "itviec")
    company_location = (
        overview_data.get("location") or raw_data.get("location") or "Vietnam"
    ).strip()
    company_desc = (
        comp_data.get("description")
        or f"{company_name} is an active technology employer."
    ).strip()

    raw_benefits = (
        comp_data.get("benefits")
        or details_data.get("benefits")
        or raw_data.get("benefits")
        or []
    )

    comp_copy = dict(comp_data)
    comp_copy["name"] = company_name
    comp_copy["location"] = company_location
    comp_copy["description"] = company_desc
    comp_copy["benefits"] = raw_benefits

    company_obj = adapter_itviec_company(comp_copy)

    raw_job_desc = details_data.get("description") or raw_data.get("description")
    responsibilities = parse_to_list(
        details_data.get("responsibilities") or raw_data.get("responsibilities") or []
    )
    if not responsibilities and raw_job_desc:
        responsibilities = parse_to_list(raw_job_desc)

    job_desc = clean_html_text(
        resolve_job_description(
            raw_job_desc if isinstance(raw_job_desc, str) else None,
            responsibilities,
            None,
        )
    )

    required_qualifications = parse_to_list(
        details_data.get("requirements") or raw_data.get("requirements") or []
    )
    nice_to_have = parse_to_list(
        details_data.get("nice_to_have") or raw_data.get("nice_to_have") or []
    )

    domains = parse_to_list(
        overview_data.get("domains") or raw_data.get("domains") or []
    )

    now = datetime.now(timezone.utc)
    valid_through = schema_data.get("validThrough")
    expired_date = (now + timedelta(days=30)).replace(tzinfo=None)
    if valid_through:
        try:
            expired_date = datetime.strptime(valid_through[:10], "%Y-%m-%d")
        except Exception:
            expired_date = (now + timedelta(days=30)).replace(tzinfo=None)

    raw_salary = ""
    base_salary_data = schema_data.get("baseSalary")
    schema_curr = None
    schema_min_sal = None
    schema_max_sal = None

    if isinstance(base_salary_data, dict):
        schema_curr = base_salary_data.get("currency")
        val_obj = base_salary_data.get("value")
        if isinstance(val_obj, dict):
            min_v = val_obj.get("minValue")
            max_v = val_obj.get("maxValue")
            val_str = str(val_obj.get("value") or "").strip()

            if min_v is not None:
                try:
                    schema_min_sal = float(min_v)
                except ValueError, TypeError:
                    pass
            if max_v is not None:
                try:
                    schema_max_sal = float(max_v)
                except ValueError, TypeError:
                    pass

            if not raw_salary and val_str and "you'll love it" not in val_str.lower():
                raw_salary = val_str

    if not raw_salary:
        raw_salary = (
            overview_data.get("salary") or raw_data.get("salary") or "Negotiable"
        ).strip()

    min_sal, max_sal, parsed_curr_str = JobAdapterBase.parse_salary(raw_salary)

    if min_sal == 0.0 and schema_min_sal is not None:
        min_sal = schema_min_sal
    if max_sal == 0.0 and schema_max_sal is not None:
        max_sal = schema_max_sal

    currency = map_currency(schema_curr or parsed_curr_str)

    raw_working_hours = (
        schema_data.get("employmentType")
        or raw_data.get("working_hours")
        or "Full-time"
    ).strip()
    working_hours = map_working_hours(raw_working_hours)

    raw_work_model = (
        overview_data.get("work_model") or raw_data.get("working_model") or "At office"
    )
    working_model = map_working_model(raw_work_model)
    seniority = map_seniority_level(title, raw_data.get("seniority", ""))

    raw_skills = overview_data.get("skills") or raw_data.get("skills") or []
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

    job_vector_context = process_job_vector_context(
        title=title,
        company_name=company_obj.name,
        location=company_obj.location,
        seniority=seniority,
        min_sal=min_sal,
        max_sal=max_sal,
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
        min_salary=min_sal,
        max_salary=max_sal,
        currency=currency,
        working_hours=working_hours,
        working_model=working_model,
        content_hash=content_hash,
        responsibilities=responsibilities,
        required_qualifications=required_qualifications,
        nice_to_have=nice_to_have,
        domains=domains,
        vector_context=job_vector_context,
        source=CrawlWebsite.ITVIEC,
        url=url,
        company=company_obj,
        skills=skills,
    )
