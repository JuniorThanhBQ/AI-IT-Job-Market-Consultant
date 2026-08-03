from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, SessionDep
from app.modules.consultant.schemas import (
    AgentServicesRequest,
    AIChatbotRequest,
    ConsultantResponse,
)

from .services import ConsultantService

router = APIRouter(tags=["Consultant Agents Flow"])


def get_consultant_service(session: SessionDep) -> ConsultantService:
    return ConsultantService(session)


@router.post("/chatbot/process-intent", response_model=ConsultantResponse)
async def execute_chatbot_intent(
    request: AIChatbotRequest,
    current_user: CurrentUser,
    service: ConsultantService = Depends(get_consultant_service),
):
    """User-facing chatbot API (requires Bearer consultee authentication)."""
    result_data = await service.process_chatbot_intent(
        user_id=current_user.id,
        intent=request.intent,
        user_input=request.user_input,
    )

    return ConsultantResponse(
        status="success",
        intent_executed=request.intent,
        sequence=result_data["execution_order"],
        result=result_data.get("final_result", ""),
        tool_outputs=result_data.get("tool_outputs"),
    )


@router.post("/agents/process-intent", response_model=ConsultantResponse)
async def execute_agent_service_intent(
    request: AgentServicesRequest,
    current_user: CurrentUser,
    service: ConsultantService = Depends(get_consultant_service),
):
    """System purpose agent services API (requires Bearer consultee authentication)."""
    result_data = await service.process_agent_intent(
        user_id=current_user.id,
        intent=request.intent,
        action_type=request.action_type,
    )

    return ConsultantResponse(
        status="success",
        intent_executed=request.intent,
        sequence=result_data["execution_order"],
        result=result_data.get("final_result", ""),
        tool_outputs=result_data.get("tool_outputs"),
    )
