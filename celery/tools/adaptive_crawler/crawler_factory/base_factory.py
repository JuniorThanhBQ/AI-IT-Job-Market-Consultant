from abc import ABC, abstractmethod
import asyncio
from datetime import timedelta
import json
import os
import random
from typing import cast, Any
import sys

from bs4 import BeautifulSoup
from crawlee import ConcurrencySettings
from crawlee.crawlers import (
    AdaptivePlaywrightCrawler,
    AdaptivePlaywrightCrawlingContext,
)
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


async def _open_queue(site_name: str, storage_client) -> RequestQueue:
    return await RequestQueue.open(
        name=f"rq-{site_name}", storage_client=storage_client
    )


class BaseCrawlerFactory(ABC):
    def __init__(self) -> None:
        self.existing_urls: set[str] = set()

    @abstractmethod
    async def process_detail(self, context, soup, url, session_factory):
        pass

    @abstractmethod
    async def process_company(self, context, soup, url, session_factory):
        pass

    @abstractmethod
    async def process_list(self, context, soup, url, config=None):
        pass

    def _load_config(self) -> dict:
        module = sys.modules[self.__module__]
        module_file = module.__file__
        if not module_file:
            module_dir = "."
        else:
            module_dir = os.path.dirname(module_file)
        site_name = self.__class__.__name__.lower().replace("crawlerfactory", "")
        config_path = os.path.join(module_dir, f"{site_name}_templates.json")

        if os.path.exists(config_path) and os.path.getsize(config_path) > 0:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {
                    "rules": {
                        "detail": {"labels": ["detail"]},
                        "company": {"labels": ["company"]},
                    },
                    "settings": {"wait_for_networkidle": False},
                }

        return {
            "rules": {
                "detail": {"labels": ["detail"]},
                "company": {"labels": ["company"]},
            },
            "settings": {"wait_for_networkidle": False},
        }

    def _matches_rules(self, url: str, label: str, rule_cfg: dict) -> bool:
        if label in rule_cfg.get("labels", []):
            return True

        contains = rule_cfg.get("url_contains", [])
        not_contains = rule_cfg.get("url_not_contains", [])

        if contains:
            matches_contains = any(c in url for c in contains)
            matches_not_contains = not any(nc in url for nc in not_contains)

            if matches_contains and matches_not_contains:
                special_rules = rule_cfg.get("special_rules", [])
                if "itviec_detail_slug_digits" in special_rules:
                    clean_url = url.split("?")[0].rstrip("/")
                    path_slug = (
                        clean_url.split("/it-jobs/")[-1]
                        if "/it-jobs/" in clean_url
                        else ""
                    )
                    if path_slug == "" or not any(char.isdigit() for char in path_slug):
                        return False
                return True

        return False

    def get_handler(self, session_factory):
        async def handler(context: AdaptivePlaywrightCrawlingContext) -> None:
            url = context.request.url
            await self.apply_delay()

            site_name = self.__class__.__name__.replace("CrawlerFactory", "")
            context.log.info(
                f"Crawling {site_name}: {url} (label: {context.request.label})"
            )

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

            config = self._load_config()
            rules = config.get("rules", {})
            settings = config.get("settings", {})

            is_detail = self._matches_rules(
                url, context.request.label or "", rules.get("detail", {})
            )
            is_company = self._matches_rules(
                url, context.request.label or "", rules.get("company", {})
            )

            if context._page and settings.get("wait_for_networkidle", False):
                try:
                    context.log.info(
                        f"Waiting for {site_name} page to fully load: {url}"
                    )
                    await context.page.wait_for_load_state("load", timeout=30000)
                    new_html = await context.page.content()
                    soup = BeautifulSoup(new_html, "html.parser")
                except Exception as e:
                    context.log.warning(
                        f"Timeout/Error waiting for page load, falling back to initial HTML: {e}"
                    )

            if is_detail:
                await self.process_detail(context, soup, url, session_factory)
                self.existing_urls.add(url)
            elif is_company:
                await self.process_company(context, soup, url, session_factory)
            else:
                await self.process_list(context, soup, url, config)

        return handler

    def get_browser_context_options(self) -> dict:
        return generate_session_fingerprint()

    async def apply_delay(self) -> None:
        await asyncio.sleep(
            random.SystemRandom().uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
        )

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
        async with session_factory() as session:
            from tools.adaptive_crawler.crawler_repository.job_repository import (
                JobRepository,
            )

            repo = JobRepository(session)
            urls = await repo.get_all_urls()
            self.existing_urls = set(urls)

        predictor = CustomRenderingTypePredictor()
        site_name = self.__class__.__name__.lower().replace("crawlerfactory", "")

        if storage_client is None:
            storage_client = RedisStorageClient(connection_string=REDIS_URL)

        if event_manager is None:
            event_manager = LocalEventManager.from_config()

        request_queue = await _open_queue(site_name, storage_client)
        await request_queue.drop()
        request_queue = await _open_queue(site_name, storage_client)

        crawler = AdaptivePlaywrightCrawler.with_beautifulsoup_static_parser(
            max_requests_per_crawl=MAX_REQUESTS_PER_CRAWL,
            max_request_retries=MAX_REQUEST_RETRIES,
            concurrency_settings=ConcurrencySettings(
                max_concurrency=MAX_CONCURRENCY,
                desired_concurrency=(
                    MAX_CONCURRENCY if MAX_CONCURRENCY == 1 else MAX_CONCURRENCY - 1
                ),
            ),
            request_handler_timeout=timedelta(seconds=REQUEST_HANDLER_TIMEOUT_SECONDS),
            rendering_type_predictor=predictor,
            request_manager=request_queue,
            playwright_crawler_specific_kwargs=cast(
                Any,
                {
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
            ),
            storage_client=storage_client,
            event_manager=event_manager,
        )

        handler = self.get_handler(session_factory)
        crawler.router.default_handler(handler)
        crawler.error_handler(self.handle_error)
        crawler.failed_request_handler(self.handle_failed_request)

        return crawler
