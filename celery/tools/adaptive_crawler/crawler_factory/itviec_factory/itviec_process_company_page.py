import logging
from bs4 import BeautifulSoup
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

from ...crawler_repository import CompanyRepository
from ...crawler_adapter.itviec_adapter import adapter_itviec_company
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
            labels = container.select(".text-dark-grey")

            for label_el in labels:
                label_text = label_el.get_text(strip=True)

                value_container = label_el.find_next_sibling("div")
                if not value_container:
                    continue

                value_text = value_container.get_text(strip=True)

                if "Company type" in label_text:
                    company_type = value_text
                elif "Company industry" in label_text:
                    industry = value_text
                elif "Company size" in label_text:
                    size = value_text
                elif "Country" in label_text:
                    country = value_text
                elif "Working days" in label_text:
                    working_days = value_text
                elif "Overtime policy" in label_text:
                    overtime_policy = value_text

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
    web_div = soup.find(lambda tag: tag.has_attr("data-redirect-url-url-value"))
    if web_div:
        val = web_div.get("data-redirect-url-url-value", "")
        if isinstance(val, str):
            website = clean_html_text(val)

    benefits_list = []
    benefits_hdr = soup.find(
        "h2", string=lambda s: s and "love working here" in s.lower()
    )
    if benefits_hdr:
        container = benefits_hdr.find_parent("div")
        if container:
            for li in container.find_all("li"):
                btxt = clean_html_text(li.get_text(strip=True))
                if btxt:
                    benefits_list.append(btxt)

    location = "Vietnam"
    loc_div = soup.select_one("div.location span.text-break")
    if loc_div:
        location = clean_html_text(loc_div.get_text(strip=True))

    addresses = []
    loc_spans = soup.select("div.location span.text-break")
    if loc_spans:
        for span in loc_spans:
            addr_text = clean_html_text(span.get_text(strip=True))
            if addr_text:
                addresses.append(addr_text)

    if not addresses:
        addresses = [location] if location else []

    raw_data = {
        "name": name,
        "industry": industry,
        "size": size,
        "location": location,
        "description": description,
        "website": website,
        "slogan": slogan,
        "company_type": company_type,
        "country": country,
        "addresses": addresses,
        "working_days": working_days,
        "overtime_policy": overtime_policy,
        "benefits": benefits_list,
    }

    company_obj = adapter_itviec_company(raw_data)
    async with session_factory() as session:
        repo = CompanyRepository(session)
        await repo.save_or_update(company_obj)
        await session.commit()
    context.log.info(f"Successfully updated and saved ITViec Company: '{name}'")
