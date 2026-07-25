import logging
import math
import re
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from crawlee import Request
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

logger = logging.getLogger(__name__)


async def process_list_page(
    context: AdaptivePlaywrightCrawlingContext, soup: BeautifulSoup, url: str
) -> None:
    context.log.info(f"Parsing ITViec list page: {url}")
    job_links = soup.select(
        "h3[data-search--job-selection-target='jobTitle'] a, h3.imt-3 a"
    )
    enqueued_count = 0
    seen_urls = set()

    for link in job_links:
        href = link.get("href")
        if href:
            full_url = urljoin("https://itviec.com", href)
            if "?" in full_url:
                full_url = full_url.split("?")[0]
            full_url = full_url.rstrip("/")

            slug = full_url.split("/it-jobs/")[-1] if "/it-jobs/" in full_url else ""
            if slug and any(c.isdigit() for c in slug) and full_url not in seen_urls:
                seen_urls.add(full_url)
                await context.add_requests(
                    [Request.from_url(url=full_url, label="detail")]
                )
                enqueued_count += 1

    context.log.info(f"Enqueued {enqueued_count} job detail pages from ITViec list.")

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    current_page = 1
    if "page" in qs:
        try:
            current_page = int(qs["page"][0])
        except ValueError:
            pass

    max_page = 20
    if enqueued_count > 0:
        h1_elem = soup.find("h1")
        h1_text = h1_elem.get_text() if h1_elem else ""
        match = re.search(r"([\d,]+)\s+IT\s+Jobs", h1_text, re.IGNORECASE)
        if match:
            try:
                total_jobs = int(match.group(1).replace(",", ""))
                max_page = max(1, math.ceil(total_jobs / enqueued_count))
            except ValueError:
                pass
        else:
            page_nums = []
            for page_elem in soup.select("nav.ipagination div.page a"):
                txt = page_elem.get_text(strip=True)
                if txt.isdigit():
                    page_nums.append(int(txt))
            if page_nums:
                max_page = max(page_nums)

    if current_page < max_page and enqueued_count > 0:
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
            f"Enqueuing next ITViec list page ({current_page + 1}/{max_page}): {next_url}"
        )
        await context.add_requests([Request.from_url(url=next_url, label="list")])
