import re
import hashlib


class JobAdapterBase:
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
