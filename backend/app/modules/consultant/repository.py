import uuid
from typing import Any, cast

from sqlmodel import Session, or_, select

from app.core.enums import ConsultantMode
from app.modules.consultant.models import ConsultantHistory


def create_history(
    *,
    session: Session,
    user_id: uuid.UUID,
    user_input: str,
    output: str,
    consultant_mode: ConsultantMode,
    request_log: str,
    response_log: str,
    input_embedding: list[float] | None = None,
    token_used: float = 0.0,
    latency: float = 0.0,
) -> ConsultantHistory:
    history = ConsultantHistory(
        user_id=user_id,
        user_input=user_input,
        output=output,
        consultant_mode=consultant_mode,
        request_log=request_log,
        response_log=response_log,
        input_embedding=input_embedding,
        token_used=token_used,
        latency=latency,
    )
    session.add(history)
    session.commit()
    session.refresh(history)
    return history


def get_history_by_user_id(
    *, session: Session, user_id: uuid.UUID
) -> list[ConsultantHistory]:
    stmt = (
        select(ConsultantHistory)
        .where(ConsultantHistory.user_id == user_id)
        .where(ConsultantHistory.user_input != "")
        .where(ConsultantHistory.output != "")
        .order_by(cast(Any, ConsultantHistory.id))
    )
    return list(session.exec(stmt).all())


def clear_history_by_user_id(*, session: Session, user_id: uuid.UUID) -> int:
    stmt = (
        select(ConsultantHistory)
        .where(ConsultantHistory.user_id == user_id)
        .where(
            or_(
                ConsultantHistory.user_input != "",
                ConsultantHistory.output != "",
            )
        )
    )
    histories = list(session.exec(stmt).all())
    for h in histories:
        h.user_input = ""
        h.output = ""
        session.add(h)
    session.commit()
    return len(histories)
