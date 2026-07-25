import logging
from bs4 import BeautifulSoup
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

from app.modules.company.models import Company, CompanyBenefit
from ...crawler_repository import CompanyRepository
from ...crawler_adapter.itviec_adapter import _map_company_type
from app.utils.text_parser import clean_html_text

logger = logging.getLogger(__name__)


async def process_company_page(
    context: AdaptivePlaywrightCrawlingContext,
    soup: BeautifulSoup,
    url: str,
    session_factory,
) -> None:
    context.log.info(f"Processing ITViec company page: {url}")
    name_elem = soup.find("h1")
    name = clean_html_text(name_elem.get_text(strip=True)) if name_elem else ""
    if not name:
        context.log.warning(f"No company name found at URL: {url}")
        return

    industry = "IT Services"
    size = "50-150 employees"
    company_type = "Product"
    country = "Vietnam"
    working_days = None
    overtime_policy = None

    gen_info_hdr = soup.find(string=lambda s: s and "General information" in s)
    if gen_info_hdr:
        container = gen_info_hdr.find_parent("div")
        if container:
            for row in container.select(".row"):
                txt = row.get_text()
                if "Company type" in txt:
                    company_type = (
                        row.select_one(".normal-text, div:last-child").get_text(
                            strip=True
                        )
                        if row.select_one(".normal-text, div:last-child")
                        else company_type
                    )
                elif "Company industry" in txt:
                    industry = (
                        row.select_one("div:last-child").get_text(strip=True)
                        if row.select_one("div:last-child")
                        else industry
                    )
                elif "Company size" in txt:
                    size = (
                        row.select_one(".normal-text, div:last-child").get_text(
                            strip=True
                        )
                        if row.select_one(".normal-text, div:last-child")
                        else size
                    )
                elif "Country" in txt:
                    span = row.select_one("span")
                    if span:
                        country = span.get_text(strip=True)
                elif "Working days" in txt:
                    wd_el = row.select_one(".normal-text")
                    if wd_el:
                        working_days = wd_el.get_text(strip=True)
                elif "Overtime policy" in txt:
                    overtime_el = row.select_one(".normal-text")
                    if overtime_el:
                        overtime_policy = overtime_el.get_text(strip=True)

    company_type = clean_html_text(company_type)
    industry = clean_html_text(industry)
    size = clean_html_text(size)
    country = clean_html_text(country)
    working_days = clean_html_text(working_days) if working_days else None
    overtime_policy = clean_html_text(overtime_policy) if overtime_policy else None

    slogan = None
    description = ""
    overview_hdr = soup.find("h2", string=lambda s: s and "Company overview" in s)
    if overview_hdr:
        overview_div = overview_hdr.find_next_sibling("div", class_="paragraph")
        if overview_div:
            lines = [
                line.strip()
                for line in overview_div.get_text(separator="\n", strip=True).split(
                    "\n"
                )
                if line.strip()
            ]
            if lines:
                slogan = clean_html_text(lines[0])
                description = clean_html_text("\n".join(lines[1:]))

    website = ""
    web_div = soup.find(attrs={"data-redirect-url-url-value": True})
    if web_div:
        website = clean_html_text(web_div.get("data-redirect-url-url-value", ""))

    benefits_list = []
    benefits_hdr = soup.find(
        "h2", string=lambda s: s and "love working here" in s.lower()
    )
    if benefits_hdr:
        benefits_ul = benefits_hdr.find_next("ul")
        if benefits_ul:
            for li in benefits_ul.find_all("li"):
                btxt = clean_html_text(li.get_text(strip=True))
                if btxt:
                    benefits_list.append(CompanyBenefit(name=btxt))

    location = "Vietnam"
    loc_div = soup.select_one("div.location span.text-break")
    if loc_div:
        location = clean_html_text(loc_div.get_text(strip=True))

    vector_context = (
        f"Company Name: {name}. Slogan: {slogan or 'N/A'}. Type: {company_type}. "
        f"Industry: {industry}. Size: {size}. Country: {country}. Location: {location}. "
        f"Working Days: {working_days or 'N/A'}. Overtime Policy: {overtime_policy or 'N/A'}. "
        f"Description: {description}."
    )

    company_type = _map_company_type(company_type)

    company_obj = Company(
        name=name,
        industry=industry,
        size=size,
        location=location,
        description=description,
        website=website,
        slogan=slogan,
        company_type=company_type,
        country=country,
        addresses=[location],
        working_days=working_days,
        overtime_policy=overtime_policy,
        vector_context=vector_context,
        benefits=benefits_list,
    )

    async with session_factory() as session:
        repo = CompanyRepository(session)
        await repo.save_or_update(company_obj)
        await session.commit()
    context.log.info(f"Successfully updated and saved ITViec Company: '{name}'")
