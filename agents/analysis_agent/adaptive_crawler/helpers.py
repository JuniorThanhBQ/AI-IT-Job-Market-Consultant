from typing import Dict, Literal
from urllib.parse import urlparse
from crawlee import Request
from crawlee.crawlers import RenderingTypePredictor, RenderingTypePrediction


class CustomRenderingTypePredictor(RenderingTypePredictor):
    def __init__(self) -> None:
        super().__init__()
        self._cache: Dict[str, bool] = {
            "topdev.vn": True,
            "itviec.com": False,
            "itjobs.com.vn": True,
            "vieclam.ou.edu.vn": False,
            "fptjobs.com": True,
        }

    def _domain(self, url: str) -> str:
        return urlparse(url).netloc.removeprefix("www.")

    def predict(self, request: Request) -> RenderingTypePrediction:
        domain = self._domain(request.url)
        for known_domain, is_dynamic in self._cache.items():
            if domain == known_domain or domain.endswith("." + known_domain):
                return RenderingTypePrediction(
                    rendering_type="client only" if is_dynamic else "static",
                    detection_probability_recommendation=0.0,
                )
        return RenderingTypePrediction(
            rendering_type="static",
            detection_probability_recommendation=0.0,
        )

    def store_result(
        self, request: Request, rendering_type: Literal["static", "client only"]
    ) -> None:
        domain = self._domain(request.url)
        self._cache[domain] = rendering_type == "client only"
