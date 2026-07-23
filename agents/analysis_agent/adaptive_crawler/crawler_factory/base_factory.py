from abc import ABC, abstractmethod
from datetime import timedelta
from crawlee import ConcurrencySettings
from crawlee.configuration import Configuration
from crawlee.crawlers import AdaptivePlaywrightCrawler
from crawlee.events import LocalEventManager
from crawlee.storage_clients import FileSystemStorageClient

from ..helpers import CustomRenderingTypePredictor
from ..config_crawler import (
    MAX_REQUESTS_PER_CRAWL,
    MAX_REQUEST_RETRIES,
    MAX_CONCURRENCY,
    REQUEST_HANDLER_TIMEOUT_SECONDS,
    BROWSER_TYPE,
    HEADLESS,
)


class BaseCrawlerFactory(ABC):
    @abstractmethod
    def get_handler(self, session_factory):
        pass

    def get_browser_context_options(self) -> dict:
        return {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "locale": "vi-VN",
            "extra_http_headers": {
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            "viewport": {"width": 1280, "height": 720},
        }

    async def handle_error(self, context, error) -> None:
        context.log.warning(
            f"[{self.__class__.__name__}] Request failed (will retry): "
            f"{context.request.url} — {error}"
        )

    async def handle_failed_request(self, context, error) -> None:
        context.log.error(
            f"[{self.__class__.__name__}] Request permanently failed after retries: "
            f"{context.request.url} — {error}"
        )

    def create_crawler(
        self, session_factory, storage_dir: str | None = None
    ) -> AdaptivePlaywrightCrawler:
        predictor = CustomRenderingTypePredictor()

        config = Configuration(storage_dir=storage_dir) if storage_dir else None
        storage_client = FileSystemStorageClient()
        event_manager = LocalEventManager.from_config(config)

        crawler = AdaptivePlaywrightCrawler.with_beautifulsoup_static_parser(
            max_requests_per_crawl=MAX_REQUESTS_PER_CRAWL,
            max_request_retries=MAX_REQUEST_RETRIES,
            concurrency_settings=ConcurrencySettings(
                max_concurrency=MAX_CONCURRENCY, desired_concurrency=MAX_CONCURRENCY
            ),
            request_handler_timeout=timedelta(seconds=REQUEST_HANDLER_TIMEOUT_SECONDS),
            rendering_type_predictor=predictor,
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
            configuration=config,
            storage_client=storage_client,
            event_manager=event_manager,
        )

        handler = self.get_handler(session_factory)
        crawler.router.default_handler(handler)
        crawler.error_handler(self.handle_error)
        crawler.failed_request_handler(self.handle_failed_request)

        return crawler
