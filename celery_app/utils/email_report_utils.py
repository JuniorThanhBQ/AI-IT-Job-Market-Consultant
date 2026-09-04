import json
from datetime import datetime
from typing import Any


def build_email_report_info(
    sender: Any = None,
    task: Any = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    state: str | None = None,
    return_value: Any = None,
) -> dict[str, Any]:
    duration_str = "Unknown"
    time_start_str = "Unknown"
    if start_time and end_time:
        duration_str = f"{(end_time - start_time).total_seconds():.3f} seconds"
        time_start_str = start_time.strftime("%d-%m-%Y %H:%M:%S")
    elif start_time:
        time_start_str = start_time.strftime("%d-%m-%Y %H:%M:%S")

    time_end_str = end_time.strftime("%d-%m-%Y %H:%M:%S") if end_time else "Unknown"
    task_name = task.name if task else str(sender)
    is_failure = (
        state == "FAILURE"
        or return_value is False
        or (
            isinstance(return_value, dict)
            and (
                return_value.get("success") is False
                or return_value.get("status") in {"failed", "error", "FAILURE"}
            )
        )
    )
    effective_state = "FAILURE" if is_failure else (state or "SUCCESS")
    status_color = "green" if effective_state == "SUCCESS" else "red"
    subject = f"Celery Task Report: {task_name} - {effective_state}"

    result_info = None
    error_info = None
    if is_failure:
        if state == "FAILURE":
            error_info = str(return_value)
        elif return_value is False:
            error_info = "Task returned False indicating operation failure or unverified health checks."
        elif isinstance(return_value, dict) and "error" in return_value:
            error_info = str(return_value.get("error"))
        else:
            error_info = json.dumps(return_value, indent=2, default=str)
    else:
        if return_value is not None:
            if isinstance(return_value, (dict, list)):
                try:
                    result_info = json.dumps(return_value, indent=2, default=str)
                except TypeError, ValueError:
                    result_info = str(return_value)
            else:
                result_info = str(return_value)

    return {
        "task_name": task_name,
        "time_start_str": time_start_str,
        "time_end_str": time_end_str,
        "duration_str": duration_str,
        "effective_state": effective_state,
        "status_color": status_color,
        "subject": subject,
        "result_info": result_info,
        "error_info": error_info,
    }
