import logging
from bs4 import BeautifulSoup
from crawlee.crawlers import AdaptivePlaywrightCrawlingContext

logger = logging.getLogger(__name__)


async def process_company_page(
    context: AdaptivePlaywrightCrawlingContext,
    soup: BeautifulSoup,
    url: str,
    session_factory,
) -> None:
    pass
