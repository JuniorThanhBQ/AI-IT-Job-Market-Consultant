import logging
import math
import re
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from crawlee import Request
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

logger = logging.getLogger(__name__)


async def process_list_page(
    context: AdaptivePlaywrightCrawlingContext,
    soup: BeautifulSoup,
    url: str,
    config: dict | None = None,
) -> None:
    context.log.info(f"Parsing list page for URLs: {url}")

    selectors = config.get("selectors", {}) if config else {}
    job_link_selector = selectors.get(
        "job_link", 'a.line-clamp-3[href*="/detail-jobs/"]'
    )

    links = soup.select(job_link_selector)
    enqueued_count = 0

    for link in links:
        href = link.get("href")
        if href and isinstance(href, str):
            detail_url = urljoin("https://topdev.vn", href)
            await context.add_requests(
                [Request.from_url(url=detail_url, label="detail")]
            )
            enqueued_count += 1

    context.log.info(f"Enqueued {enqueued_count} job detail pages from TopDev list.")

    if enqueued_count > 0:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        current_page = 1
        if "page" in qs:
            try:
                current_page = int(qs["page"][0])
            except ValueError:
                pass

        max_page = 15
        title_elem = soup.find("title")
        title_text = title_elem.get_text() if title_elem else ""
        match = re.search(
            r"Recruiting\s+([\d,]+)\s+positions?", title_text, re.IGNORECASE
        )
        if match:
            try:
                total_jobs = int(match.group(1).replace(",", ""))
                max_page = max(1, math.ceil(total_jobs / enqueued_count))
            except ValueError:
                pass

        if current_page < max_page:
            qs["page"] = [str(current_page + 1)]
            next_url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    urlencode(qs, doseq=True),
                    parsed.fragment,
                )
            )
            context.log.info(
                f"Enqueuing next TopDev list page ({current_page + 1}/{max_page}): {next_url}"
            )
            await context.add_requests([Request.from_url(url=next_url, label="list")])
