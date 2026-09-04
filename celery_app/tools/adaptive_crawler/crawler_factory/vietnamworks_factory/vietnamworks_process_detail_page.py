import logging
import re
from datetime import date, datetime, timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from crawlee import Request
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

from ...crawler_adapter import JobAdapter
from ...crawler_repository import JobRepository

logger = logging.getLogger(__name__)


def _clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def _extract_text(container, tag_names=None) -> str:
    if not container:
        return ""
    text_parts = []
    for node in container.find_all(
        tag_names or ["p", "span", "div", "h1", "h2", "h3", "li"]
    ):
        text = _clean_text(node.get_text(" ", strip=True))
        if text:
            text_parts.append(text)
    return _clean_text(" ".join(text_parts))


def _extract_section(heading: Tag) -> str:
    parts = []

    for sibling in heading.find_next_siblings():
        if sibling.name in ("h2", "h3", "h4"):
            break
        parts.append(_extract_text(sibling))

    return "\n".join(filter(None, parts)).strip()


async def process_detail_page(
    context: AdaptivePlaywrightCrawlingContext,
    soup: BeautifulSoup,
    url: str,
    session_factory,
) -> None:
    context.log.info(f"Processing VietnamWorks detail page: {url}")

    expired_date: date | None = None
    title = ""
    title_elem = soup.find(["h1", "h2"])
    if title_elem:
        title = _clean_text(title_elem.get_text(" ", strip=True))

    if not title:
        title = "Unknown Title"

    company_name = ""
    company_link = None
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if (
            href
            and isinstance(href, str)
            and ("/nha-tuyen-dung/" in href or "/company/" in href)
        ):
            company_link = href
            company_name = _clean_text(a.get_text(" ", strip=True))
            break

    location = "Vietnam"

    address_tag = soup.find(
        "a",
        href=re.compile(r"google\.com/maps\?q=", re.IGNORECASE),
    )

    if address_tag:
        address_p = address_tag.find_previous("p")
        if address_p:
            location = _clean_text(address_p.get_text(" ", strip=True))

    if location == "Vietnam":
        location_candidates = [
            soup.find(
                string=re.compile(
                    r"Hưng Yên|Hà Nội|TP\. Hồ Chí Minh|Đà Nẵng|Việt Nam", re.IGNORECASE
                )
            ),
            soup.find(string=re.compile(r"Địa điểm|Địa chỉ|Location", re.IGNORECASE)),
        ]

        for candidate in location_candidates:
            if candidate:
                parent = getattr(candidate, "parent", None)
                if parent is not None and hasattr(parent, "get_text"):
                    location_text = _clean_text(parent.get_text(" ", strip=True))
                if location_text:
                    location = location_text
                    break

    metadata_sections = []
    for label in soup.find_all(["label", "span", "p"]):
        label_text = _clean_text(label.get_text(" ", strip=True))
        if not label_text:
            continue
        if label_text.upper() in {
            "NGÀY ĐĂNG",
            "CẤP BẬC",
            "NGÀNH NGHỀ",
            "KỸ NĂNG",
            "LĨNH VỰC",
            "SỐ NĂM KINH NGHIỆM TỐI THIỂU",
            "QUỐC TỊCH",
            "NGÔN NGỮ TRÌNH BÀY HỒ SƠ",
        }:
            value = ""
            parent = label.parent
            if parent:
                value = _clean_text(parent.get_text(" ", strip=True))
            if value:
                metadata_sections.append(value)

    description = ""
    requirement_blocks = []

    for heading in soup.find_all(["h2", "h3", "h4"]):
        heading_text = _clean_text(heading.get_text(" ", strip=True)).lower()

        if "mô tả" in heading_text or "description" in heading_text:
            description = _extract_section(heading)
        elif "yêu cầu" in heading_text or "requirement" in heading_text:
            requirement_blocks.append(_extract_section(heading))

    if not description:
        description = _extract_text(soup.find(id="vnwLayout__col"))

    responsibilities: list[str] = []
    requirements: list[str] = []
    nice_to_have: list[str] = []
    if requirement_blocks:
        requirements = [block for block in requirement_blocks if block]

    if not requirements and description:
        requirements = [description]

    if company_link and isinstance(company_link, str):
        company_url = urljoin("https://www.vietnamworks.com", company_link)
        if "?" in company_url:
            company_url = company_url.split("?")[0]
        await context.add_requests([Request.from_url(url=company_url, label="company")])

    expired_span = soup.find(
        "span",
        string=re.compile(r"Hết hạn trong\s+\d+\s+(ngày|tháng)", re.IGNORECASE),
    )
    if expired_span:
        text = expired_span.get_text(strip=True)
        match = re.search(
            r"Hết hạn trong\s+(\d+)\s+(ngày|tháng)",
            text,
            re.IGNORECASE,
        )
        if match:
            days_val = int(match.group(1))
            unit = match.group(2).lower()
            if unit == "ngày":
                expired_date_dt = datetime.now() + timedelta(days=days_val)
            else:
                expired_date_dt = datetime.now() + timedelta(days=days_val * 30)

            expired_date = expired_date_dt.date()

    skills: list[str] = []
    domains: list[str] = []
    working_time = "Full-time"
    columns = soup.find_all("div", id="vnwLayout__col")
    for col in columns:
        label_tag = col.find("label", attrs={"name": "label"})
        p_tag = col.find("p", attrs={"name": "paragraph"})

        if label_tag and p_tag:
            label_text = label_tag.get_text(strip=True).upper()
            value_text = p_tag.get_text(strip=True)

            if label_text == "LOẠI HÌNH LÀM VIỆC":
                if value_text.strip().lower() == "toàn thời gian":
                    working_time = "Full-time"
                else:
                    working_time = "Part-time"
            elif label_text == "KỸ NĂNG":
                skills.extend([s.strip() for s in value_text.split(",") if s.strip()])
            elif label_text == "NGÀNH NGHỀ":
                domains.extend(s for s in re.split(r"\s*[,>]\s*", value_text) if s)

    raw_data = {
        "title": title,
        "url": url,
        "expired_date": expired_date.isoformat() if expired_date else None,
        "valid_through": expired_date.isoformat() if expired_date else None,
        "company": {
            "name": company_name or "Unknown Company",
            "location": location,
            "description": "",
            "industry": "IT Services",
            "size": "50-150 employees",
            "company_type": "Product",
            "country": "Vietnam",
            "addresses": [location],
            "benefits": [],
        },
        "location": location,
        "description": description or "No description provided",
        "min_salary": None,
        "max_salary": None,
        "currency": "VND",
        "responsibilities": responsibilities,
        "required_qualifications": requirements,
        "nice_to_have": nice_to_have,
        "skills": skills,
        "domains": domains,
        "working_hours": working_time,
        "working_model": "ONSITE",
    }

    job = JobAdapter.to_job(raw_data, "VietnamWorks")
    async with session_factory() as session:
        repo = JobRepository(session)
        await repo.save_or_update(job)
        await session.commit()

    context.log.info(f"Successfully adapted and saved VietnamWorks Job: '{job.title}'")
