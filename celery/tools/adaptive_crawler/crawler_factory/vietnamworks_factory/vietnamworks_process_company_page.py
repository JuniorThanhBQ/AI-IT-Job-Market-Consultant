import logging
from bs4 import BeautifulSoup
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

from ...crawler_repository import CompanyRepository
from ...crawler_adapter.vietnamworks_adapter import adapter_vietnamworks_company
from utils.text_parser import clean_html_text

logger = logging.getLogger(__name__)


async def process_company_page(
    context: AdaptivePlaywrightCrawlingContext,
    soup: BeautifulSoup,
    url: str,
    session_factory,
) -> None:
    context.log.info(f"Processing VietnamWorks company page: {url}")

    name = ""
    name_elem = soup.select_one("h1")
    if name_elem:
        name = clean_html_text(name_elem.get_text(" ", strip=True))

    if not name:
        context.log.warning(f"No company name found at URL: {url}")
        return

    industry = ""
    size = None
    company_type = None
    country = "Vietnam"
    working_days = None
    overtime_policy = None
    location = "Vietnam"
    addresses = []

    info_items = soup.select("#AboutUs ul li")
    for li in info_items:
        type_elem = li.select_one(".type")
        if type_elem:
            type_text = type_elem.get_text(strip=True)
            if type_text == "Lĩnh vực":
                val_elem = li.select_one(".text")
                if val_elem:
                    industry = clean_html_text(val_elem.get_text(strip=True))
            elif type_text == "Địa chỉ":
                val_elem = li.select_one(".dangerously-text")
                if val_elem:
                    addresses.append(clean_html_text(val_elem.get_text(strip=True)))
                    location = addresses[0]
            elif type_text == "Quy mô":
                val_elem = li.select_one(".text")
                if val_elem:
                    size_text = clean_html_text(val_elem.get_text(strip=True))
                    size = size_text.replace("nhân viên", "employees").strip()

    description = ""
    desc_elem = soup.select_one("#AboutUs ul + p")
    if desc_elem:
        description = clean_html_text(desc_elem.get_text(separator="\n", strip=True))

    benefits_list = []
    benefit_section = soup.find(id="Benefit")
    if benefit_section:
        benefit_cols = benefit_section.select('div[id="vnwLayout__col"]')
        for col in benefit_cols:
            title_elem = col.find("h4")
            if title_elem:
                title = clean_html_text(title_elem.get_text(strip=True))
                desc_divs = col.find_all("div")
                if desc_divs:
                    desc = clean_html_text(desc_divs[-1].get_text(strip=True))
                    benefits_list.append(f"{title}: {desc}")

    raw_data = {
        "name": name,
        "industry": industry,
        "size": size,
        "location": location,
        "description": description,
        "website": "",
        "slogan": None,
        "company_type": company_type,
        "country": country,
        "addresses": addresses,
        "working_days": working_days,
        "overtime_policy": overtime_policy,
        "benefits": benefits_list,
    }

    company_obj = adapter_vietnamworks_company(raw_data)

    async with session_factory() as session:
        repo = CompanyRepository(session)
        await repo.save_or_update(company_obj)
        await session.commit()

    context.log.info(f"Successfully updated and saved VietnamWorks Company: '{name}'")
