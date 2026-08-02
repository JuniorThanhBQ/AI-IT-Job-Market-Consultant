from difflib import SequenceMatcher
from typing import Any

from app.core.enums import (
    CompanyType,
    CountryEnum,
    Currency,
    SeniorityLevel,
    WorkingModel,
)
from app.utils.utils import parse_seniority_level


def parse_skills_paragraph(div_elem):
    reqs_list = []
    nice_list = []
    target = reqs_list

    for elem in div_elem.children:
        if not hasattr(elem, "name") or not elem.name:
            continue
        elem_txt = elem.get_text(strip=True).lower()
        if elem.name in ["p", "div", "strong", "h4", "h5"]:
            if "nice to have" in elem_txt or "preferred" in elem_txt:
                target = nice_list
                continue
            elif (
                "qualifications" in elem_txt
                or "requirements" in elem_txt
                or "must have" in elem_txt
                or "skills" in elem_txt
            ):
                target = reqs_list
                continue

        if elem.name in ["ul", "ol"]:
            lis = [
                li.get_text(strip=True)
                for li in elem.find_all("li")
                if li.get_text(strip=True)
            ]
            target.extend(lis)
        elif elem.name == "p" and not elem.find("strong"):
            ptxt = elem.get_text(strip=True)
            if ptxt:
                target.append(ptxt)

    if not reqs_list and not nice_list:
        lis = [
            li.get_text(strip=True)
            for li in div_elem.select("li")
            if li.get_text(strip=True)
        ]
        if lis:
            reqs_list = lis
        else:
            c_txt = div_elem.get_text(separator="\n", strip=True)
            if c_txt:
                reqs_list = [c_txt]

    return reqs_list, nice_list


def map_working_model(raw_model: str) -> WorkingModel:
    lowered = (raw_model or "").lower()
    if "remote" in lowered:
        return WorkingModel.REMOTE
    elif "hybrid" in lowered:
        return WorkingModel.HYBRID
    elif "office" in lowered or "onsite" in lowered:
        return WorkingModel.ONSITE
    return WorkingModel.ONSITE


def map_seniority_level(title: str, raw_seniority: str = "") -> SeniorityLevel:
    return parse_seniority_level(title, raw_seniority)


def map_company_type(raw_type: str) -> CompanyType:
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


def map_currency(raw_currency: str) -> Currency:
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


def map_country(raw_country: str) -> CountryEnum:
    lowered = (raw_country or "").lower().strip()
    if not lowered:
        return CountryEnum.VIETNAM
    for enum_val in CountryEnum:
        if enum_val.value.lower() == lowered:
            return enum_val
    if "vietnam" in lowered:
        return CountryEnum.VIETNAM
    elif "united states" in lowered or "us" == lowered or "usa" in lowered:
        return CountryEnum.UNITED_STATES
    elif "singapore" in lowered:
        return CountryEnum.SINGAPORE
    elif "japan" in lowered:
        return CountryEnum.JAPAN
    elif "south korea" in lowered or "korea" in lowered:
        return CountryEnum.SOUTH_KOREA
    return CountryEnum.VIETNAM


def map_working_hours(working_hours_raw: str | None) -> str:
    if not working_hours_raw:
        return "FULL_TIME"

    val = working_hours_raw.strip().upper().replace("-", "_").replace(" ", "_")
    if "FULL" in val:
        return "FULL_TIME"
    if "PART" in val:
        return "PART_TIME"
    if "CONTRACT" in val:
        return "CONTRACTOR"
    if "TEMP" in val:
        return "TEMPORARY"
    return "OTHER"


def process_job_vector_context(
    title: str,
    company_name: str | None,
    location: str | None,
    seniority: Any,
    min_sal: Any,
    max_sal: Any,
    currency: Any,
    working_hours: str | None,
    working_model: Any,
    domains_str: str | None,
    resp_str: str | None,
    req_str: str | None,
    nice_str: str | None,
    job_desc: str | None,
    skills_str: str | None,
) -> str:
    parts = []
    if title:
        parts.append(f"Job Title: {title}.")
    if company_name:
        parts.append(f"Company: {company_name}.")
    if location:
        parts.append(f"Location: {location}.")
    if seniority:
        parts.append(f"Seniority: {seniority}.")

    if min_sal is not None and max_sal is not None:
        try:
            min_val = float(min_sal)
            max_val = float(max_sal)
        except ValueError, TypeError:
            min_val, max_val = 0.0, 0.0
        if min_val > 0.0 or max_val > 0.0:
            parts.append(f"Salary: {min_sal}-{max_sal} {currency}.")

    if working_hours:
        parts.append(f"Working Hours: {working_hours}.")
    if working_model:
        parts.append(f"Working Model: {working_model}.")
    if domains_str:
        parts.append(f"Domains: {domains_str}.")
    resp_clean = ""
    if resp_str:
        resp_lines = [line.strip() for line in resp_str.split("\n") if line.strip()]
        resp_clean = "\n".join(resp_lines[:10])

    req_clean = ""
    if req_str:
        req_lines = [line.strip() for line in req_str.split("\n") if line.strip()]
        req_clean = "\n".join(req_lines[:10])

    if resp_clean:
        parts.append(f"Responsibilities: {resp_clean}.")
    if req_clean:
        parts.append(f"Required Qualifications: {req_clean}.")
    if nice_str:
        parts.append(f"Nice to Have: {nice_str}.")

    base_parts = parts.copy()
    if skills_str:
        base_parts.append(f"Skills: {skills_str}.")
    base_text = " ".join(base_parts)
    base_words = len(base_text.split())

    include_desc = bool(job_desc)
    if job_desc:
        if resp_clean and SequenceMatcher(None, resp_clean, job_desc).ratio() > 0.6:
            include_desc = False
        elif req_clean and SequenceMatcher(None, req_clean, job_desc).ratio() > 0.6:
            include_desc = False

    if include_desc and job_desc:
        max_desc_words = 500 - base_words - 3
        if max_desc_words <= 0:
            include_desc = False
        else:
            desc_words = job_desc.split()
            if len(desc_words) > max_desc_words:
                job_desc = " ".join(desc_words[:max_desc_words])

    if include_desc and job_desc:
        parts.append(f"General Description: {job_desc}.")

    if skills_str:
        parts.append(f"Skills: {skills_str}.")

    return " ".join(parts)
