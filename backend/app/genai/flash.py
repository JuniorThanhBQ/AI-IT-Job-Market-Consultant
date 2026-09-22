from app.genai.base import BaseModelService
from app.genai.client import GenAIClientManager
from app.genai.models import GeminiModel


class FlashModelService(BaseModelService):
    def __init__(
        self, client_manager: GenAIClientManager, models: list[str] | None = None
    ):
        model_list = models or [
            GeminiModel.GEMINI_3_8_FLASH.value,
            GeminiModel.GEMINI_3_7_FLASH.value,
            GeminiModel.GEMINI_3_6_FLASH.value,
            GeminiModel.GEMINI_3_5_FLASH.value,
            GeminiModel.GEMINI_2_5_FLASH.value,
        ]
        super().__init__(
            client_manager=client_manager,
            model=model_list,
            model_name_log="Flash",
        )
