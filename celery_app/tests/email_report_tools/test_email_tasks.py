from unittest.mock import MagicMock, patch

import pytest
from app.core.config import settings
from jinja2 import TemplateError
from tools.email_report_tool.tasks import on_task_postrun, on_task_prerun, thread_local


class MockSuccessTask:
    name = "mock_success_task"


class MockFailureTask:
    name = "mock_failure_task"


@pytest.fixture(autouse=True)
def cleanup_thread_local():
    if hasattr(thread_local, "start_time"):
        del thread_local.start_time

    yield
    if hasattr(thread_local, "start_time"):
        del thread_local.start_time


@pytest.fixture(autouse=True)
def configure_smtp_settings(monkeypatch):
    monkeypatch.setattr(settings.smtp, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(settings.smtp, "EMAILS_FROM_EMAIL", "sender@example.com")
    monkeypatch.setattr(settings, "FIRST_SUPERUSER", "admin@example.com")


@patch("tools.email_report_tool.tasks.send_email")
def test_on_task_postrun_full_flow_success(mock_send_email: MagicMock):
    success_task = MockSuccessTask()
    on_task_prerun(task=success_task)
    assert hasattr(thread_local, "start_time")
    on_task_postrun(
        sender=success_task,
        task_id="task-123",
        task=success_task,
        args=["arg1", 100],
        return_value={"success": True, "count": 5},
        state="SUCCESS",
    )
    assert mock_send_email.called
    call_kwargs = mock_send_email.call_args.kwargs
    assert call_kwargs["email_to"] == "admin@example.com"
    assert call_kwargs["subject"] == "Celery Task Report: mock_success_task - SUCCESS"
    assert "mock_success_task" in call_kwargs["html_content"]
    assert "task-123" in call_kwargs["html_content"]
    assert "SUCCESS" in call_kwargs["html_content"]
    assert "green" in call_kwargs["html_content"]
    assert "count" in call_kwargs["html_content"]
    assert not hasattr(thread_local, "start_time")


@patch("tools.email_report_tool.tasks.send_email")
def test_on_task_postrun_full_flow_failure(mock_send_email: MagicMock):
    failure_task = MockFailureTask()
    on_task_prerun(task=failure_task)
    assert hasattr(thread_local, "start_time")
    on_task_postrun(
        sender=failure_task,
        task_id="task-999",
        task=failure_task,
        args=[],
        return_value=RuntimeError("Database connection dropped"),
        state="FAILURE",
    )
    assert mock_send_email.called
    call_kwargs = mock_send_email.call_args.kwargs
    assert call_kwargs["email_to"] == "admin@example.com"
    assert call_kwargs["subject"] == "Celery Task Report: mock_failure_task - FAILURE"
    assert "mock_failure_task" in call_kwargs["html_content"]
    assert "task-999" in call_kwargs["html_content"]
    assert "FAILURE" in call_kwargs["html_content"]
    assert "red" in call_kwargs["html_content"]
    assert "Database connection dropped" in call_kwargs["html_content"]
    assert not hasattr(thread_local, "start_time")


@patch("tools.email_report_tool.tasks.send_email")
def test_on_task_postrun_smtp_disabled(mock_send_email: MagicMock, monkeypatch):
    monkeypatch.setattr(settings.smtp, "SMTP_HOST", None)
    task = MockSuccessTask()
    on_task_prerun(task=task)
    on_task_postrun(task=task, task_id="task-1", state="SUCCESS", return_value=True)
    assert not mock_send_email.called
    assert not hasattr(thread_local, "start_time")


@patch("tools.email_report_tool.tasks.send_email")
def test_on_task_postrun_without_start_time(mock_send_email: MagicMock):
    task = MockSuccessTask()
    assert not hasattr(thread_local, "start_time")
    on_task_postrun(task=task, task_id="task-2", state="SUCCESS", return_value=True)
    assert mock_send_email.called
    call_kwargs = mock_send_email.call_args.kwargs
    assert "Unknown" in call_kwargs["html_content"]


@patch("tools.email_report_tool.tasks.send_email")
@patch("tools.email_report_tool.tasks.Path.exists", return_value=False)
def test_on_task_postrun_template_not_found(
    mock_exists: MagicMock, mock_send_email: MagicMock
):
    task = MockSuccessTask()
    on_task_prerun(task=task)
    on_task_postrun(task=task, task_id="task-3", state="SUCCESS", return_value=True)

    assert not mock_send_email.called


@patch("tools.email_report_tool.tasks.send_email")
@patch(
    "tools.email_report_tool.tasks.Template.render",
    side_effect=TemplateError("Render error"),
)
def test_on_task_postrun_template_render_error(
    mock_render: MagicMock, mock_send_email: MagicMock
):
    task = MockSuccessTask()
    on_task_prerun(task=task)
    on_task_postrun(task=task, task_id="task-4", state="SUCCESS", return_value=True)

    assert not mock_send_email.called


@patch("tools.email_report_tool.tasks.send_email")
def test_on_task_postrun_no_recipient(mock_send_email: MagicMock, monkeypatch):
    monkeypatch.setattr(settings, "FIRST_SUPERUSER", "")
    monkeypatch.setattr(settings.smtp, "EMAILS_FROM_EMAIL", None)
    task = MockSuccessTask()
    on_task_prerun(task=task)
    on_task_postrun(task=task, task_id="task-5", state="SUCCESS", return_value=True)

    assert not mock_send_email.called


@patch("tools.email_report_tool.tasks.send_email")
def test_on_task_postrun_fallback_to_from_email(
    mock_send_email: MagicMock, monkeypatch
):
    monkeypatch.setattr(settings, "FIRST_SUPERUSER", "")
    monkeypatch.setattr(settings.smtp, "EMAILS_FROM_EMAIL", "fallback@example.com")
    task = MockSuccessTask()
    on_task_prerun(task=task)
    on_task_postrun(task=task, task_id="task-6", state="SUCCESS", return_value=True)

    assert mock_send_email.called
    assert mock_send_email.call_args.kwargs["email_to"] == "fallback@example.com"


@patch(
    "tools.email_report_tool.tasks.send_email",
    side_effect=ConnectionError("Connection refused"),
)
def test_on_task_postrun_send_email_exception(mock_send_email: MagicMock):
    task = MockSuccessTask()
    on_task_prerun(task=task)
    on_task_postrun(task=task, task_id="task-7", state="SUCCESS", return_value=True)
