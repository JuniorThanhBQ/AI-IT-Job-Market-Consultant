import hashlib
import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.utils.utils import clean_field

SKILL_CATEGORIES_CACHE: dict[str, list[str]] | None = None


def get_skill_taxonomy() -> dict[str, list[str]]:
    global SKILL_CATEGORIES_CACHE
    if SKILL_CATEGORIES_CACHE is None:
        json_path = Path(__file__).parent.parent / "resources" / "skill_categories.json"
        if json_path.exists():
            try:
                with open(json_path, encoding="utf-8") as f:
                    SKILL_CATEGORIES_CACHE = json.load(f)
            except Exception:
                SKILL_CATEGORIES_CACHE = {}
        else:
            SKILL_CATEGORIES_CACHE = {}
    return SKILL_CATEGORIES_CACHE


class JobAdapterBase:
    @classmethod
    def classify_skill_category(cls, skill_name: str) -> str:
        if not skill_name:
            return "Technical"
        clean = skill_name.strip().lower()
        taxonomy = get_skill_taxonomy()

        for category, terms in taxonomy.items():
            for term in terms:
                term_clean = term.strip().lower()
                if (
                    clean == term_clean
                    or clean.startswith(f"{term_clean} ")
                    or clean.endswith(f" {term_clean}")
                    or f" {term_clean} " in clean
                ):
                    return category

        return "Technical"

    @staticmethod
    def calculate_content_hash(
        title: str, company_name: str, description: str, location: str
    ) -> str:
        norm_title = clean_field(title)
        norm_company = clean_field(company_name)
        norm_description = re.sub(r"</?[a-zA-Z][^>]*>", " ", description or "")
        norm_description = clean_field(norm_description)
        norm_location = clean_field(location)
        raw_fingerprint = "\x1f".join(
            f"{len(f)}:{f}"
            for f in (norm_title, norm_company, norm_description, norm_location)
        )
        return hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()

    @staticmethod
    def parse_salary(salary_str: str) -> tuple[float, float, str]:
        if not salary_str:
            return 0.0, 0.0, "VND"

        lowered = salary_str.lower()
        has_vnd_signal = "vnd" in lowered or "đ" in salary_str or "đô" in lowered
        has_usd_signal = "$" in salary_str
        currency = "VND" if has_vnd_signal else ("USD" if has_usd_signal else "VND")

        numbers = [
            float(x)
            for x in re.findall(r"\d+", salary_str.replace(".", "").replace(",", ""))
        ]

        if not numbers:
            return 0.0, 0.0, currency

        if len(numbers) >= 2:
            return numbers[0], numbers[1], currency
        return numbers[0], numbers[0], currency

    @staticmethod
    def process_skills(raw_skills: list[str]) -> list[Any]:
        from app.modules.job.models import Skills
        from utils.text_parser import clean_html_text

        seen = set()
        skills = []
        for s in raw_skills:
            cleaned = clean_html_text(s)
            if cleaned:
                cleaned_lower = cleaned.lower()
                if cleaned_lower not in seen:
                    seen.add(cleaned_lower)
                    skills.append(
                        Skills(
                            name=cleaned,
                            category=JobAdapterBase.classify_skill_category(cleaned),
                        )
                    )
        return skills

    @staticmethod
    def build_job(
        *,
        title: str,
        job_desc: str,
        expired_date: datetime | None,
        seniority: Any,
        min_salary: float | Decimal,
        max_salary: float | Decimal,
        currency: Any,
        working_hours: str,
        working_model: Any,
        content_hash: str,
        responsibilities: list[str],
        required_qualifications: list[str],
        nice_to_have: list[str],
        domains: list[str],
        vector_context: str,
        source: Any,
        url: str,
        company: Any,
        skills: list[Any],
    ) -> Any:
        from app.core.enums import JobStatus
        from app.modules.job.models import Job

        now = datetime.now()
        return Job(
            title=title,
            job_description=job_desc,
            created_date=now,
            expired_date=expired_date,
            updated_date=now,
            seniority=seniority,
            min_salary=Decimal(str(min_salary)),
            max_salary=Decimal(str(max_salary)),
            currency=currency,
            working_hours=working_hours,
            working_model=working_model,
            status=JobStatus.OPEN,
            content_hash=content_hash,
            responsibilities=responsibilities,
            required_qualifications=required_qualifications,
            nice_to_have=nice_to_have,
            domains=domains,
            vector_context=vector_context,
            source=source,
            url=url,
            company=company,
            skills=skills,
        )

    @staticmethod
    def build_company_vector_context(
        name: str,
        slogan: str | None,
        company_type: str | None,
        industry: str | None,
        size: str | None,
        country: str | None,
        location: str | None,
        description: str | None,
        working_days: str | None = None,
        overtime_policy: str | None = None,
    ) -> str:
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
        if country:
            parts.append(f"Country: {country}.")
        if location:
            parts.append(f"Location: {location}.")
        if working_days:
            parts.append(f"Working Days: {working_days}.")
        if overtime_policy:
            parts.append(f"Overtime Policy: {overtime_policy}.")
        if description:
            parts.append(f"Description: {description}.")
        return " ".join(parts)
