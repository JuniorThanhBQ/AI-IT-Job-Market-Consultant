import logging
from bs4 import BeautifulSoup
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

from ..base_factory import BaseCrawlerFactory
from .itviec_process_company_page import process_company_page
from .itviec_process_detail_page import process_detail_page
from .itviec_process_list_page import process_list_page

logger = logging.getLogger(__name__)


class ITViecCrawlerFactory(BaseCrawlerFactory):
    def get_handler(self, session_factory):
        async def handler(context: AdaptivePlaywrightCrawlingContext) -> None:
            url = context.request.url
            await self.apply_delay()

            html_content = ""
            if context._page:
                html_content = await context.page.content()
            elif context.http_response:
                html_content = (await context.http_response.read()).decode(
                    "utf-8", errors="ignore"
                )

            if not html_content:
                context.log.warning(f"Empty HTML content received for URL: {url}")
                return

            soup = BeautifulSoup(html_content, "html.parser")

            clean_url = url.split("?")[0].rstrip("/")
            path_slug = (
                clean_url.split("/it-jobs/")[-1] if "/it-jobs/" in clean_url else ""
            )

            is_detail = context.request.label in ["detail"] or (
                "/it-jobs/" in clean_url
                and path_slug != ""
                and any(char.isdigit() for char in path_slug)
            )
            is_company = context.request.label == "company" or "/companies/" in url

            if is_detail:
                await process_detail_page(context, soup, url, session_factory)
            elif is_company:
                await process_company_page(context, soup, url, session_factory)
            else:
                await process_list_page(context, soup, url)

        return handler
