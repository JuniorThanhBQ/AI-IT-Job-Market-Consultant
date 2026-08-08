import logging

from google.genai.errors import APIError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def genai_retry(max_attempts: int = 3):
    return retry(
        reraise=True,
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(APIError),
        before_sleep=lambda retry_state: logger.warning(
            f"GenAI SDK API call failed. Retrying in {retry_state.next_action.sleep if retry_state.next_action is not None else 0}s... "
            f"(Attempt {retry_state.attempt_number} of {max_attempts})"
        ),
    )
