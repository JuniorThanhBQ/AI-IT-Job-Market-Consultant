from agents.supervisor.orchestrator import Intent
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import SessionDep

from .services import ConsultantService

router = APIRouter(prefix="/consultant", tags=["Consultant Agents Flow"])


class ConsultantRequest(BaseModel):
    intent: Intent
    user_input: str


def get_consultant_service(session: SessionDep) -> ConsultantService:
    return ConsultantService(session)


@router.post("/process-intent")
async def execute_intent_flow(
    request: ConsultantRequest,
    service: ConsultantService = Depends(get_consultant_service),
):
    result_data = await service.process_intent_flow(request.intent, request.user_input)

    return {
        "status": "success",
        "intent_executed": request.intent,
        "sequence": result_data["execution_order"],
        "result": result_data.get("final_result", ""),
    }
