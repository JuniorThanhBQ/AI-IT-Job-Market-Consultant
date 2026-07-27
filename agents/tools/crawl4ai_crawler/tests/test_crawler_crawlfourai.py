import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from agents.tools.crawl4ai_crawler.crawler import clean_json_string, run_crawl4ai_main


def test_clean_json_string_valid():
    assert clean_json_string('```json\n{"key": "value"}\n```') == '{"key": "value"}'
    assert clean_json_string("```\n[1, 2, 3]\n```") == "[1, 2, 3]"
    assert clean_json_string('{"test": 123}') == '{"test": 123}'


def test_clean_json_string_invalid():
    assert clean_json_string("") == ""
    assert clean_json_string("   ") == ""
    assert clean_json_string("```json") == ""


@pytest.mark.asyncio
@patch("agents.tools.crawl4ai_crawler.crawler.create_async_engine")
@patch("agents.tools.crawl4ai_crawler.crawler.sessionmaker")
@patch("agents.tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
@patch("agents.tools.crawl4ai_crawler.crawler.JobRepository")
@patch("agents.tools.crawl4ai_crawler.crawler.crawl4ai_adapter")
async def test_run_crawl4ai_main_valid(
    mock_adapter, mock_job_repo, mock_crawler_cls, mock_sessionmaker, mock_engine_func
):
    # 1. Setup mock cho 'async with engine.begin() as conn'
    mock_conn = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dialect.name = "postgresql"
    mock_engine.begin.return_value.__aenter__.return_value = mock_conn
    mock_engine.dispose = AsyncMock()  # Dành cho await engine.dispose()
    mock_engine_func.return_value = mock_engine

    # 2. Setup mock cho 'async with session_factory() as session'
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_sessionmaker.return_value = MagicMock(return_value=mock_session)

    # 3. Setup mock cho Repo
    mock_repo_instance = MagicMock()
    mock_repo_instance.save_or_update = AsyncMock()
    mock_job_repo.return_value = mock_repo_instance

    # 4. Setup mock cho 'async with AsyncWebCrawler() as crawler'
    mock_crawler_instance = AsyncMock()
    mock_crawler_cls.return_value.__aenter__.return_value = mock_crawler_instance

    # Mock kết quả crawl
    list_result = MagicMock()
    list_result.extracted_content = '[{"url": "/job/1"}]'

    detail_result = MagicMock()
    detail_result.extracted_content = '{"title": "Dev", "company_name": "ABC"}'

    mock_crawler_instance.arun.side_effect = [list_result, detail_result]
    mock_adapter.return_value = MagicMock()

    await run_crawl4ai_main()

    assert mock_crawler_instance.arun.call_count == 2
    mock_repo_instance.save_or_update.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_engine.dispose.assert_called_once()


@pytest.mark.asyncio
@patch("agents.tools.crawl4ai_crawler.crawler.create_async_engine")
@patch("agents.tools.crawl4ai_crawler.crawler.sessionmaker")
@patch("agents.tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
async def test_run_crawl4ai_main_invalid_no_content(
    mock_crawler_cls, mock_sessionmaker, mock_engine_func
):
    mock_conn = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.begin.return_value.__aenter__.return_value = mock_conn
    mock_engine.dispose = AsyncMock()
    mock_engine_func.return_value = mock_engine

    mock_crawler_instance = AsyncMock()
    mock_crawler_cls.return_value.__aenter__.return_value = mock_crawler_instance

    list_result = MagicMock()
    list_result.extracted_content = None
    mock_crawler_instance.arun.return_value = list_result

    await run_crawl4ai_main()

    assert mock_crawler_instance.arun.call_count == 1
    mock_engine.dispose.assert_called_once()


@pytest.mark.asyncio
@patch("agents.tools.crawl4ai_crawler.crawler.create_async_engine")
@patch("agents.tools.crawl4ai_crawler.crawler.sessionmaker")
@patch("agents.tools.crawl4ai_crawler.crawler.AsyncWebCrawler")
@patch("agents.tools.crawl4ai_crawler.crawler.JobRepository")
@patch("agents.tools.crawl4ai_crawler.crawler.crawl4ai_adapter")
async def test_run_crawl4ai_main_invalid_db_error(
    mock_adapter, mock_job_repo, mock_crawler_cls, mock_sessionmaker, mock_engine_func
):
    mock_conn = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.dialect.name = "postgresql"
    mock_engine.begin.return_value.__aenter__.return_value = mock_conn
    mock_engine.dispose = AsyncMock()
    mock_engine_func.return_value = mock_engine

    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_sessionmaker.return_value = MagicMock(return_value=mock_session)

    mock_repo_instance = MagicMock()
    mock_repo_instance.save_or_update = AsyncMock(side_effect=Exception("DB Error"))
    mock_job_repo.return_value = mock_repo_instance

    mock_crawler_instance = AsyncMock()
    mock_crawler_cls.return_value.__aenter__.return_value = mock_crawler_instance

    list_result = MagicMock()
    list_result.extracted_content = '[{"url": "/job/1"}]'

    detail_result = MagicMock()
    detail_result.extracted_content = '{"title": "Dev"}'

    mock_crawler_instance.arun.side_effect = [list_result, detail_result]
    mock_adapter.return_value = MagicMock()

    await run_crawl4ai_main()

    mock_session.rollback.assert_called_once()
    mock_engine.dispose.assert_called_once()
