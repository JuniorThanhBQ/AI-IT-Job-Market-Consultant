import uuid

from agents.agent import MarketAnalysisAgent
from agents.memory.history import load_chat_context
from sqlmodel import Session

from app.core.enums import ConsultantMode
from app.modules.consultant import repository as consultant_repo
from app.modules.consultant.exceptions import InvalidConsultantInputError
from app.modules.consultant.models import ConsultantHistory
from app.modules.consultant.schemas import AIAgentResponse
from app.utils.embeddings import generate_embedding_async


def get_user_chat_history(
    *, session: Session, user_id: uuid.UUID
) -> list[ConsultantHistory]:
    return consultant_repo.get_history_by_user_id(session=session, user_id=user_id)


def clear_user_chat_history(*, session: Session, user_id: uuid.UUID) -> int:
    return consultant_repo.clear_history_by_user_id(session=session, user_id=user_id)


async def execute_agent_service(
    *,
    session: Session,
    user_id: uuid.UUID,
    intent: ConsultantMode,
    user_input: str,
) -> AIAgentResponse:
    if not user_input or not user_input.strip():
        raise InvalidConsultantInputError("User query cannot be empty.")

    input_embedding = await generate_embedding_async(user_input)
    chat_history = load_chat_context(session=session, user_id=user_id, max_turns=2)

    agent = MarketAnalysisAgent()
    result = await agent.run_agent(
        user_input=user_input,
        chat_history=chat_history,
    )

    final_result = result["final_result"]
    latency = result["latency"]
    iterations = result["iterations"]

    token_used = float(max(1, len(user_input) // 4) + max(1, len(final_result) // 4))

    consultant_repo.create_history(
        session=session,
        user_id=user_id,
        user_input=user_input,
        output=final_result,
        consultant_mode=intent,
        request_log=agent.build_request_log(user_input),
        response_log=agent.build_response_log(final_result),
        input_embedding=list(input_embedding),
        token_used=token_used,
        latency=latency,
    )

    return AIAgentResponse(
        final_result=final_result,
        latency=latency,
        iterations=iterations,
    )
