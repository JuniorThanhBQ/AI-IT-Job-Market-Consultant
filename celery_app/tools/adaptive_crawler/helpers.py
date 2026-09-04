from typing import Literal
from urllib.parse import urlparse

import redis.asyncio as redis
from crawlee import Request
from crawlee.crawlers import RenderingTypePrediction, RenderingTypePredictor
from crawlee.fingerprint_suite import (
    DefaultFingerprintGenerator,
    HeaderGeneratorOptions,
)

fingerprint_generator = DefaultFingerprintGenerator(
    header_options=HeaderGeneratorOptions(locales=["vi-VN", "en-US"])
)


def generate_session_fingerprint() -> dict:
    fp = fingerprint_generator.generate()

    return {
        "user_agent": fp.navigator.userAgent,
        "viewport": {
            "width": fp.screen.width,
            "height": fp.screen.height,
        },
        "locale": "vi-VN",
        "timezone_id": "Asia/Ho_Chi_Minh",
        "extra_http_headers": fp.headers,
    }


async def check_redis_connection(redis_url: str) -> None:
    client = redis.from_url(redis_url)
    try:
        await client.ping()
    except Exception as e:
        raise RuntimeError(f"Cannot connect to Redis at {redis_url}: {e}") from e
    finally:
        await client.aclose()


class CustomRenderingTypePredictor(RenderingTypePredictor):
    def __init__(self) -> None:
        super().__init__()
        self._cache: dict[str, bool] = {
            "topdev.vn": True,
            "itviec.com": False,
            "itjobs.com.vn": True,
            "vieclam.ou.edu.vn": False,
            "fptjobs.com": True,
            "vietnamworks.com": True,
        }

    def domain(self, url: str) -> str:
        return urlparse(url).netloc.removeprefix("www.")

    def predict(self, request: Request) -> RenderingTypePrediction:
        domain = self.domain(request.url)
        for knowndomain, is_dynamic in self._cache.items():
            if domain == knowndomain or domain.endswith("." + knowndomain):
                return RenderingTypePrediction(
                    rendering_type="client only" if is_dynamic else "static",
                    detection_probability_recommendation=0.0 if is_dynamic else 0.2,
                )
        return RenderingTypePrediction(
            rendering_type="static",
            detection_probability_recommendation=0.5,
        )

    def store_result(
        self, request: Request, rendering_type: Literal["static", "client only"]
    ) -> None:
        domain = self.domain(request.url)
        if domain in {"vietnamworks.com"}:
            return
        self._cache[domain] = rendering_type == "client only"
