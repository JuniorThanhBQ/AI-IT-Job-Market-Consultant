import json
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from crawlee import Request
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

from app.core.enums import JobStatus
from app.utils.topdev_utils import extract_company_meta
from ...crawler_repository import JobRepository
from ...crawler_adapter import JobAdapter

logger = logging.getLogger(__name__)


async def process_detail_page(
    context: AdaptivePlaywrightCrawlingContext,
    soup: BeautifulSoup,
    url: str,
    session_factory,
) -> None:
    context.log.info(f"Extracting detail page: {url}")

    is_not_found = context.http_response and context.http_response.status_code in [
        404,
        410,
    ]
    if is_not_found:
        context.log.info(f"Job posting closed or not found for URL: {url}")
        async with session_factory() as session:
            repo = JobRepository(session)
            existing = await repo.get_by_url(url)
            if existing:
                existing.status = JobStatus.CLOSED
                existing.updated_date = datetime.now(timezone.utc)
                session.add(existing)
                await session.commit()
        return

    title = None
    company_name = None
    skills = []
    description = ""
    requirements = ""
    benefits = []
    valid_through = None
    location = "Vietnam"
    salary = "Negotiable"

    json_ld_tags = soup.find_all("script", type="application/ld+json")
    for tag in json_ld_tags:
        try:
            data = json.loads(tag.string)
            if data.get("@type") == "JobPosting" or "JobPosting" in str(
                data.get("@type")
            ):
                title = data.get("title")
                company_name = data.get("hiringOrganization", {}).get("name")
                if data.get("skills"):
                    if isinstance(data["skills"], str):
                        skills = [
                            s.strip() for s in data["skills"].split(",") if s.strip()
                        ]
                    elif isinstance(data["skills"], list):
                        skills = data["skills"]

                loc_data = data.get("jobLocation")
                if loc_data:
                    if isinstance(loc_data, list) and len(loc_data) > 0:
                        loc_data = loc_data[0]
                    address = loc_data.get("address", {})
                    location = address.get(
                        "addressRegion",
                        address.get("addressLocality", "Vietnam"),
                    )

                salary_val = data.get("baseSalary", {}).get("value", {})
                if isinstance(salary_val, dict):
                    salary = salary_val.get("value", "Negotiable")
                elif isinstance(salary_val, str):
                    salary = salary_val

                valid_through = data.get("validThrough")
                raw_desc = data.get("description", "")
                description = (
                    BeautifulSoup(raw_desc, "html.parser").get_text(
                        separator="\n", strip=True
                    )
                    if raw_desc
                    else ""
                )
                job_benefits = data.get("jobBenefits", "")
                if job_benefits:
                    if isinstance(job_benefits, list):
                        benefits = job_benefits
                    else:
                        sub_soup = BeautifulSoup(job_benefits, "html.parser")
                        benefits = [
                            li.get_text(strip=True)
                            for li in sub_soup.find_all("li")
                            if li.get_text(strip=True)
                        ]
                break
        except Exception as e:
            logger.error(f"Error parsing JSON-LD in TopDev: {e}")

    if not title:
        title_elem = soup.find("h1")
        title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"

    company_container = soup.find(
        "div",
        class_=lambda c: c and "font-sans" in c and "relative" in c and "h-fit" in c,
    )
    company_search_context = company_container if company_container else soup

    employer_links = company_search_context.find_all(
        "a", href=lambda h: h and "/companies/" in h
    )
    employer_info = None

    if employer_links:
        employer_info = employer_links[0]
        if not company_name:
            name_span = employer_info.find(
                "span",
                class_=lambda c: c and "font-semibold" in c,
            )
            if name_span:
                company_name = name_span.get_text(strip=True)
            else:
                company_name = employer_info.get_text(strip=True)

    if employer_info:
        company_href = employer_info.get("href")
        if company_href:
            company_url = urljoin(url, company_href)
            await context.add_requests(
                [Request.from_url(url=company_url, label="company")]
            )
    else:
        if not company_name:
            company_name = "Unknown Company"

    if not description:
        desc_div = soup.select_one(".job-description") or soup.select_one(
            ".description"
        )
        description = (
            desc_div.get_text(strip=True) if desc_div else "No description provided"
        )

    nice_to_have = []
    extracted_requirements = []

    qual_header = soup.find(
        lambda tag: (
            tag.name in ["span"]
            and tag.get_text()
            and any(
                keyword in tag.get_text().lower()
                for keyword in [
                    "skills & qualifications",
                    "Your skills & qualifications",
                    "qualifications",
                ]
            )
        )
    )
    if qual_header:
        qual_container = qual_header.find_next_sibling("div")
        if not qual_container:
            for d in qual_header.find_all_next("div"):
                if qual_header not in d.parents:
                    qual_container = d
                    break
        if qual_container:
            current_list_type = "req"
            elements = qual_container.find_all(
                ["p", "span", "strong", "div", "h1", "h2", "h3", "h4", "li"]
            )
            for child in elements:
                if child.find_parent("li"):
                    continue

                if child.name == "li":
                    txt = child.get_text(strip=True)
                    if txt:
                        if current_list_type == "req":
                            if txt not in extracted_requirements:
                                extracted_requirements.append(txt)
                        else:
                            if txt not in nice_to_have:
                                nice_to_have.append(txt)
                else:
                    text_clean = child.get_text(strip=True).lower()
                    nice_keywords = [
                        "nice to have",
                        "plus",
                        "preferred",
                        "key competencies",
                        "điểm cộng",
                        "ưu tiên",
                        "lợi thế",
                        "khuyến khích",
                    ]
                    if len(text_clean) < 50 and any(
                        kw in text_clean for kw in nice_keywords
                    ):
                        current_list_type = "nice"

    if extracted_requirements:
        requirements = "\n".join(extracted_requirements) + "\n"

    if not requirements:
        skills_header = soup.find(
            lambda tag: (
                tag.name in ["span", "h1", "h2", "h3", "h4", "div"]
                and tag.get_text()
                and "skills & qualifications" in tag.get_text().lower()
            )
        )
        container = None
        if skills_header:
            container = skills_header.find_next("div", class_="prose-ul")
        if not container:
            container = soup.find("div", class_="prose-ul")

        if container:
            current_list = "req"
            for element in container.children:
                if element.name in ["p", "div", "h1", "h2", "h3", "h4"]:
                    text_clean = element.get_text(strip=True).lower()
                    nice_keywords = [
                        "nice to have",
                        "plus",
                        "preferred",
                        "key competencies",
                        "điểm cộng",
                        "ưu tiên",
                        "lợi thế",
                        "khuyến khích",
                    ]
                    if len(text_clean) < 50 and any(
                        kw in text_clean for kw in nice_keywords
                    ):
                        current_list = "nice"
                elif element.name in ["ul", "ol"]:
                    for li in element.find_all("li"):
                        txt = li.get_text(strip=True)
                        if txt:
                            if current_list == "req":
                                requirements += txt + "\n"
                            else:
                                if txt not in nice_to_have:
                                    nice_to_have.append(txt)

    if not nice_to_have:
        nice_header = soup.find(
            lambda tag: (
                tag.name in ["p", "span", "strong", "h1", "h2", "h3", "h4", "div"]
                and tag.get_text()
                and "nice to have" in tag.get_text().lower()
            )
        )
        if nice_header:
            next_list = nice_header.find_next(["ul", "ol"])
            if next_list:
                for li in next_list.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt:
                        if txt not in nice_to_have:
                            nice_to_have.append(txt)

    company_industry = extract_company_meta(company_search_context, "industry")
    company_size = extract_company_meta(company_search_context, "size")
    if company_size:
        match = re.search(r"(\d+-\d+|\d+\+?|\d+)", company_size)
        if match:
            company_size = f"{match.group(1)} employees"

    responsibilities = []
    resp_header = soup.find(
        lambda tag: (
            tag.name in ["span"]
            and tag.get_text()
            and any(
                keyword in tag.get_text().lower()
                for keyword in [
                    "Your role & responsibilities",
                    "role & responsibilities",
                    "responsibilities",
                ]
            )
        )
    )
    if resp_header:
        resp_container = resp_header.find_next_sibling("div")
        if not resp_container:
            for d in resp_header.find_all_next("div"):
                if resp_header not in d.parents:
                    resp_container = d
                    break
        if resp_container:
            for li in resp_container.find_all("li"):
                txt = li.get_text(strip=True)
                if txt and txt not in responsibilities:
                    responsibilities.append(txt)
        if not responsibilities:
            next_list = resp_header.find_next(["ul", "ol"])
            if next_list:
                for li in next_list.find_all("li"):
                    txt = li.get_text(strip=True)
                    if txt and txt not in responsibilities:
                        responsibilities.append(txt)

    for item in nice_to_have + responsibilities:
        requirements = requirements.replace(item + "\n", "").replace(item, "")

    raw_data = {
        "title": title,
        "company": company_name,
        "company_industry": company_industry,
        "company_size": company_size,
        "url": url,
        "description": description,
        "requirements": requirements or "No requirements specified",
        "nice_to_have": [],
        "responsibilities": responsibilities,
        "benefits": benefits,
        "location": location,
        "salary": salary,
        "skills": skills,
        "job_overview": {
            "valid_through": valid_through,
        },
    }

    job = JobAdapter.to_job(raw_data, "topdev")
    async with session_factory() as session:
        repo = JobRepository(session)
        await repo.save_or_update(job)
        await session.commit()
    context.log.info(f"Successfully saved TopDev Job: {title} at {company_name}")
