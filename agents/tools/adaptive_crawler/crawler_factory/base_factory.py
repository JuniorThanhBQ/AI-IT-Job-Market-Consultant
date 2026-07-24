from abc import ABC, abstractmethod
import asyncio
from datetime import timedelta
import random

from crawlee import ConcurrencySettings
from crawlee.crawlers import AdaptivePlaywrightCrawler
from crawlee.events import LocalEventManager
from crawlee.storage_clients import RedisStorageClient
from crawlee.storages import RequestQueue

from ..config_crawler import (
    BROWSER_TYPE,
    HEADLESS,
    MAX_CONCURRENCY,
    MAX_DELAY_SECONDS,
    MAX_REQUEST_RETRIES,
    MAX_REQUESTS_PER_CRAWL,
    MIN_DELAY_SECONDS,
    REDIS_URL,
    REQUEST_HANDLER_TIMEOUT_SECONDS,
)
from ..helpers import CustomRenderingTypePredictor, generate_session_fingerprint


class BaseCrawlerFactory(ABC):
    @abstractmethod
    def get_handler(self, session_factory):
        pass

    async def apply_delay(self) -> None:
        await asyncio.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))

    def get_browser_context_options(self) -> dict:
        return generate_session_fingerprint()

    async def handle_error(self, context, error) -> None:
        context.log.warning(
            f"[{self.__class__.__name__}] Request failed (retry): "
            f"{context.request.url} — {error}"
        )

    async def handle_failed_request(self, context, error) -> None:
        context.log.error(
            f"[{self.__class__.__name__}] Request permanently failed after retries: "
            f"{context.request.url} — {error}"
        )

    async def create_crawler(
        self,
        session_factory,
        storage_client: RedisStorageClient | None = None,
        event_manager: LocalEventManager | None = None,
    ) -> AdaptivePlaywrightCrawler:
        predictor = CustomRenderingTypePredictor()
        site_name = self.__class__.__name__.lower().replace("crawlerfactory", "")

        if storage_client is None:
            storage_client = RedisStorageClient(connection_string=REDIS_URL)

        if event_manager is None:
            event_manager = LocalEventManager.from_config()

        request_queue = await RequestQueue.open(
            name=f"rq-{site_name}", storage_client=storage_client
        )

        crawler = AdaptivePlaywrightCrawler.with_beautifulsoup_static_parser(
            max_requests_per_crawl=MAX_REQUESTS_PER_CRAWL,
            max_request_retries=MAX_REQUEST_RETRIES,
            concurrency_settings=ConcurrencySettings(
                max_concurrency=MAX_CONCURRENCY, desired_concurrency=MAX_CONCURRENCY
            ),
            request_handler_timeout=timedelta(seconds=REQUEST_HANDLER_TIMEOUT_SECONDS),
            rendering_type_predictor=predictor,
            request_manager=request_queue,
            playwright_crawler_specific_kwargs={
                "browser_type": BROWSER_TYPE,
                "headless": HEADLESS,
                "browser_launch_options": {
                    "args": [
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                    ]
                },
                "browser_new_context_options": self.get_browser_context_options(),
            },
            storage_client=storage_client,
            event_manager=event_manager,
        )

        handler = self.get_handler(session_factory)
        crawler.router.default_handler(handler)
        crawler.error_handler(self.handle_error)
        crawler.failed_request_handler(self.handle_failed_request)

        return crawler
