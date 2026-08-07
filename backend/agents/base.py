import logging
import time
from abc import ABC, abstractmethod
from typing import Any

from agents.supervisor.state import AgentState

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    name: str = "unnamed_agent"

    @abstractmethod
    async def execute(self, state: AgentState) -> dict[str, Any]:
        """Core logic implemented by each concrete agent.

        Must return a dict of state updates (only the keys to change).
        """
        ...

    async def run(self, state: AgentState) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            result = await self.execute(state)
            elapsed = time.perf_counter() - start
            logger.info(
                "Agent [%s] completed in %.2fs",
                self.name,
                elapsed,
            )
            result.setdefault("execution_order", [self.name])
            return result
        except Exception:
            elapsed = time.perf_counter() - start
            logger.exception(
                "Agent [%s] failed after %.2fs",
                self.name,
                elapsed,
            )
            return {
                "execution_order": [self.name],
                "error": f"Agent '{self.name}' encountered an error.",
                "status": "partial",
            }
