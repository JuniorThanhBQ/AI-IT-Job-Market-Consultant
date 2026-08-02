import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


class GenAIMetricsTracker:
    @staticmethod
    def log_usage(
        model_name: str,
        operation: str,
        latency: float,
        prompt_tokens: int | None = None,
        candidates_tokens: int | None = None,
    ) -> None:
        p_tok = prompt_tokens if prompt_tokens is not None else "N/A"
        c_tok = candidates_tokens if candidates_tokens is not None else "N/A"
        total = (
            prompt_tokens + candidates_tokens
            if (prompt_tokens is not None and candidates_tokens is not None)
            else "N/A"
        )
        logger.info(
            f"[GenAI Metrics] Operation: {operation} | Model: {model_name} | "
            f"Latency: {latency:.4f}s | Tokens: [Prompt={p_tok}, Output={c_tok}, Total={total}]"
        )


def track_genai_metrics(operation_name: str):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            model_name = getattr(args[0], "model", "unknown") if args else "unknown"
            try:
                result = await func(*args, **kwargs)
                latency = time.perf_counter() - start_time
                GenAIMetricsTracker.log_usage(
                    model_name=model_name,
                    operation=operation_name,
                    latency=latency,
                )
                return result
            except Exception as e:
                latency = time.perf_counter() - start_time
                logger.error(
                    f"[GenAI Metrics] Failed operation: {operation_name} | "
                    f"Model: {model_name} | Latency: {latency:.4f}s | Error: {str(e)}"
                )
                raise

        return wrapper

    return decorator
