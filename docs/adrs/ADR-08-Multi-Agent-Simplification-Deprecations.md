# ADR-08: Decision on Multi-Agent Simplification and Deprecation of Unused Subagents

## Status
Accepted

## Context
The system was originally designed with a three-agent LangGraph network: `MarketAnalysisAgent`, `PersonalizationAgent`, and `RecommendationAgent`. These agents were intended to analyze markets, personalize profiles, and recommend job postings sequentially.

In practice, the front-end user experience only utilizes the `MARKET_ANALYSIS` intent. Running personalization and recommendation subagents can cause request latency, high token usage, and extra API orchestration code while being completely unused by the active front-end features.

## Decision
Temporarily halt multi-agent development. Focus on AI Agents for market analysis using the ReAct framework:

1. **Agent Deprecation:** Delete `personalization_agent` and `recommendation_agent` source folders from the `backend/agents/subagents/` directory. Remove their imports and registrations from `orchestrator.py`.
2. **Intent Pipeline Fallback Routing:** Update the `INTENT_PIPELINES` map inside `graph.py` to route all secondary intents (`PERSONAL_STANDARD_EVALUATION`, `JOB_RECOMMEND`, and `DEEP_ANALYSIS_EVALUATION`) to the active `market_analysis` agent.
3. **Focus on AI Agent market analysis:** The development of an AI agent for market analysis is prioritized until the entire system is operating stably.

## Rationale
1. **Reduced Code Complexity:** Deleting unused folders reduces codebase maintenance costs, decreases testing surface area, and keeps the project structure clean.
2. **Backward Compatibility:** Mapping the unused intents to the single active agent prevents backend runtime crashes if an API request executes with legacy intent tags.

## Consequences
### Positive
* **Lower Maintenance Overhead:** Only one active agent is maintained, simplifying prompt updates and agent tests.
* **Higher API Performance:** Avoids serial LLM invocations, leading to faster response times and lower token consumption.
* **Crash Prevention:** Fallback intent routing protects legacy database entries and endpoints.

### Negative
* **Loss of Specialization:** Removing the personalization and recommendation components means that any future features requiring specialized persona evaluations or custom recommendations must re-implement these graphs from scratch.

## Decision Date
22/08/2026
