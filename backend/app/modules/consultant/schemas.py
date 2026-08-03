from typing import Any

from pydantic import BaseModel

from app.core.enums import ActionType, ConsultantMode


class AIChatbotRequest(BaseModel):
    intent: ConsultantMode
    user_input: str


class AgentServicesRequest(BaseModel):
    intent: ConsultantMode
    action_type: ActionType


class ConsultantResponse(BaseModel):
    status: str
    intent_executed: ConsultantMode
    sequence: list[str]
    result: str
    tool_outputs: dict[str, Any] | None = None
