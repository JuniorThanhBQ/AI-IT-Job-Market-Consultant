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
from agents.tools.adaptive_crawler.crawler_adapter.base_adapter import JobAdapterBase
from app.utils.text_parser import clean_html_text, parse_to_list


def _map_working_model(raw_model: str) -> WorkingModel:
    lowered = (raw_model or "").lower()
    if "remote" in lowered:
        return WorkingModel.REMOTE
    elif "hybrid" in lowered:
        return WorkingModel.HYBRID
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


def crawl4ai_adapter(raw_data: dict[str, Any], source_url: str) -> Job:
    title = (raw_data.get("title") or "Unknown Title").strip()
    job_desc = clean_html_text(raw_data.get("description") or "")
    company_name = (raw_data.get("company_name") or "Unknown Company").strip()
    location = (raw_data.get("location") or "Vietnam").strip()

    now = datetime.now(timezone.utc)
    expired_date = (now + timedelta(days=30)).replace(tzinfo=None)

    raw_salary = (raw_data.get("salary") or "Thỏa Thuận").strip()
    min_salary, max_salary, parsed_curr_str = JobAdapterBase.parse_salary(raw_salary)
    currency = _map_currency(parsed_curr_str)

    seniority = _map_seniority_level(title, "")
    working_model = _map_working_model("On-site")
    working_hours = "Toàn thời gian"

    reqs = raw_data.get("requirements") or []
    required_qualifications = (
        parse_to_list(reqs) if isinstance(reqs, list) else parse_to_list(str(reqs))
    )

    raw_bens = raw_data.get("benefits") or []
    benefits_list = (
        parse_to_list(raw_bens)
        if isinstance(raw_bens, list)
        else parse_to_list(str(raw_bens))
    )
    benefits = [
        CompanyBenefit(name=clean_html_text(b))
        for b in benefits_list
        if clean_html_text(b)
    ]

    raw_skills = raw_data.get("skills") or []
    skills_list = (
        parse_to_list(raw_skills)
        if isinstance(raw_skills, list)
        else parse_to_list(str(raw_skills))
    )
    skills = [
        Skills(
            name=clean_html_text(s),
            category=JobAdapterBase.classify_skill_category(clean_html_text(s)),
        )
        for s in skills_list
        if clean_html_text(s)
    ]

    url = (raw_data.get("apply_url") or source_url).strip()

    content_hash = JobAdapterBase.calculate_content_hash(
        title, company_name, job_desc, location
    )

    company_type = _map_company_type("Product")
    company_industry = "Information Technology"
    company_size = "Unknown"
    company_country = "Vietnam"
    company_desc = ""

    comp_vector_context = (
        f"Company Name: {company_name}. Slogan: None. Type: {company_type}. "
        f"Industry: {company_industry}. Size: {company_size}. Country: {company_country}. "
        f"Location: {location}. Working Days: . Overtime Policy: . "
        f"Description: {company_desc}."
    )

    skills_str = ", ".join([s.name for s in skills])
    req_str = "\n".join(required_qualifications)

    job_vector_context = (
        f"Job Title: {title}. Company: {company_name}. Location: {location}. Seniority: {seniority}. "
        f"Salary: {min_salary}-{max_salary} {currency}. "
        f"Working Hours: {working_hours}. Working Model: {working_model}. "
        f"Domains: . Responsibilities: . Required Qualifications: {req_str}. "
        f"Nice to Have: . General Description: {job_desc}. Skills: {skills_str}."
    )

    company_obj = Company(
        name=company_name,
        industry=company_industry,
        size=company_size,
        location=location,
        description=company_desc,
        website="",
        company_type=company_type,
        country=company_country,
        addresses=[location],
        working_days=None,
        vector_context=comp_vector_context,
        benefits=benefits,
        slogan="",
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
        status=JobStatus.OPEN,
        content_hash=content_hash,
        responsibilities=[],
        required_qualifications=required_qualifications,
        nice_to_have=[],
        domains=[],
        vector_context=job_vector_context,
        source="crawl4ai",
        url=url,
        company=company_obj,
        skills=skills,
    )
