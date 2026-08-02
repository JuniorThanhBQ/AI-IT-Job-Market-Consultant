import asyncio
import logging
from urllib.parse import urljoin
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
    show_more_selector = selectors.get("show_more_button", "#btnShowMoreJob")
    job_link_selector = selectors.get(
        "job_link", "a.jp_job_post_link, a.top-jobs__item"
    )

    if context._page:
        for i in range(15):
            try:
                button = await context.page.query_selector(show_more_selector)
                if button and await button.is_visible():
                    context.log.info(f"Clicking 'XEM THÊM' button (iteration {i + 1})")
                    await button.click()
                    await asyncio.sleep(2.0)
                else:
                    break
            except Exception as e:
                context.log.warning(f"Failed to click show more button: {e}")
                break
        html_content = await context.page.content()
        soup = BeautifulSoup(html_content, "html.parser")

    anchors = soup.select(job_link_selector)
    enqueued_count = 0

    for a in anchors:
        href = a.get("href")
        if href and "/job/" in href:
            detail_url = urljoin("https://itjobs.com.vn", href)
            await context.add_requests(
                [Request.from_url(url=detail_url, label="detail")]
            )
            enqueued_count += 1

    context.log.info(f"Enqueued {enqueued_count} job detail pages from ITJobs list.")
