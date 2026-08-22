# ADR-08: Decision on Multi-Agent Simplification and Deprecation of Unused Subagents

## Status
Accepted

## Context
The system was originally designed with a three-agent LangGraph network: `MarketAnalysisAgent`, `PersonalizationAgent`, and `RecommendationAgent`. These agents were intended to analyze markets, personalize profiles, and recommend job postings sequentially.

In practice, the front-end user experience (chatbot and dashboards) only utilizes the `MARKET_ANALYSIS` intent. Running personalization and recommendation subagents introduced significant request latency, high token usage, and extra API orchestration code, while being completely unused by the active front-end features.

## Decision
1. **Agent Deprecation:** Completely delete the `personalization_agent` and `recommendation_agent` source folders from the `backend/agents/subagents/` directory. Remove their imports and registrations from `orchestrator.py`.
2. **Intent Pipeline Fallback Routing:** Update the `INTENT_PIPELINES` map inside `graph.py` to route all secondary intents (`PERSONAL_STANDARD_EVALUATION`, `JOB_RECOMMEND`, and `DEEP_ANALYSIS_EVALUATION`) to the active `market_analysis` agent.

## Rationale
1. **Reduced Code Complexity:** Deleting unused folders reduces codebase maintenance costs, decreases testing surface area, and keeps the project structure clean.
2. **Backward Compatibility:** Mapping the unused intents to the single active agent prevents backend runtime crashes if an API request (e.g. from historical chat database logs or client test suites) executes with legacy intent tags.

## Consequences
### Positive
* **Lower Maintenance Overhead:** Only one active agent is maintained, simplifying prompt updates and agent tests.
* **Higher API Performance:** Avoids serial LLM invocations, leading to faster response times and lower token consumption.
* **Crash Prevention:** Fallback intent routing protects legacy database entries and endpoints.

### Negative
* **Loss of Specialization:** Removing the personalization and recommendation components means that any future features requiring specialized persona evaluations or custom recommendations must re-implement these graphs from scratch.

## Decision Date
22/08/2026
