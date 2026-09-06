import json
import uuid
from collections.abc import AsyncGenerator

from sqlmodel import Session

from app.core.enums import ConsultantMode
from app.modules.consultant import repository as consultant_repo
from app.modules.consultant.exceptions import InvalidConsultantInputError
from app.modules.consultant.models import ConsultantHistory


def get_user_chat_history(
    *, session: Session, user_id: uuid.UUID
) -> list[ConsultantHistory]:
    return consultant_repo.get_history_by_user_id(session=session, user_id=user_id)


def clear_user_chat_history(*, session: Session, user_id: uuid.UUID) -> int:
    return consultant_repo.clear_history_by_user_id(session=session, user_id=user_id)


async def stream_mock_agent(
    *,
    session: Session,
    user_id: uuid.UUID,
    intent: ConsultantMode,
    user_input: str,
) -> AsyncGenerator[str]:
    if not user_input or not user_input.strip():
        raise InvalidConsultantInputError("User query cannot be empty.")

    mock_chunks = [
        "This is a temporary mock response from the consultant agent.\n\n",
        f"Received query: '{user_input}'.\n",
        f"Target intent: '{intent.value}'.\n",
        "The AI agent orchestration engine is currently undergoing system refactoring.",
    ]
    full_text = "".join(mock_chunks)

    for chunk in mock_chunks:
        yield json.dumps({"type": "chunk", "text": chunk}) + "\n"

    consultant_repo.create_history(
        session=session,
        user_id=user_id,
        user_input=user_input,
        output=full_text,
        consultant_mode=intent,
        request_log=f"User query: {user_input}\nIntent: {intent.value}",
        response_log=f"Mock Agent Output:\n{full_text}",
        input_embedding=None,
        token_used=0.0,
        latency=0.0,
    )

    yield (
        json.dumps(
            {
                "type": "metadata",
                "intent": intent.value,
                "execution_order": ["mock_agent"],
                "tool_outputs": {},
                "final_result": full_text,
            }
        )
        + "\n"
    )
