from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import CurrentUser, SessionDep
from app.modules.consultant.schemas import (
    AgentServicesRequest,
    AIChatbotRequest,
    ConsultantHistoryItem,
    ConsultantResponse,
)

from .services import ConsultantService

router = APIRouter()


def get_consultant_service(session: SessionDep) -> ConsultantService:
    return ConsultantService(session)


@router.get("/history", response_model=list[ConsultantHistoryItem])
def get_user_history_endpoint(
    current_user: CurrentUser,
    service: ConsultantService = Depends(get_consultant_service),
):
    return service.get_history(user_id=current_user.id)


@router.delete("/history")
def clear_user_history_endpoint(
    current_user: CurrentUser,
    service: ConsultantService = Depends(get_consultant_service),
):
    cleared_count = service.clear_history(user_id=current_user.id)
    return {"status": "success", "cleared_count": cleared_count}


@router.post("/chatbot/process-intent")
async def execute_chatbot_intent(
    request: AIChatbotRequest,
    current_user: CurrentUser,
    service: ConsultantService = Depends(get_consultant_service),
):
    generator = service.stream_chatbot_intent(
        user_id=current_user.id,
        intent=request.intent,
        user_input=request.user_input,
    )
    return StreamingResponse(generator, media_type="application/x-ndjson")


@router.post("/agents/process-intent", response_model=ConsultantResponse)
async def execute_agent_service_intent(
    request: AgentServicesRequest,
    current_user: CurrentUser,
    service: ConsultantService = Depends(get_consultant_service),
):
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
