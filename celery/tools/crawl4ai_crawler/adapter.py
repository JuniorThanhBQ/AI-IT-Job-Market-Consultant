from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.enums import (
    CrawlWebsite,
)
from app.modules.company.models import Company
from app.modules.job.models import Job
from tools.adaptive_crawler.crawler_adapter.base_adapter import JobAdapterBase
from utils.text_parser import clean_html_text, parse_to_list
from utils.itviec_utils import (
    map_company_type,
    map_currency,
    map_country,
    map_working_hours,
    map_working_model,
    map_seniority_level,
    process_job_vector_context,
)


def crawl4ai_adapter_company(raw_data: dict[str, Any]) -> Company:
    company_name = (raw_data.get("company_name") or "Unknown Company").strip()
    location = (raw_data.get("location") or "Vietnam").strip()

    company_type = map_company_type("Product")
    company_industry = "Information Technology"
    company_size = "Unknown"
    company_country = map_country("Vietnam")
    company_desc = ""

    raw_bens = raw_data.get("benefits") or []
    benefits = (
        parse_to_list(raw_bens)
        if isinstance(raw_bens, list)
        else parse_to_list(str(raw_bens))
    )
    benefits = [clean_html_text(b).strip() for b in benefits if clean_html_text(b)]

    comp_vector_context = JobAdapterBase.build_company_vector_context(
        name=company_name,
        slogan="",
        company_type=company_type,
        industry=company_industry,
        size=company_size,
        country=company_country,
        location=location,
        description=company_desc,
    )

    return Company(
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


def crawl4ai_adapter(raw_data: dict[str, Any], source_url: str) -> Job:
    title = (raw_data.get("title") or "Unknown Title").strip()
    job_desc = clean_html_text(raw_data.get("description") or "")
    location = (raw_data.get("location") or "Vietnam").strip()

    now = datetime.now(timezone.utc)
    expired_date = (now + timedelta(days=30)).replace(tzinfo=None)

    raw_salary = (raw_data.get("salary") or "Thỏa Thuận").strip()
    min_salary, max_salary, parsed_curr_str = JobAdapterBase.parse_salary(raw_salary)
    currency = map_currency(parsed_curr_str)

    seniority = map_seniority_level(title, "")
    working_model = map_working_model("On-site")
    working_hours = map_working_hours("Toàn thời gian")

    reqs = raw_data.get("requirements") or []
    required_qualifications = (
        parse_to_list(reqs) if isinstance(reqs, list) else parse_to_list(str(reqs))
    )

    raw_skills = raw_data.get("skills") or []
    skills_list = (
        parse_to_list(raw_skills)
        if isinstance(raw_skills, list)
        else parse_to_list(str(raw_skills))
    )
    skills = JobAdapterBase.process_skills(skills_list)

    nice_to_have = raw_data.get("nice_to_have") or []
    nice_to_have = [clean_html_text(n) for n in nice_to_have if clean_html_text(n)]
    url = (raw_data.get("apply_url") or source_url).strip()
    company_obj = crawl4ai_adapter_company(raw_data)
    content_hash = JobAdapterBase.calculate_content_hash(
        title, company_obj.name, job_desc, location
    )

    skills_str, req_str = (
        ", ".join([s.name for s in skills]),
        "\n".join(required_qualifications),
    )
    nice_str = "\n".join(nice_to_have) if nice_to_have else ""

    job_vector_context = process_job_vector_context(
        title=title,
        company_name=company_obj.name,
        location=location,
        seniority=seniority,
        min_sal=min_salary,
        max_sal=max_salary,
        currency=currency,
        working_hours=working_hours,
        working_model=working_model,
        domains_str="",
        resp_str="",
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
        responsibilities=[],
        required_qualifications=required_qualifications,
        nice_to_have=nice_to_have,
        domains=[],
        vector_context=job_vector_context,
        source=CrawlWebsite.FPTJOBS,
        url=url,
        company=company_obj,
        skills=skills,
    )
