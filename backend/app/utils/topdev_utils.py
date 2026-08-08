import re

from app.core.enums import SeniorityLevel, WorkingModel
from app.utils.utils import parse_seniority_level


def extract_company_meta(company_search_context, keyword: str) -> str | None:
    lbl = company_search_context.find(
        lambda tag: (
            tag.name == "span"
            and tag.get_text(strip=True)
            and keyword in tag.get_text(strip=True).lower()
        )
    )
    if lbl and lbl.parent:
        val_span = lbl.parent.find(
            "span", class_=lambda c: c and "font-semibold" in c and "text-text-700" in c
        )
        if val_span:
            return re.sub(r"\s+", " ", val_span.get_text(separator=" ")).strip()
        for s in lbl.parent.find_all("span"):
            if s != lbl:
                return re.sub(r"\s+", " ", s.get_text(separator=" ")).strip()

    return None


def map_working_model(raw_model: str) -> WorkingModel:
    lowered = (raw_model or "").lower()
    if "remote" in lowered or "từ xa" in lowered:
        return WorkingModel.REMOTE
    elif "hybrid" in lowered or "linh hoạt" in lowered:
        return WorkingModel.HYBRID
    elif (
        "office" in lowered
        or "onsite" in lowered
        or "trực tiếp" in lowered
        or "tại văn phòng" in lowered
    ):
        return WorkingModel.ONSITE
    return WorkingModel.ONSITE


def map_seniority_level(title: str, raw_seniority: str = "") -> SeniorityLevel:
    return parse_seniority_level(title, raw_seniority)


def clean_job_description(job_desc: str | None) -> str:
    if not job_desc:
        return "No extra general information"

    lowered_desc = job_desc.lower()
    keywords = [
        "your role & responsibilities",
        "role & responsibilities",
        "responsibilities",
    ]
    earliest_idx = -1
    for kw in keywords:
        idx = lowered_desc.find(kw)
        if idx != -1:
            if earliest_idx == -1 or idx < earliest_idx:
                earliest_idx = idx

    if earliest_idx != -1:
        job_desc = job_desc[:earliest_idx].strip()

    if not job_desc or job_desc.strip() == "":
        return "No extra general information"

    return job_desc
