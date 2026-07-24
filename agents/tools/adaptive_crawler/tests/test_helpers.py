import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agents.tools.adaptive_crawler.helpers import (
    CustomRenderingTypePredictor,
    check_redis_connection,
    generate_session_fingerprint,
)


class TestCheckRedisConnection:
    @patch("agents.tools.adaptive_crawler.helpers.redis.from_url")
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

    @patch("agents.tools.adaptive_crawler.helpers.redis.from_url")
    def test_redis_connection_failure_raises_runtime_error(self, mock_from_url):
        mock_client = AsyncMock()
        mock_client.ping.side_effect = ConnectionError("Connection refused")
        mock_from_url.return_value = mock_client

        async def _run():
            with pytest.raises(RuntimeError, match="Cannot connect to Redis"):
                await check_redis_connection("redis://localhost:6379/0")

        asyncio.run(_run())
        mock_client.aclose.assert_awaited_once()


class TestGenerateSessionFingerprint:
    @patch("agents.tools.adaptive_crawler.helpers._fingerprint_generator.generate")
    def test_generates_valid_fingerprint_dict(self, mock_generate):
        mock_fp = MagicMock()
        mock_fp.navigator.userAgent = "Mock-Agent/1.0"
        mock_fp.screen.width = 1920
        mock_fp.screen.height = 1080
        mock_fp.headers = {"Accept-Language": "vi-VN"}
        mock_generate.return_value = mock_fp

        result = generate_session_fingerprint()

        assert result["user_agent"] == "Mock-Agent/1.0"
        assert result["viewport"] == {"width": 1920, "height": 1080}
        assert result["locale"] == "vi-VN"
        assert result["timezone_id"] == "Asia/Ho_Chi_Minh"
        assert result["extra_http_headers"] == {"Accept-Language": "vi-VN"}


class TestCustomRenderingTypePredictor:
    @pytest.fixture
    def predictor(self):
        return CustomRenderingTypePredictor()

    @pytest.fixture
    def mock_request(self):
        def _make_req(url):
            req = MagicMock()
            req.url = url
            return req

        return _make_req

    def test_predict_known_static_domain(self, predictor, mock_request):
        req = mock_request("https://itviec.com/it-jobs")

        prediction = predictor.predict(req)

        assert prediction.rendering_type == "static"
        assert prediction.detection_probability_recommendation == 0.2

    def test_predict_known_dynamic_domain(self, predictor, mock_request):
        req = mock_request("https://topdev.vn/jobs")

        prediction = predictor.predict(req)

        assert prediction.rendering_type == "client only"
        assert prediction.detection_probability_recommendation == 0.2

    def test_predict_unknown_domain_defaults_to_static(self, predictor, mock_request):
        req = mock_request("https://unknown-domain.com/jobs")

        prediction = predictor.predict(req)

        assert prediction.rendering_type == "static"
        assert prediction.detection_probability_recommendation == 0.5

    def test_store_result_updates_prediction(self, predictor, mock_request):
        req = mock_request("https://unknown-domain.com/jobs")

        predictor.store_result(req, "client only")
        updated_prediction = predictor.predict(req)

        assert updated_prediction.rendering_type == "client only"
        assert updated_prediction.detection_probability_recommendation == 0.2
