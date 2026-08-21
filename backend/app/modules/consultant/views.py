from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import CurrentUser, SessionDep
from app.modules.consultant.schemas import (
    AIChatbotRequest,
    ConsultantHistoryItem,
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


@router.post("/chatbot/intents")
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
