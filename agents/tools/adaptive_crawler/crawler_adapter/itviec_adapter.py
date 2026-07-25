from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.enums import (
    CompanyType,
    Currency,
    JobStatus,
    SeniorityLevel,
    WorkingModel,
)
from app.modules.company.models import Company, CompanyBenefit
from app.modules.job.models import Job, Skills
from app.utils.text_parser import (
    clean_html_text,
    parse_to_list,
    resolve_company_name,
    resolve_job_description,
)

from .base_adapter import JobAdapterBase


def _map_working_model(raw_model: str) -> WorkingModel:
    lowered = (raw_model or "").lower()
    if "remote" in lowered:
        return WorkingModel.REMOTE
    elif "hybrid" in lowered:
        return WorkingModel.HYBRID
    elif "office" in lowered or "onsite" in lowered:
        return WorkingModel.ONSITE
    return WorkingModel.ONSITE


def _map_seniority_level(title: str, raw_seniority: str = "") -> SeniorityLevel:
    combined = f"{title} {raw_seniority}".lower()
    if "intern" in combined:
        return SeniorityLevel.INTERN
    elif "fresher" in combined:
        return SeniorityLevel.FRESHER
    elif "junior" in combined:
        return SeniorityLevel.JUNIOR
    elif "senior" in combined:
        return SeniorityLevel.SENIOR
    elif "lead" in combined:
        return SeniorityLevel.LEAD
    elif "manager" in combined:
        return SeniorityLevel.MANAGER
    elif "director" in combined:
        return SeniorityLevel.DIRECTOR
    elif "executive" in combined:
        return SeniorityLevel.EXECUTIVE
    return SeniorityLevel.MID


def _map_company_type(raw_type: str) -> CompanyType:
    lowered = (raw_type or "").lower()
    if "outsource" in lowered or "outsourcing" in lowered:
        return CompanyType.OUTSOURCING
    elif "consulting" in lowered:
        return CompanyType.CONSULTING
    elif "agency" in lowered:
        return CompanyType.AGENCY
    elif "product" in lowered:
        return CompanyType.PRODUCT
    return CompanyType.PRODUCT


def _map_currency(raw_currency: str) -> Currency:
    lowered = (raw_currency or "").lower()
    if "usd" in lowered or "$" in lowered:
        return Currency.USD
    elif "eur" in lowered or "€" in lowered:
        return Currency.EUR
    elif "jpy" in lowered or "¥" in lowered:
        return Currency.JPY
    elif "sgd" in lowered:
        return Currency.SGD
    return Currency.VND


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
    company_industry = (comp_data.get("industry") or "IT Services").strip()
    company_size = (comp_data.get("size") or "50-150 employees").strip()
    company_location = (
        overview_data.get("location") or raw_data.get("location") or "Vietnam"
    ).strip()
    company_desc = f"{company_name} is an active technology employer."
    company_web = ""
    slogan = ""
    raw_comp_type = comp_data.get("type") or "Product"
    company_type = _map_company_type(raw_comp_type)
    company_country = comp_data.get("country") or "Vietnam"
    working_days = comp_data.get("working_days")
    overtime_policy = comp_data.get("overtime_policy")
    company_addresses = comp_data.get("addresses") or [company_location]

    raw_benefits = (
        comp_data.get("benefits")
        or details_data.get("benefits")
        or raw_data.get("benefits")
        or []
    )
    benefits = [
        CompanyBenefit(name=clean_html_text(b))
        for b in raw_benefits
        if clean_html_text(b)
    ]

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
    expired_date = now + timedelta(days=30)
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

    currency = _map_currency(schema_curr or parsed_curr_str)

    working_hours = (
        schema_data.get("employmentType")
        or raw_data.get("working_hours")
        or "Full-time"
    ).strip()

    raw_work_model = (
        overview_data.get("work_model") or raw_data.get("working_model") or "At office"
    )
    working_model = _map_working_model(raw_work_model)
    seniority = _map_seniority_level(title, raw_data.get("seniority", ""))

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
        title, company_name, job_desc, company_location
    )

    comp_vector_context = (
        f"Company Name: {company_name}. Slogan: {slogan or 'N/A'}. Type: {company_type}. "
        f"Industry: {company_industry}. Size: {company_size}. Country: {company_country}. "
        f"Location: {company_location}. Working Days: {working_days or 'N/A'}. "
        f"Overtime Policy: {overtime_policy or 'N/A'}. Description: {company_desc}."
    )

    skills_str = ", ".join([s.name for s in skills])
    domains_str = ", ".join(domains)
    resp_str = "\n".join(responsibilities)
    req_str = "\n".join(required_qualifications)
    nice_str = "\n".join(nice_to_have)

    job_vector_context = (
        f"Job Title: {title}. Company: {company_name}. Location: {company_location}. Seniority: {seniority}. "
        f"Salary: {min_sal}-{max_sal} {currency}. Working Hours: {working_hours}. Working Model: {working_model}. "
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
        company_type=company_type,
        country=company_country,
        addresses=company_addresses,
        working_days=working_days,
        overtime_policy=overtime_policy,
        slogan=slogan,
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
        min_salary=min_sal,
        max_salary=max_sal,
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
        source="itviec",
        url=url,
        company=company_obj,
        skills=skills,
    )
