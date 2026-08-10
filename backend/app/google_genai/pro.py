from app.google_genai.base import BaseModelService
from app.google_genai.client import GenAIClientManager
from app.google_genai.models import GeminiModel


class ProModelService(BaseModelService):
    def __init__(
        self, client_manager: GenAIClientManager, models: list[str] | None = None
    ):
        model_list = models or [
            GeminiModel.GEMINI_2_5_PRO.value,
            GeminiModel.GEMINI_3_PRO_PREVIEW.value,
            GeminiModel.GEMINI_3_1_PRO_PREVIEW.value,
        ]
        super().__init__(
            client_manager=client_manager,
            model=model_list,
            model_name_log="Pro",
        )
