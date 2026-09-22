import json
import logging
from typing import Any

from agents.core.react_executor import execute_agent_async

logger = logging.getLogger(__name__)


class MarketAnalysisAgent:
    def __init__(self) -> None:
        self.total_latency: float = 0.0
        self.tool_calls: list[str] = []
        self.iterations: int = 0

    async def run_agent(
        self,
        user_input: str,
        chat_history: str,
    ) -> dict[str, Any]:
        res = await execute_agent_async(
            user_input=user_input,
            chat_history=chat_history,
        )
        self.tool_calls = res.get("tool_calls", [])
        self.iterations = res.get("iterations", 0)
        self.total_latency = res.get("latency", 0.0)
        return {
            "final_result": res.get("final_result", ""),
            "latency": self.total_latency,
            "iterations": self.iterations,
        }

    def build_request_log(self, user_input: str) -> str:
        return json.dumps(
            {
                "user_input": user_input,
                "tools_invoked": self.tool_calls,
                "iterations": self.iterations,
            },
            ensure_ascii=False,
        )

    def build_response_log(self, final_result: str) -> str:
        return json.dumps(
            {
                "final_answer": final_result,
                "tools_invoked": self.tool_calls,
                "iterations": self.iterations,
                "latency": round(self.total_latency, 3),
            },
            ensure_ascii=False,
        )
