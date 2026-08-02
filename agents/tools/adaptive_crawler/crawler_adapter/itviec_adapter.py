from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from app.core.enums import (
    CrawlWebsite,
    JobStatus,
)
from app.modules.company.models import Company
from app.modules.job.models import Job, Skills
from app.utils.text_parser import (
    clean_html_text,
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
)
from app.utils.itviec_utils import (
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
            val = b.get("name")
        elif hasattr(b, "name"):
            val = b.name
        else:
            val = str(b)
        cleaned = clean_html_text(val)
        if cleaned:
            benefits.append(cleaned)

    vector_context = comp_data.get("vector_context")
    if not vector_context:
        parts = []
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
        if company_country:
            parts.append(f"Country: {company_country}.")
        if location:
            parts.append(f"Location: {location}.")
        if working_days:
            parts.append(f"Working Days: {working_days}.")
        if overtime_policy:
            parts.append(f"Overtime Policy: {overtime_policy}.")
        if description:
            parts.append(f"Description: {description}.")
        vector_context = " ".join(parts)

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
    comp_data = (
        raw_data.get("company") if isinstance(raw_data.get("company"), dict) else {}
    )
    overview_data = (
        raw_data.get("job_overview")
        if isinstance(raw_data.get("job_overview"), dict)
        else {}
    )
    details_data = (
        raw_data.get("job_details")
        if isinstance(raw_data.get("job_details"), dict)
        else {}
    )
    schema_data = (
        raw_data.get("schema_data")
        if isinstance(raw_data.get("schema_data"), dict)
        else {}
    )

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
            pass

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
    skills = [
        Skills(
            name=clean_html_text(s),
            category=JobAdapterBase.classify_skill_category(clean_html_text(s)),
        )
        for s in raw_skills
        if clean_html_text(s)
    ]

    content_hash = JobAdapterBase.calculate_content_hash(
        title, company_obj.name, job_desc, company_obj.location
    )

    skills_str = ", ".join([s.name for s in skills])
    domains_str = ", ".join(domains)
    resp_str = "\n".join(responsibilities)
    req_str = "\n".join(required_qualifications)
    nice_str = "\n".join(nice_to_have)

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

    return Job(
        title=title,
        job_description=job_desc,
        created_date=now,
        expired_date=expired_date,
        updated_date=now,
        seniority=seniority,
        min_salary=Decimal(str(min_sal)),
        max_salary=Decimal(str(max_sal)),
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
        source=CrawlWebsite.ITVIEC,
        url=url,
        company=company_obj,
        skills=skills,
    )
