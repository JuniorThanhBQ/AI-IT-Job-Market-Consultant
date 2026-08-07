import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.adaptive_crawler.helpers import (
    CustomRenderingTypePredictor,
    check_redis_connection,
)


class TestCheckRedisConnection:
    @patch("tools.adaptive_crawler.helpers.redis.from_url")
    def test_redis_connection_success(self, mock_from_url):
        mock_client = AsyncMock()
        mock_from_url.return_value = mock_client
        redis_url = "redis://localhost:6379/0"

        async def _run():
            await check_redis_connection(redis_url)

        asyncio.run(_run())
        mock_from_url.assert_called_once_with(redis_url)
        mock_client.ping.assert_awaited_once()
        mock_client.aclose.assert_awaited_once()

    @patch("tools.adaptive_crawler.helpers.redis.from_url")
    def test_redis_connection_failure(self, mock_from_url):
        mock_client = AsyncMock()
        mock_client.ping.side_effect = Exception("Connection refused")
        mock_from_url.return_value = mock_client
        redis_url = "redis://localhost:6379/0"

        async def _run():
            with pytest.raises(RuntimeError) as exc_info:
                await check_redis_connection(redis_url)
            assert "Cannot connect to Redis at redis://localhost:6379/0" in str(
                exc_info.value
            )

        asyncio.run(_run())
        mock_from_url.assert_called_once_with(redis_url)
        mock_client.ping.assert_awaited_once()
        mock_client.aclose.assert_awaited_once()


class TestCustomRenderingTypePredictor:
    def test_domain_extraction(self):
        predictor = CustomRenderingTypePredictor()
        assert predictor._domain("https://topdev.vn/jobs") == "topdev.vn"
        assert predictor._domain("https://www.topdev.vn") == "topdev.vn"
        assert predictor._domain("http://sub.itviec.com/") == "sub.itviec.com"

    def test_predict_known_domains(self):
        predictor = CustomRenderingTypePredictor()

        # Dynamic
        req_topdev = MagicMock()
        req_topdev.url = "https://topdev.vn/jobs"
        pred = predictor.predict(req_topdev)
        assert pred.rendering_type == "client only"

        # Static
        req_itviec = MagicMock()
        req_itviec.url = "https://itviec.com/jobs"
        pred = predictor.predict(req_itviec)
        assert pred.rendering_type == "static"

    def test_predict_unknown_domain_defaults_to_static(self):
        predictor = CustomRenderingTypePredictor()
        req_unknown = MagicMock()
        req_unknown.url = "https://unknown-job-site.com"
        pred = predictor.predict(req_unknown)
        assert pred.rendering_type == "static"

    def test_store_result_updates_cache(self):
        predictor = CustomRenderingTypePredictor()
        req = MagicMock()
        req.url = "https://new-site.com/list"

        # Default prediction
        assert predictor.predict(req).rendering_type == "static"

        # Store "client only" result
        predictor.store_result(req, "client only")
        assert predictor.predict(req).rendering_type == "client only"

        # Store "static" result
        predictor.store_result(req, "static")
        assert predictor.predict(req).rendering_type == "static"
