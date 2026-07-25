import json
import logging
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from crawlee import Request
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

from app.core.enums import JobStatus
from ...crawler_adapter import adapter_itviec
from ...crawler_repository import JobRepository

logger = logging.getLogger(__name__)


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


async def process_detail_page(
    context: AdaptivePlaywrightCrawlingContext,
    soup: BeautifulSoup,
    url: str,
    session_factory,
) -> None:
    context.log.info(f"Processing ITViec detail page: {url}")

    has_search_button = bool(
        soup.select_one("button.ibtn-search, button.ibtn-primary.ibtn-search")
    )
    is_not_found = (
        context.http_response and context.http_response.status_code in [404, 410]
    ) or has_search_button

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

    schema_data = {}
    json_ld_tags = soup.find_all("script", type="application/ld+json")
    for tag in json_ld_tags:
        try:
            data = json.loads(tag.string or "{}")
            if isinstance(data, dict) and (
                data.get("@type") == "JobPosting"
                or "JobPosting" in str(data.get("@type"))
            ):
                schema_data = data
                break
        except Exception as e:
            context.log.warning(f"Error parsing JSON-LD: {e}")

    main_container = soup.select_one("div.row.im-0.ip-0")
    if not main_container:
        raise ValueError(
            "Main container <div class='row im-0 ip-0'> not found on detail page"
        )

    title_elem = main_container.find("h1")
    title = (
        title_elem.get_text(strip=True)
        if title_elem
        else schema_data.get("title", "Unknown Title")
    )

    company_name = schema_data.get("hiringOrganization", {}).get("name", "")
    company_href = None
    company_elem = main_container.select_one(
        "a.text-it-black.text-hover-red.cursor-pointer"
    )
    if company_elem:
        company_href = company_elem.get("href")
        text = company_elem.get_text(strip=True)
        if text:
            company_name = text

    if company_href:
        comp_url = urljoin("https://itviec.com", company_href)
        if "?" in comp_url:
            comp_url = comp_url.split("?")[0]
        await context.add_requests([Request.from_url(url=comp_url, label="company")])

    company_type = None
    company_industry = None
    company_size = None
    company_country = None
    working_days = None
    overtime_policy = None

    for row in main_container.select("div.row.ipy-2, div.row.border-bottom-dashed"):
        label_elem = row.select_one("div.text-dark-grey")
        if not label_elem:
            continue
        label = label_elem.get_text(strip=True).lower()
        cols = row.select("div.col")
        val_elem = row.select_one("div.col.text-end") or (
            cols[-1] if len(cols) > 1 else None
        )
        if not val_elem:
            continue

        if "country" in label:
            span_country = val_elem.select_one("span.align-middle")
            company_country = (
                span_country.get_text(strip=True)
                if span_country
                else val_elem.get_text(strip=True)
            )
        elif "company type" in label:
            company_type = val_elem.get_text(strip=True)
        elif "company industry" in label:
            company_industry = val_elem.get_text(separator=" ", strip=True)
        elif "company size" in label:
            company_size = " ".join(
                val_elem.get_text(separator=" ", strip=True).split()
            )
        elif "working days" in label:
            working_days = val_elem.get_text(strip=True)
        elif "overtime policy" in label:
            overtime_policy = val_elem.get_text(strip=True)

    location = "Vietnam"
    addresses = []
    loc_data = schema_data.get("jobLocation")
    invalid_loc_values = {"not available", "n/a", "none", "null", "unknown"}

    if loc_data:
        loc_list = loc_data if isinstance(loc_data, list) else [loc_data]
        for loc in loc_list:
            if not isinstance(loc, dict):
                continue
            addr = loc.get("address", {})
            if isinstance(addr, dict):
                street = (addr.get("streetAddress") or "").strip()
                locality = (addr.get("addressLocality") or "").strip()
                region = (addr.get("addressRegion") or "").strip()

                valid_parts = [
                    p
                    for p in [street, locality, region]
                    if p and p.lower() not in invalid_loc_values
                ]
                if valid_parts:
                    full_address = ", ".join(valid_parts)
                    addresses.append(full_address)

                if (
                    locality
                    and locality.lower() not in invalid_loc_values
                    and location == "Vietnam"
                ):
                    location = locality

    work_model = "At office"
    wm_elem = main_container.find(
        string=lambda s: s and any(k in s for k in ["At office", "Remote", "Hybrid"])
    )
    if wm_elem:
        work_model = wm_elem.strip()

    skills = []
    skills_section = main_container.find("div", string=lambda s: s and "Skills:" in s)
    if skills_section:
        skills_container = skills_section.find_parent("div")
        if skills_container:
            skills = [
                s.get_text(strip=True)
                for s in skills_container.select("a.itag")
                if s.get_text(strip=True)
            ]

    domains = []
    domain_section = main_container.find(
        "div", string=lambda s: s and "Job Domain:" in s
    )
    if domain_section:
        domain_container = domain_section.find_parent("div")
        if domain_container:
            domains = [
                d.get_text(strip=True)
                for d in domain_container.select(".itag")
                if d.get_text(strip=True)
            ]

    description = ""
    responsibilities = []
    requirements = []
    nice_to_have = []

    paragraph_divs = main_container.select("div.imy-5.paragraph")
    for p_div in paragraph_divs:
        header = p_div.find(["h2", "h3"])
        header_text = header.get_text(strip=True).lower() if header else ""
        header_raw = header.get_text(strip=True) if header else ""
        content_text = p_div.get_text(separator="\n", strip=True)

        if header_raw and content_text.startswith(header_raw):
            content_text = content_text[len(header_raw) :].strip()

        if "description" in header_text or "job description" in header_text:
            description = content_text
        elif "responsibilities" in header_text or "your role" in header_text:
            responsibilities.extend(
                [li.get_text(strip=True) for li in p_div.select("li")]
                or ([content_text] if content_text else [])
            )
        elif (
            "skills" in header_text
            or "experience" in header_text
            or "required" in header_text
            or "requirements" in header_text
        ):
            reqs, nice = parse_skills_paragraph(p_div)
            requirements.extend(reqs)
            nice_to_have.extend(nice)
        elif "preferred" in header_text or "nice to have" in header_text:
            nice_to_have.extend(
                [li.get_text(strip=True) for li in p_div.select("li")]
                or ([content_text] if content_text else [])
            )

    raw_data = {
        "title": title,
        "url": url,
        "schema_data": schema_data,
        "company": {
            "name": company_name,
            "type": company_type,
            "industry": company_industry,
            "size": company_size,
            "country": company_country,
            "working_days": working_days,
            "overtime_policy": overtime_policy,
            "addresses": addresses,
        },
        "job_overview": {
            "location": location,
            "work_model": work_model,
            "skills": skills,
            "domains": domains,
        },
        "job_details": {
            "description": description or "No description provided",
            "responsibilities": responsibilities,
            "requirements": requirements,
            "nice_to_have": nice_to_have,
        },
    }

    job = adapter_itviec(raw_data)
    async with session_factory() as session:
        repo = JobRepository(session)
        await repo.save_or_update(job)
        await session.commit()

    context.log.info(f"Successfully adapted and saved ITViec Job: '{job.title}'")
