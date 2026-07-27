import logging
from bs4 import BeautifulSoup
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

from ..base_factory import BaseCrawlerFactory
from .itjobs_process_company_page import process_company_page
from .itjobs_process_detail_page import process_detail_page
from .itjobs_process_list_page import process_list_page

logger = logging.getLogger(__name__)


class ITJobsCrawlerFactory(BaseCrawlerFactory):
    def get_handler(self, session_factory):
        async def handler(context: AdaptivePlaywrightCrawlingContext) -> None:
            url = context.request.url

            await self.apply_delay()

            context.log.info(f"Crawling ITJobs: {url} (label: {context.request.label})")

            html_content = ""
            if context._page:
                html_content = await context.page.content()
            elif context.http_response:
                html_content = (await context.http_response.read()).decode(
                    "utf-8", errors="ignore"
                )

            if not html_content:
                context.log.warning(f"Empty content for URL: {url}")
                return

            soup = BeautifulSoup(html_content, "html.parser")

            is_detail = context.request.label in ["detail", "updater_detail"] or (
                "/job/" in url and "/search" not in url
            )

            is_company = context.request.label == "company" or "/company/" in url

            if is_detail:
                await process_detail_page(context, soup, url, session_factory)
            elif is_company:
                await process_company_page(context, soup, url, session_factory)
            else:
                await process_list_page(context, soup, url)

        return handler
