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
