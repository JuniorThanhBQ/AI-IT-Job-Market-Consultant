import pytest
from unittest.mock import patch, MagicMock
from agents.tools.crawl4ai_crawler.tasks import run_crawl4ai_task_sync


@patch("agents.tools.crawl4ai_crawler.tasks.asyncio.run")
@patch("agents.tools.crawl4ai_crawler.tasks.run_crawl4ai_main", new_callable=MagicMock)
def test_run_crawl4ai_task_sync_valid(mock_main, mock_run):
    run_crawl4ai_task_sync()
    mock_run.assert_called_once()
    mock_main.assert_called_once()


@patch("agents.tools.crawl4ai_crawler.tasks.asyncio.run")
@patch("agents.tools.crawl4ai_crawler.tasks.run_crawl4ai_main", new_callable=MagicMock)
def test_run_crawl4ai_task_sync_invalid(mock_main, mock_run):
    mock_run.side_effect = RuntimeError("Asyncio failed")
    with pytest.raises(RuntimeError):
        run_crawl4ai_task_sync()
