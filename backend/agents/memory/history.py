import uuid
from typing import Any, cast

from app.modules.consultant.models import ConsultantHistory
from sqlmodel import Session, select


def load_chat_context(
    session: Session,
    user_id: uuid.UUID,
    max_turns: int = 2,
) -> str:
    stmt = (
        select(ConsultantHistory)
        .where(ConsultantHistory.user_id == user_id)
        .where(ConsultantHistory.user_input != "")
        .where(ConsultantHistory.output != "")
        .order_by(cast(Any, ConsultantHistory.id).desc())
        .limit(max_turns)
    )
    records = list(session.exec(stmt).all())
    records.reverse()

    if not records:
        return "No previous conversation."

    parts: list[str] = []
    for record in records:
        parts.append(f"User: {record.user_input}")
        output_preview = (
            record.output[:500] if len(record.output) > 500 else record.output
        )
        parts.append(f"Assistant: {output_preview}")
    return "\n".join(parts)
