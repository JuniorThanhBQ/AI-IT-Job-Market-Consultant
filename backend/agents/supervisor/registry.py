from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base import BaseAgent

logger = logging.getLogger(__name__)

_AGENT_REGISTRY: dict[str, BaseAgent] = {}


def register_agent(agent: BaseAgent) -> BaseAgent:
    if agent.name in _AGENT_REGISTRY:
        logger.warning("Agent '%s' is already registered — overwriting.", agent.name)
    _AGENT_REGISTRY[agent.name] = agent
    logger.debug("Registered agent: %s", agent.name)
    return agent


def get_agent(name: str) -> BaseAgent:
    try:
        return _AGENT_REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"Agent '{name}' not found. "
            f"Registered agents: {list(_AGENT_REGISTRY.keys())}"
        ) from None


def list_agents() -> list[str]:
    return list(_AGENT_REGISTRY.keys())
