from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from crawlee import Request
from tools.adaptive_crawler.helpers import (
    CustomRenderingTypePredictor,
    check_redis_connection,
    generate_session_fingerprint,
)


@patch("tools.adaptive_crawler.helpers.fingerprint_generator")
def test_generate_session_fingerprint(mock_fp_generator: MagicMock) -> None:
    mock_navigator = MagicMock()
    mock_navigator.userAgent = "Mozilla/5.0 TestBrowser"
    mock_screen = MagicMock()
    mock_screen.width = 1920
    mock_screen.height = 1080
    mock_fp = MagicMock()
    mock_fp.navigator = mock_navigator
    mock_fp.screen = mock_screen
    mock_fp.headers = {"accept-language": "vi-VN"}
    mock_fp_generator.generate.return_value = mock_fp
    result = generate_session_fingerprint()

    assert result["user_agent"] == "Mozilla/5.0 TestBrowser"
    assert result["viewport"] == {"width": 1920, "height": 1080}
    assert result["locale"] == "vi-VN"
    assert result["timezone_id"] == "Asia/Ho_Chi_Minh"
    assert result["extra_http_headers"] == {"accept-language": "vi-VN"}


@pytest.mark.asyncio
@patch("tools.adaptive_crawler.helpers.redis.from_url")
async def test_check_redis_connection_success(mock_from_url: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.ping = AsyncMock(return_value=True)
    mock_client.aclose = AsyncMock()
    mock_from_url.return_value = mock_client
    await check_redis_connection("redis://localhost:6379/0")
    mock_client.ping.assert_awaited_once()
    mock_client.aclose.assert_awaited_once()


@pytest.mark.asyncio
@patch("tools.adaptive_crawler.helpers.redis.from_url")
async def test_check_redis_connection_failure(mock_from_url: MagicMock) -> None:
    mock_client = MagicMock()
    mock_client.ping = AsyncMock(side_effect=ConnectionError("Connection refused"))
    mock_client.aclose = AsyncMock()
    mock_from_url.return_value = mock_client
    with pytest.raises(RuntimeError) as exc_info:
        await check_redis_connection("redis://localhost:6379/0")

    assert "Cannot connect to Redis at redis://localhost:6379/0" in str(exc_info.value)
    mock_client.aclose.assert_awaited_once()


def test_custom_rendering_type_predictor_domain() -> None:
    predictor = CustomRenderingTypePredictor()
    assert predictor.domain("https://www.topdev.vn/jobs") == "topdev.vn"
    assert predictor.domain("http://itviec.com/it-jobs") == "itviec.com"
    assert predictor.domain("https://jobs.topdev.vn/list") == "jobs.topdev.vn"


def test_custom_rendering_type_predictor_predict_dynamic_domain() -> None:
    predictor = CustomRenderingTypePredictor()
    request_exact = Request.from_url("https://topdev.vn/jobs")
    request_subdomain = Request.from_url("https://api.topdev.vn/search")
    prediction_exact = predictor.predict(request_exact)
    prediction_subdomain = predictor.predict(request_subdomain)

    assert prediction_exact.rendering_type == "client only"
    assert prediction_exact.detection_probability_recommendation == 0.0
    assert prediction_subdomain.rendering_type == "client only"
    assert prediction_subdomain.detection_probability_recommendation == 0.0


def test_custom_rendering_type_predictor_predict_static_domain() -> None:
    predictor = CustomRenderingTypePredictor()
    request_static = Request.from_url("https://www.itviec.com/it-jobs")
    prediction = predictor.predict(request_static)

    assert prediction.rendering_type == "static"
    assert prediction.detection_probability_recommendation == 0.2


def test_custom_rendering_type_predictor_predict_unknown_domain() -> None:
    predictor = CustomRenderingTypePredictor()
    request_unknown = Request.from_url("https://unknown-domain.com/jobs")
    prediction = predictor.predict(request_unknown)

    assert prediction.rendering_type == "static"
    assert prediction.detection_probability_recommendation == 0.5


def test_custom_rendering_type_predictor_store_result_ignored_domains() -> None:
    predictor = CustomRenderingTypePredictor()
    request = Request.from_url("https://www.vietnamworks.com/jobs")
    predictor.store_result(request, "static")
    prediction = predictor.predict(request)

    assert prediction.rendering_type == "client only"


def test_custom_rendering_type_predictor_store_result_updates_cache() -> None:
    predictor = CustomRenderingTypePredictor()
    request = Request.from_url("https://example.com/jobs")
    predictor.store_result(request, "client only")
    prediction_dynamic = predictor.predict(request)
    predictor.store_result(request, "static")
    prediction_static = predictor.predict(request)

    assert prediction_dynamic.rendering_type == "client only"
    assert prediction_dynamic.detection_probability_recommendation == 0.0
    assert prediction_static.rendering_type == "static"
    assert prediction_static.detection_probability_recommendation == 0.2
