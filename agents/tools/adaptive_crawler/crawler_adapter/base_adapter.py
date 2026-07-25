import json
import re
import hashlib
from pathlib import Path

_SKILL_CATEGORIES_CACHE: dict[str, list[str]] | None = None


def _get_skill_taxonomy() -> dict[str, list[str]]:
    global _SKILL_CATEGORIES_CACHE
    if _SKILL_CATEGORIES_CACHE is None:
        json_path = Path(__file__).parent.parent / "resources" / "skill_categories.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    _SKILL_CATEGORIES_CACHE = json.load(f)
            except Exception:
                _SKILL_CATEGORIES_CACHE = {}
        else:
            _SKILL_CATEGORIES_CACHE = {}
    return _SKILL_CATEGORIES_CACHE


class JobAdapterBase:
    @classmethod
    def classify_skill_category(cls, skill_name: str) -> str:
        if not skill_name:
            return "Technical"
        clean = skill_name.strip().lower()
        taxonomy = _get_skill_taxonomy()

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
        norm_title = (title or "").lower().strip()
        norm_company = (company_name or "").lower().strip()
        norm_description = (description or "").lower().strip()
        norm_description = re.sub(r"<[^>]+>", "", norm_description)
        norm_location = (location or "").lower().strip()
        raw_fingerprint = (
            f"{norm_title}|{norm_company}|{norm_description}|{norm_location}"
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
