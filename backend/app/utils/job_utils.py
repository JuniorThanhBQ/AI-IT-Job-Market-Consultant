from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException, status

from app.core.enums import SeniorityLevel, WorkingModel


def parse_seniority_levels(values: list[str] | None) -> list[SeniorityLevel] | None:
    if not values:
        return None
    parsed = []
    for val in values:
        for item in val.split(","):
            item_stripped = item.strip()
            if not item_stripped:
                continue
            matched = False
            for level in SeniorityLevel:
                if level.value.lower() == item_stripped.lower():
                    parsed.append(level)
                    matched = True
                    break
            if not matched:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid seniority level: '{item_stripped}'",
                )
    return parsed


def parse_working_models(values: list[str] | None) -> list[WorkingModel] | None:
    if not values:
        return None
    parsed = []
    for val in values:
        for item in val.split(","):
            item_stripped = item.strip()
            if not item_stripped:
                continue
            matched = False
            for model in WorkingModel:
                if model.value.lower() == item_stripped.lower():
                    parsed.append(model)
                    matched = True
                    break
            if not matched:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid working model: '{item_stripped}'",
                )
    return parsed


def resolve_enum_value(
    update_dict: dict[str, Any], key: str, fallback: Any | None
) -> str | None:
    if key in update_dict and update_dict[key] is not None:
        value = update_dict[key]
        return str(getattr(value, "value", value))
    if fallback:
        return str(getattr(fallback, "value", fallback))
    return None


def built_semantic_results(
    *,
    embedding_latency: float,
    retrieval_latency: float,
    rrf_latency: float,
    top_candidates: Sequence[tuple[Any, Any, float]],
) -> list[dict[str, Any]]:
    metrics: dict[str, Any] = {
        "embedding_latency": embedding_latency,
        "retrieval_latency": retrieval_latency,
        "rrf_latency": rrf_latency,
    }
    results: list[dict[str, Any]] = [metrics]
    for item in top_candidates:
        job = item[0]
        distance = item[2]
        results.append(
            {
                "job_id": job.id,
                "score": float(max(0.0, round(1.0 - float(distance), 4))),
                "distance": float(distance),
            }
        )
    return results
