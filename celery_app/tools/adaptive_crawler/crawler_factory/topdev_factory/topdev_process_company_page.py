import logging

from bs4 import BeautifulSoup
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

from ...crawler_adapter.topdev_adapter import adapter_topdev_company
from ...crawler_repository import CompanyRepository

logger = logging.getLogger(__name__)


async def process_company_page(
    context: AdaptivePlaywrightCrawlingContext,
    soup: BeautifulSoup,
    url: str,
    session_factory,
) -> None:
    context.log.info(f"Extracting company page: {url}")
    name_elem = soup.find(
        lambda tag: (
            tag.name == "span"
            and tag.get("class")
            and all(
                c in tag.get("class") for c in ["block", "text-xl", "font-semibold"]
            )
        )
    )
    name = name_elem.get_text(strip=True) if name_elem else ""

    if not name:
        context.log.warning(f"Company profile has no name: {url}")
        return

    industry = "Unknown"
    size = "Unknown"
    company_type = None
    country = "Unknown"
    location = "Vietnam"
    slogan_elem = soup.find(
        "span",
        class_=lambda c: (
            c
            and all(
                cls in c
                for cls in [
                    "block",
                    "text-sm",
                    "font-medium",
                    "text-text-700",
                    "md:my-1",
                    "md:text-base",
                ]
            )
        ),
    )
    slogan = slogan_elem.get_text(strip=True) if slogan_elem else None
    description = ""
    website = ""
    benefits_list = []

    loc_spans = soup.find_all("span", class_="flex text-sm text-text-400")
    for span in loc_spans:
        if span.find("svg"):
            location = span.get_text(strip=True)
            break

    def find_label_span(keyword):
        return soup.find(
            lambda tag: (
                tag.name == "span"
                and tag.get_text(strip=True)
                and keyword in tag.get_text(strip=True).lower()
            )
        )

    country_lbl = find_label_span("country")
    if country_lbl and country_lbl.parent:
        val_span = country_lbl.parent.find(
            "span",
            class_=lambda c: c and "font-semibold" in c and "text-text-700" in c,
        )
        if val_span:
            country = val_span.get_text(strip=True)

    industry_lbl = find_label_span("industry")
    if industry_lbl and industry_lbl.parent:
        val_spans = industry_lbl.parent.find_all(
            "span",
            class_=lambda c: c and "font-semibold" in c and "text-text-700" in c,
        )
        industry = ", ".join([s.get_text(strip=True) for s in val_spans])

    size_lbl = find_label_span("size")
    if size_lbl and size_lbl.parent:
        val_span = size_lbl.parent.find(
            "span",
            class_=lambda c: c and "font-semibold" in c and "text-text-700" in c,
        )
        if val_span:
            size = val_span.get_text(strip=True)

    overview_lbl = find_label_span("company overview")
    description = ""

    if overview_lbl and overview_lbl.parent:
        desc_div = overview_lbl.parent.find("div", class_="text-gray-700")

        if desc_div:
            paragraphs = desc_div.find_all("p")
            if paragraphs:
                description = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
            else:
                description = desc_div.get_text(separator="\n", strip=True)

    benefits_lbl = find_label_span("benefits")
    if benefits_lbl and benefits_lbl.parent:
        ul_elem = benefits_lbl.parent.find("ul")
        if ul_elem:
            for li in ul_elem.find_all("li"):
                txt = li.get_text(strip=True)
                if txt:
                    benefits_list.append(txt.strip())

    website_span = soup.find("span", string=lambda s: s and "Company Website" in s)
    if website_span:
        website_link = website_span.find_parent("a")
        if website_link:
            href = website_link.get("href", "")
            if isinstance(href, str):
                website = href

    raw_data = {
        "url": url,
        "location": location,
        "company_info": {
            "name": name,
            "industry": industry,
            "type": company_type,
            "size": size,
            "description": description,
            "profile_url": website,
            "country": country,
            "addresses": [location] if location else [],
        },
        "benefits": benefits_list,
        "slogan": slogan,
    }

    company_obj = adapter_topdev_company(raw_data)
    async with session_factory() as session:
        company_repo = CompanyRepository(session)
        await company_repo.save_or_update(company_obj)
        await session.commit()
    context.log.info(f"Successfully saved company information for: {name}")
