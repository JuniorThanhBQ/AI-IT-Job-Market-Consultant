import logging

from ..base_factory import BaseCrawlerFactory
from .itjobs_process_company_page import process_company_page
from .itjobs_process_detail_page import process_detail_page
from .itjobs_process_list_page import process_list_page

logger = logging.getLogger(__name__)


class ITJobsCrawlerFactory(BaseCrawlerFactory):
    async def process_detail(self, context, soup, url, session_factory):
        await process_detail_page(context, soup, url, session_factory)

    async def process_company(self, context, soup, url, session_factory):
        await process_company_page(context, soup, url, session_factory)

    async def process_list(self, context, soup, url, config=None):
        await process_list_page(context, soup, url, config)
