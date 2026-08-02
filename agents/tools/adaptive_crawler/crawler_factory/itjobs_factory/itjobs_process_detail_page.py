import logging
from urllib.parse import urlparse
from datetime import datetime, UTC
from bs4 import BeautifulSoup
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

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

    company_name = "Unknown Company"
    company_size = "Unknown"
    company_address = ""
    company_slogan = ""
    company_description = ""

    company_right = soup.select_one(".jp_company-right")
    if company_right:
        h1 = company_right.find("h1")
        company_name = h1.get_text(strip=True) if h1 else "Unknown Company"

        text_nodes = [
            t
            for t in company_right.children
            if isinstance(t, str) or (t.name != "h1" and t.name != "a")
        ]
        for node in text_nodes:
            node_text = (
                node.get_text(strip=True)
                if hasattr(node, "get_text")
                else str(node).strip()
            )
            if not node_text:
                continue
            if "Quy mô công ty" in node_text or "Quy mô" in node_text:
                company_size = node_text.split(":")[-1].strip()
            else:
                company_address += node_text + " "
        company_address = company_address.strip()

    business_profile = soup.find(id="business-profile")
    if business_profile:
        slider_wrapper = business_profile.select_one(".jp_skills_slider_wrapper")
        if slider_wrapper:
            slogan_h2 = slider_wrapper.find("h2")
            if slogan_h2:
                company_slogan = slogan_h2.get_text(strip=True)

            p_tags = slider_wrapper.find_all("p")
            desc_lines = [
                p.get_text(strip=True)
                for p in p_tags
                if p.get_text(strip=True) and p.get("class") != ["profile-paragraph"]
            ]
            if desc_lines:
                company_description = "\n".join(desc_lines)

    title = "Unknown Title"
    location = "Vietnam"
    salary = "Negotiable"
    working_hours = "Full-time"
    seniority = "Middle"

    job_summary = soup.select_one(".jp_job_post_detail_cont") or soup.select_one(
        "#job-summary"
    )
    if job_summary:
        h3 = job_summary.find("h3")
        if h3:
            title = h3.get_text(strip=True)

        loc_icon = job_summary.find("i", class_="fa-map-marker")
        if loc_icon:
            loc_span = loc_icon.find_parent("li") or loc_icon.find_next("span")
            if loc_span:
                location = loc_span.get_text(strip=True)

        sal_icon = job_summary.find("i", class_="fa-usd")
        if sal_icon:
            sal_span = sal_icon.find_parent("li") or sal_icon.find_next("span")
            if sal_span:
                salary = sal_span.get_text(strip=True)

        clock_icon = job_summary.find("i", class_="fa-clock-o")
        if clock_icon:
            clock_span = clock_icon.find_parent("li") or clock_icon.find_next("span")
            if clock_span:
                working_hours = clock_span.get_text(strip=True)

        suit_icon = job_summary.find("i", class_="fa-suitcase")
        if suit_icon:
            suit_span = suit_icon.find_parent("li") or suit_icon.find_next("span")
            if suit_span:
                seniority = suit_span.get_text(strip=True)

    company_type = "Product"
    side_info = soup.select_one(".jp_job_post_side_img ul")
    if side_info:
        type_icon = side_info.find("i", class_="fa-list-alt")
        if type_icon:
            type_span = type_icon.find_next_sibling("span")
            if type_span:
                company_type = type_span.get_text(strip=True)

    description = ""
    requirements = ""

    desc_sect = soup.select_one(".job-description-section .jp_overview_wrapper")
    if desc_sect:
        description = desc_sect.get_text("\n", strip=True)
        if description.startswith("Tóm tắt công việc"):
            description = description[len("Tóm tắt công việc") :].lstrip(" \t\n\r:,-")

    req_sect = soup.select_one(".job-requirement-section .jp_overview_wrapper")
    if req_sect:
        requirements = req_sect.get_text("\n", strip=True)

    skills = []
    skills_wrapper = soup.select_one(".jp_job_post_keyword_wrapper")
    if skills_wrapper:
        anchors = skills_wrapper.find_all("a")
        for a in anchors:
            tag = a.get_text(strip=True).rstrip(",")
            if tag and tag not in skills:
                skills.append(tag)

    raw_data = {
        "title": title,
        "company": company_name,
        "company_size": company_size,
        "company_address": company_address,
        "company_slogan": company_slogan,
        "company_description": company_description,
        "company_type": company_type,
        "url": url,
        "description": description or "No description provided",
        "requirements": requirements or "No requirements specified",
        "benefits": [],
        "location": location,
        "salary": salary,
        "working_hours": working_hours,
        "seniority": seniority,
        "skills": skills,
    }

    is_updater = context.request.label == "updater_detail"
    if is_updater:
        is_not_found = False
        if context.http_response and context.http_response.status_code in [
            404,
            410,
        ]:
            is_not_found = True
        elif context._page:
            current_url = context.page.url
            if urlparse(current_url).path != urlparse(url).path:
                if "/job/" not in current_url:
                    is_not_found = True

        page_text = soup.get_text().lower()
        is_expired_text = any(
            msg in page_text
            for msg in [
                "ngưng nhận hồ sơ",
                "hết hạn",
                "job expired",
                "posting expired",
            ]
        )

        if is_not_found or is_expired_text:
            context.log.info(
                f"Job posting not found or expired: {url}. Marking as Closed."
            )
            async with session_factory() as session:
                repo = JobRepository(session)
                existing = await repo.get_by_url(url)
                if existing:
                    existing.status = "Closed"
                    existing.updated_date = datetime.now(UTC)
                    session.add(existing)
                    await session.commit()
            return

        if (
            not title
            or title.strip().lower() in ["unknown title", "no title", ""]
            or not description
            or description.strip().lower()
            in ["no description provided", "not provided", ""]
        ):
            context.log.warning(
                f"New parsed data is null/empty for URL {url} due to extraction error. Keeping old record."
            )
            return

    job = JobAdapter.to_job(raw_data, "itjobs")
    async with session_factory() as session:
        repo = JobRepository(session)
        await repo.save(job)
        await session.commit()
    context.log.info(f"Successfully saved ITJobs Job: {title} at {company_name}")
