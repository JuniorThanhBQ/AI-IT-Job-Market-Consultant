import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tools.crawl4ai_crawler.crawler import run_crawl4ai_main


@pytest.mark.asyncio
class TestCrawlerListProcessing:
    @patch("tools.crawl4ai_crawler.crawler.URLS", ["http://base.com"])
    @patch("tools.crawl4ai_crawler.crawler.create_async_engine")
    @patch("tools.crawl4ai_crawler.crawler.async_sessionmaker")
    @patch("tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
    async def test_empty_list_content(
        self, mock_crawler_class, mock_sessionmaker, mock_engine
    ):
        mock_engine.return_value.begin.return_value = AsyncMock()
        mock_engine.return_value.dispose = AsyncMock()

        mock_crawler_instance = AsyncMock()
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler_instance

        mock_list_result = MagicMock()
        mock_list_result.extracted_content = None
        mock_crawler_instance.arun.return_value = mock_list_result

        await run_crawl4ai_main()

        mock_crawler_instance.arun.assert_called_once()
        assert mock_crawler_instance.arun.call_count == 1

    @patch("tools.crawl4ai_crawler.crawler.URLS", ["http://base.com"])
    @patch("tools.crawl4ai_crawler.crawler.create_async_engine")
    @patch("tools.crawl4ai_crawler.crawler.async_sessionmaker")
    @patch("tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
    @patch("tools.crawl4ai_crawler.crawler.clean_json_string")
    @patch("tools.crawl4ai_crawler.crawler.logger.error")
    async def test_invalid_json_in_list(
        self,
        mock_logger_error,
        mock_clean,
        mock_crawler_class,
        mock_sessionmaker,
        mock_engine,
    ):
        mock_engine.return_value.begin.return_value = AsyncMock()
        mock_engine.return_value.dispose = AsyncMock()

        mock_crawler_instance = AsyncMock()
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler_instance

        mock_list_result = MagicMock()
        mock_list_result.extracted_content = "invalid json"
        mock_crawler_instance.arun.return_value = mock_list_result
        mock_clean.return_value = "invalid json"

        await run_crawl4ai_main()

        mock_logger_error.assert_called_once()
        assert "Error processing http://base.com" in mock_logger_error.call_args[0][0]

    @patch("tools.crawl4ai_crawler.crawler.URLS", ["http://base.com"])
    @patch("tools.crawl4ai_crawler.crawler.MAX_JOBS_TO_CRAWL", 1)
    @patch("tools.crawl4ai_crawler.crawler.create_async_engine")
    @patch("tools.crawl4ai_crawler.crawler.async_sessionmaker")
    @patch("tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
    @patch("tools.crawl4ai_crawler.crawler.clean_json_string")
    async def test_valid_list_truncation(
        self, mock_clean, mock_crawler_class, mock_sessionmaker, mock_engine
    ):
        mock_engine.return_value.begin.return_value = AsyncMock()
        mock_engine.return_value.dispose = AsyncMock()

        mock_crawler_instance = AsyncMock()
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler_instance

        mock_list_result = MagicMock()
        mock_list_result.extracted_content = "valid json"

        mock_detail_result = MagicMock()
        mock_detail_result.extracted_content = None

        mock_crawler_instance.arun.side_effect = [
            mock_list_result,
            mock_detail_result,
        ]

        mock_clean.return_value = json.dumps([{"url": "/job1"}, {"url": "/job2"}])

        await run_crawl4ai_main()

        assert mock_crawler_instance.arun.call_count == 2


@pytest.mark.asyncio
class TestCrawlerDetailProcessing:
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.patch_urls = patch(
            "tools.crawl4ai_crawler.crawler.URLS", ["http://base.com"]
        )
        self.patch_urls.start()

        self.patch_engine = patch("tools.crawl4ai_crawler.crawler.create_async_engine")
        self.mock_engine = self.patch_engine.start()
        self.mock_engine.return_value.begin.return_value = AsyncMock()
        self.mock_engine.return_value.dispose = AsyncMock()

        self.patch_sessionmaker = patch(
            "tools.crawl4ai_crawler.crawler.async_sessionmaker"
        )
        self.mock_sessionmaker = self.patch_sessionmaker.start()

        self.mock_session = AsyncMock()
        self.mock_sessionmaker.return_value = MagicMock(return_value=self.mock_session)
        self.mock_session.__aenter__.return_value = self.mock_session

        self.patch_crawler = patch("tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
        self.mock_crawler_class = self.patch_crawler.start()
        self.mock_crawler_instance = AsyncMock()
        self.mock_crawler_class.return_value.__aenter__.return_value = (
            self.mock_crawler_instance
        )

        self.patch_repo = patch("tools.crawl4ai_crawler.crawler.JobRepository")
        self.mock_repo_class = self.patch_repo.start()
        self.mock_repo_instance = AsyncMock()
        self.mock_repo_class.return_value = self.mock_repo_instance

        self.patch_adapter = patch("tools.crawl4ai_crawler.crawler.crawl4ai_adapter")
        self.mock_adapter = self.patch_adapter.start()

        yield

        self.patch_urls.stop()
        self.patch_engine.stop()
        self.patch_sessionmaker.stop()
        self.patch_crawler.stop()
        self.patch_repo.stop()
        self.patch_adapter.stop()

    @patch("tools.crawl4ai_crawler.crawler.clean_json_string")
    async def test_detail_empty_list(self, mock_clean):
        mock_list_result = MagicMock()
        mock_list_result.extracted_content = "list content"

        mock_detail_result = MagicMock()
        mock_detail_result.extracted_content = "detail content"

        self.mock_crawler_instance.arun.side_effect = [
            mock_list_result,
            mock_detail_result,
        ]
        mock_clean.side_effect = [
            json.dumps([{"url": "/job1"}]),
            json.dumps([]),
        ]

        await run_crawl4ai_main()

        self.mock_adapter.assert_not_called()
        self.mock_session.commit.assert_not_called()

    @patch("tools.crawl4ai_crawler.crawler.clean_json_string")
    async def test_detail_valid_list_and_commit(self, mock_clean):
        mock_list_result = MagicMock()
        mock_list_result.extracted_content = "list content"

        mock_detail_result = MagicMock()
        mock_detail_result.extracted_content = "detail content"

        self.mock_crawler_instance.arun.side_effect = [
            mock_list_result,
            mock_detail_result,
        ]
        mock_clean.side_effect = [
            json.dumps([{"url": "/job1"}]),
            json.dumps([{"title": "Job A"}]),
        ]

        self.mock_adapter.return_value = MagicMock()

        await run_crawl4ai_main()

        self.mock_adapter.assert_called_once()
        self.mock_repo_instance.save_or_update.assert_called_once()
        self.mock_session.commit.assert_called_once()

    @patch("tools.crawl4ai_crawler.crawler.clean_json_string")
    async def test_detail_valid_dict_and_commit(self, mock_clean):
        mock_list_result = MagicMock()
        mock_list_result.extracted_content = "list content"

        mock_detail_result = MagicMock()
        mock_detail_result.extracted_content = "detail content"

        self.mock_crawler_instance.arun.side_effect = [
            mock_list_result,
            mock_detail_result,
        ]
        mock_clean.side_effect = [
            json.dumps([{"url": "/job1"}]),
            json.dumps({"title": "Job A"}),
        ]

        self.mock_adapter.return_value = MagicMock()

        await run_crawl4ai_main()

        self.mock_adapter.assert_called_once()
        self.mock_repo_instance.save_or_update.assert_called_once()
        self.mock_session.commit.assert_called_once()

    @patch("tools.crawl4ai_crawler.crawler.clean_json_string")
    async def test_detail_db_rollback_on_error(self, mock_clean):
        mock_list_result = MagicMock()
        mock_list_result.extracted_content = "list content"

        mock_detail_result = MagicMock()
        mock_detail_result.extracted_content = "detail content"

        self.mock_crawler_instance.arun.side_effect = [
            mock_list_result,
            mock_detail_result,
        ]
        mock_clean.side_effect = [
            json.dumps([{"url": "/job1"}]),
            json.dumps({"title": "Job A"}),
        ]

        self.mock_adapter.return_value = MagicMock()
        self.mock_repo_instance.save_or_update.side_effect = Exception("DB Error")

        await run_crawl4ai_main()

        self.mock_session.commit.assert_not_called()
        self.mock_session.rollback.assert_called_once()
