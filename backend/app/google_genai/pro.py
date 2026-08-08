from app.google_genai.base import BaseModelService
from app.google_genai.client import GenAIClientManager
from app.google_genai.models import GeminiModel


class ProModelService(BaseModelService):
    def __init__(self, client_manager: GenAIClientManager):
        super().__init__(
            client_manager=client_manager,
            model=GeminiModel.GEMINI_2_5_PRO.value,
            model_name_log="Pro",
        )
