from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ActionType, ConsultantMode
from app.utils.validators import SafeStr


class AIChatbotRequest(BaseModel):
    intent: ConsultantMode
    user_input: SafeStr


class AIAgentResponse(BaseModel):
    final_result: str
    latency: float
    iterations: int


class AgentServicesRequest(BaseModel):
    intent: ConsultantMode
    action_type: ActionType


class ConsultantResponse(BaseModel):
    status: str
    intent_executed: ConsultantMode
    sequence: list[str]
    result: str
    tool_outputs: dict[str, Any] | None = None


class ConsultantHistoryItem(BaseModel):
    id: int | None = None
    user_input: str
    output: str
    consultant_mode: ConsultantMode | None = None
    created_at: datetime | None = Field(default=None, alias="created_date")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ConsultantHistoryClearResponse(BaseModel):
    status: str
    cleared_count: int
