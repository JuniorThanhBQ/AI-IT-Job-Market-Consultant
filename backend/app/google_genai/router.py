from app.google_genai.models import GeminiModel


class ModelRouter:
    @staticmethod
    def route_task(task_type: str, has_large_context: bool = False) -> GeminiModel:
        if task_type == "embedding":
            return GeminiModel.GEMINI_EMBEDDING_001
        if has_large_context or task_type == "reasoning":
            return GeminiModel.GEMINI_2_5_PRO
        return GeminiModel.GEMINI_2_5_FLASH
