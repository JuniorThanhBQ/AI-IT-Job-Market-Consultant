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
    context.log.info(f"Parsing VietnamWorks list page: {url}")

    if context.page:
        context.log.info("Scrolling page to trigger lazy-load elements...")
        import asyncio

        for _ in range(5):
            await context.page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)"
            )
            await asyncio.sleep(1)
        html_content = await context.page.content()
        soup = BeautifulSoup(html_content, "html.parser")

    selectors = config.get("selectors", {}) if config else {}
    job_link_selector = selectors.get(
        "job_link",
        "a[href*='/job/'], a[href*='/viec-lam/'], a[href*='jobs/'], a[href$='-jv'], a[href*='-jv?']",
    )

    job_links = soup.select(job_link_selector)
    enqueued_count = 0
    seen_urls = set()

    for link in job_links:
        href = link.get("href")
        if not href or not isinstance(href, str):
            continue

        full_url = urljoin("https://www.vietnamworks.com", href)
        if "?" in full_url:
            full_url = full_url.split("?")[0]
        full_url = full_url.rstrip("/")

        if full_url and full_url not in seen_urls:
            seen_urls.add(full_url)
            await context.add_requests([Request.from_url(url=full_url, label="detail")])
            enqueued_count += 1

    context.log.info(
        f"Enqueued {enqueued_count} job detail pages from VietnamWorks list."
    )

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
        total_jobs = None

        title_text = ""
        title_elem = soup.find("title")
        if title_elem:
            title_text = title_elem.get_text(" ", strip=True)

        if title_text:
            match = re.search(
                r"([\d,]+)\s+việc\s+làm|([\d,]+)\s+jobs?|([\d,]+)\s+positions?",
                title_text,
                re.IGNORECASE,
            )
            if match:
                for group in match.groups():
                    if group:
                        try:
                            total_jobs = int(group.replace(",", ""))
                            break
                        except ValueError:
                            continue

        if total_jobs is None:
            count_candidates = []
            for label in soup.select("label"):
                text = " ".join(label.get_text(" ", strip=True).split())
                if not text:
                    continue
                match = re.search(r"\((\d+)\)", text)
                if match:
                    count_candidates.append(int(match.group(1)))
            if count_candidates:
                total_jobs = max(count_candidates)

        if total_jobs is not None:
            max_page = max(1, math.ceil(total_jobs / enqueued_count))

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
                f"Enqueuing next VietnamWorks list page ({current_page + 1}/{max_page}): {next_url}"
            )
            await context.add_requests([Request.from_url(url=next_url, label="list")])
