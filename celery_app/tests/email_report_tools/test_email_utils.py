import json
from datetime import UTC, datetime

from utils.email_report_utils import build_email_report_info


class MockTask:
    name = "custom_mock_task"


class NonSerializableObject:
    def __str__(self):
        return "custom_repr"


def test_build_info_with_start_and_end_time():
    start_time = datetime(2026, 9, 4, 10, 0, 0, tzinfo=UTC)
    end_time = datetime(2026, 9, 4, 10, 0, 10, tzinfo=UTC)
    task = MockTask()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=start_time,
        end_time=end_time,
        state="SUCCESS",
        return_value={"status": "complete"},
    )
    assert info["task_name"] == "custom_mock_task"
    assert info["time_start_str"] == "04-09-2026 10:00:00"
    assert info["time_end_str"] == "04-09-2026 10:00:10"
    assert "10.000 seconds" in info["duration_str"]
    assert info["effective_state"] == "SUCCESS"
    assert info["status_color"] == "green"
    assert info["subject"] == "Celery Task Report: custom_mock_task - SUCCESS"
    assert "complete" in info["result_info"]
    assert info["error_info"] is None


def test_build_info_with_only_start_time():
    start_time = datetime(2026, 9, 4, 10, 0, 0, tzinfo=UTC)
    task = MockTask()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=start_time,
        end_time=None,
        state="SUCCESS",
        return_value=None,
    )
    assert info["time_start_str"] == "04-09-2026 10:00:00"
    assert info["time_end_str"] == "Unknown"
    assert info["duration_str"] == "Unknown"


def test_build_info_with_sender_only():
    info = build_email_report_info(
        sender="sender_module.task_name",
        task=None,
        start_time=None,
        end_time=None,
        state="SUCCESS",
        return_value=None,
    )
    assert info["task_name"] == "sender_module.task_name"
    assert info["time_start_str"] == "Unknown"
    assert info["time_end_str"] == "Unknown"
    assert info["duration_str"] == "Unknown"


def test_build_info_state_failure():
    task = MockTask()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=None,
        end_time=None,
        state="FAILURE",
        return_value="Crash error message",
    )
    assert info["effective_state"] == "FAILURE"
    assert info["status_color"] == "red"
    assert info["error_info"] == "Crash error message"
    assert info["result_info"] is None


def test_build_info_return_value_false():
    task = MockTask()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=None,
        end_time=None,
        state="SUCCESS",
        return_value=False,
    )
    assert info["effective_state"] == "FAILURE"
    assert info["status_color"] == "red"
    assert "Task returned False" in info["error_info"]


def test_build_info_return_value_dict_failed():
    task = MockTask()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=None,
        end_time=None,
        state="SUCCESS",
        return_value={"success": False, "reason": "timeout"},
    )
    assert info["effective_state"] == "FAILURE"
    assert info["status_color"] == "red"
    assert "timeout" in info["error_info"]


def test_build_info_return_value_dict_with_error_key():
    task = MockTask()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=None,
        end_time=None,
        state="SUCCESS",
        return_value={"status": "error", "error": "Disk full"},
    )
    assert info["effective_state"] == "FAILURE"
    assert info["status_color"] == "red"
    assert info["error_info"] == "Disk full"


def test_build_info_return_value_dict_without_error_key():
    task = MockTask()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=None,
        end_time=None,
        state="SUCCESS",
        return_value={"success": False, "code": 500},
    )
    assert info["effective_state"] == "FAILURE"
    assert info["status_color"] == "red"
    assert "500" in info["error_info"]


def test_build_info_return_value_list():
    task = MockTask()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=None,
        end_time=None,
        state="SUCCESS",
        return_value=[1, 2, 3],
    )
    assert info["effective_state"] == "SUCCESS"
    assert "[1, 2, 3]" in info["result_info"] or "1" in info["result_info"]


def test_build_info_return_value_string():
    task = MockTask()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=None,
        end_time=None,
        state="SUCCESS",
        return_value="Simple success string",
    )
    assert info["effective_state"] == "SUCCESS"
    assert info["result_info"] == "Simple success string"


def test_build_info_return_value_non_serializable():
    task = MockTask()
    obj = NonSerializableObject()
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=None,
        end_time=None,
        state="SUCCESS",
        return_value=[obj],
    )
    assert info["effective_state"] == "SUCCESS"
    assert "custom_repr" in info["result_info"]


def test_build_info_json_dumps_exception(monkeypatch):
    task = MockTask()

    def mock_dumps(*args, **kwargs):
        raise TypeError("Forced serialization error")

    monkeypatch.setattr(json, "dumps", mock_dumps)
    info = build_email_report_info(
        sender=task,
        task=task,
        start_time=None,
        end_time=None,
        state="SUCCESS",
        return_value={"sample": "data"},
    )
    assert info["effective_state"] == "SUCCESS"
    assert "sample" in info["result_info"]
