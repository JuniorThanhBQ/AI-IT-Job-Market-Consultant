import re
from typing import Any

import tldextract
from bs4 import BeautifulSoup


def clean_html_text(text: str) -> str:
    if not text:
        return ""

    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text(
            separator=" ",
            strip=True,
        )

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    return text.strip()


def parse_to_list(input_data: Any) -> list[str]:
    if not input_data:
        return []

    if isinstance(input_data, list):
        return [clean for item in input_data if (clean := clean_html_text(str(item)))]

    if not isinstance(input_data, str):
        return []

    if "<li" in input_data.lower():
        soup = BeautifulSoup(input_data, "html.parser")
        li_elements = soup.find_all("li")
        if li_elements:
            return [
                clean
                for li in li_elements
                if (clean := clean_html_text(li.decode_contents()))
            ]

    raw_lines = input_data.split("\n")
    cleaned_lines = []

    for line in raw_lines:
        line_str = clean_html_text(line)
        if not line_str:
            continue

        line_str = re.sub(r"^[-*+•]\s*", "", line_str)
        line_str = re.sub(r"^\d+\.\s*", "", line_str)

        if line_str:
            cleaned_lines.append(line_str)

    if not cleaned_lines and clean_html_text(input_data).strip():
        text_clean = clean_html_text(input_data)
        sentences = re.split(r"(?<=[.!?])\s+", text_clean)
        cleaned_lines = [s for s in sentences if s.strip()]

    return cleaned_lines


def list_to_paragraph(items: list[str]) -> str:
    return "\n".join(filter(None, items)) if items else ""


def resolve_company_name(
    scraped_name: str | None, job_title: str | None, job_url: str | None, source: str
) -> str:
    if scraped_name:
        name_clean = clean_html_text(scraped_name)
        if name_clean and name_clean.lower() not in [
            "unknown",
            "unknown company",
            "none",
        ]:
            return name_clean

    if job_title:
        title_str = clean_html_text(job_title)

        match = re.search(
            r"\bat\s+([^,\-\|\(\)]+)|^(.*?)\b(?:hiring|tuyển dụng|tuyển)\b",
            title_str,
            re.IGNORECASE,
        )
        if match:
            candidate = (match.group(1) or match.group(2)).strip()
            if candidate:
                return candidate

        parts = re.split(r"[\-\|\(\)]", title_str)
        if len(parts) > 1:
            candidate = parts[-1].strip()
            if candidate and len(candidate) < 35:
                return candidate

    if job_url:
        extracted = tldextract.extract(job_url)
        if extracted.domain:
            return extracted.domain.capitalize()

    return f"Unspecified Employer ({source.capitalize()})"


def resolve_job_description(
    scraped_desc: str | None,
    responsibilities: list[str] | None,
    qualifications: list[str] | None,
) -> str:
    if scraped_desc:
        desc_clean = clean_html_text(scraped_desc)
        if desc_clean and desc_clean.lower() != "no description provided":
            return desc_clean

    fallback_parts = []

    if responsibilities and any(r.strip() for r in responsibilities):
        clean_resp = "\n- ".join(r.strip() for r in responsibilities if r.strip())
        fallback_parts.append(f"Responsibilities:\n- {clean_resp}")

    if qualifications and any(q.strip() for q in qualifications):
        clean_qual = "\n- ".join(q.strip() for q in qualifications if q.strip())
        fallback_parts.append(f"Requirements:\n- {clean_qual}")

    if fallback_parts:
        return "\n\n".join(fallback_parts)

    return (
        "Detailed job description was not provided in the source posting. "
        "Please review the original listing for application guidelines."
    )
