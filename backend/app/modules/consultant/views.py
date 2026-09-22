from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, SessionDep
from app.modules.consultant.exceptions import (
    ConsultantError,
    InvalidConsultantInputError,
)
from app.modules.consultant.schemas import (
    AIAgentResponse,
    AIChatbotRequest,
    ConsultantHistoryClearResponse,
    ConsultantHistoryItem,
)
from app.modules.consultant.services import (
    clear_user_chat_history,
    execute_agent_service,
    get_user_chat_history,
)

router = APIRouter()


@router.get(
    "/agent-history/",
    response_model=list[ConsultantHistoryItem],
    status_code=status.HTTP_200_OK,
)
def get_user_chat_history_view(
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    try:
        return get_user_chat_history(session=session, user_id=current_user.id)
    except ConsultantError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.delete(
    "/agent-history/",
    response_model=ConsultantHistoryClearResponse,
    status_code=status.HTTP_200_OK,
)
def clear_user_chat_history_view(
    current_user: CurrentUser,
    session: SessionDep,
) -> ConsultantHistoryClearResponse:
    try:
        cleared_count = clear_user_chat_history(
            session=session,
            user_id=current_user.id,
        )
        return ConsultantHistoryClearResponse(
            status="success",
            cleared_count=cleared_count,
        )
    except ConsultantError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.post(
    "/agent/",
    response_model=AIAgentResponse,
    status_code=status.HTTP_200_OK,
)
async def execute_agent(
    request: AIChatbotRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> AIAgentResponse:
    try:
        return await execute_agent_service(
            session=session,
            user_id=current_user.id,
            intent=request.intent,
            user_input=request.user_input,
        )
    except InvalidConsultantInputError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except ConsultantError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        ) from err
