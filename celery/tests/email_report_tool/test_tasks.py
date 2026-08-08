import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from tools.email_report_tool.tasks import on_task_prerun, on_task_postrun, _local


class TestTaskPrerun:
    @patch("tools.email_report_tool.tasks.datetime")
    def test_on_task_prerun_sets_start_time(self, mock_datetime):
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        on_task_prerun(sender="test_sender", task_id="123")

        assert hasattr(_local, "start_time")
        assert _local.start_time == mock_now
        delattr(_local, "start_time")


class TestTaskPostrunConfigAndTemplate:
    @patch("tools.email_report_tool.tasks.settings")
    def test_emails_disabled(self, mock_settings):
        mock_settings.smtp.emails_enabled = False

        with patch("tools.email_report_tool.tasks.Path.exists") as mock_exists:
            on_task_postrun(state="SUCCESS")
            mock_exists.assert_not_called()

    @patch("tools.email_report_tool.tasks.settings")
    @patch("tools.email_report_tool.tasks.Path.exists", return_value=False)
    @patch("tools.email_report_tool.tasks.logger.error")
    def test_template_not_found(self, mock_logger, mock_exists, mock_settings):
        mock_settings.smtp.emails_enabled = True

        on_task_postrun(state="SUCCESS")

        mock_logger.assert_called_once_with(
            "Email template email_templates.html not found."
        )

    @patch("tools.email_report_tool.tasks.settings")
    @patch("tools.email_report_tool.tasks.Path.exists", return_value=True)
    @patch(
        "tools.email_report_tool.tasks.Path.read_text",
        return_value="Invalid {{ template",
    )
    @patch("tools.email_report_tool.tasks.Template")
    @patch("tools.email_report_tool.tasks.logger.error")
    def test_template_render_exception(
        self, mock_logger, mock_template, mock_read, mock_exists, mock_settings
    ):
        mock_settings.smtp.emails_enabled = True
        mock_template_instance = MagicMock()
        mock_template_instance.render.side_effect = Exception("Render error")
        mock_template.return_value = mock_template_instance

        on_task_postrun(state="SUCCESS")

        mock_logger.assert_called_once()
        assert "Failed to render HTML email template" in mock_logger.call_args[0][0]


class TestTaskPostrunTimeCalculation:
    @patch("tools.email_report_tool.tasks.settings")
    @patch("tools.email_report_tool.tasks.Path.exists", return_value=True)
    @patch(
        "tools.email_report_tool.tasks.Path.read_text",
        return_value="<html></html>",
    )
    @patch("tools.email_report_tool.tasks.Template")
    @patch("tools.email_report_tool.tasks.send_email")
    @patch("tools.email_report_tool.tasks.datetime")
    def test_duration_calculated_correctly(
        self,
        mock_datetime,
        mock_send,
        mock_template,
        mock_read,
        mock_exists,
        mock_settings,
    ):
        mock_settings.smtp.emails_enabled = True
        mock_settings.FIRST_SUPERUSER = "admin@test.com"

        start_time = datetime(2023, 1, 1, 12, 0, 0)
        end_time = datetime(2023, 1, 1, 12, 0, 5)
        mock_datetime.now.return_value = end_time
        _local.start_time = start_time

        mock_template_instance = MagicMock()
        mock_template.return_value = mock_template_instance

        on_task_postrun(state="SUCCESS", retval=True)

        assert not hasattr(_local, "start_time")
        render_kwargs = mock_template_instance.render.call_args[1]
        assert render_kwargs["run_duration"] == "5.000 seconds"
        assert render_kwargs["time_start"] == "01-01-2023 12:00:00"
        assert render_kwargs["time_end"] == "01-01-2023 12:00:05"

    @patch("tools.email_report_tool.tasks.settings")
    @patch("tools.email_report_tool.tasks.Path.exists", return_value=True)
    @patch(
        "tools.email_report_tool.tasks.Path.read_text",
        return_value="<html></html>",
    )
    @patch("tools.email_report_tool.tasks.Template")
    @patch("tools.email_report_tool.tasks.send_email")
    def test_duration_without_start_time(
        self, mock_send, mock_template, mock_read, mock_exists, mock_settings
    ):
        mock_settings.smtp.emails_enabled = True
        mock_settings.FIRST_SUPERUSER = "admin@test.com"

        if hasattr(_local, "start_time"):
            delattr(_local, "start_time")

        mock_template_instance = MagicMock()
        mock_template.return_value = mock_template_instance

        on_task_postrun(state="SUCCESS", retval=True)

        render_kwargs = mock_template_instance.render.call_args[1]
        assert render_kwargs["run_duration"] == "Unknown"
        assert render_kwargs["time_start"] == "Unknown"


class TestTaskPostrunFailureLogic:
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.patch_settings = patch("tools.email_report_tool.tasks.settings")
        self.mock_settings = self.patch_settings.start()
        self.mock_settings.smtp.emails_enabled = True
        self.mock_settings.FIRST_SUPERUSER = "admin@test.com"

        self.patch_exists = patch(
            "tools.email_report_tool.tasks.Path.exists", return_value=True
        )
        self.patch_exists.start()

        self.patch_read = patch(
            "tools.email_report_tool.tasks.Path.read_text", return_value="html"
        )
        self.patch_read.start()

        self.patch_template = patch("tools.email_report_tool.tasks.Template")
        self.mock_template = self.patch_template.start()
        self.mock_template_instance = MagicMock()
        self.mock_template.return_value = self.mock_template_instance

        self.patch_send = patch("tools.email_report_tool.tasks.send_email")
        self.patch_send.start()

        yield

        self.patch_settings.stop()
        self.patch_exists.stop()
        self.patch_read.stop()
        self.patch_template.stop()
        self.patch_send.stop()

    def test_state_failure(self):
        on_task_postrun(state="FAILURE", retval="Crash")
        render_kwargs = self.mock_template_instance.render.call_args[1]
        assert render_kwargs["state"] == "FAILURE"
        assert render_kwargs["status_color"] == "red"
        assert render_kwargs["error_info"] == "Crash"

    def test_retval_false(self):
        on_task_postrun(state="SUCCESS", retval=False)
        render_kwargs = self.mock_template_instance.render.call_args[1]
        assert render_kwargs["state"] == "FAILURE"
        assert (
            render_kwargs["error_info"]
            == "Task returned False indicating operation failure or unverified health checks."
        )

    def test_retval_dict_success_false(self):
        on_task_postrun(state="SUCCESS", retval={"success": False, "msg": "failed"})
        render_kwargs = self.mock_template_instance.render.call_args[1]
        assert render_kwargs["state"] == "FAILURE"
        assert "failed" in render_kwargs["error_info"]

    def test_retval_dict_status_error_with_explicit_error_key(self):
        on_task_postrun(
            state="SUCCESS", retval={"status": "error", "error": "Disk full"}
        )
        render_kwargs = self.mock_template_instance.render.call_args[1]
        assert render_kwargs["state"] == "FAILURE"
        assert render_kwargs["error_info"] == "Disk full"

    def test_retval_success_dict(self):
        on_task_postrun(state="SUCCESS", retval={"success": True, "data": [1, 2]})
        render_kwargs = self.mock_template_instance.render.call_args[1]
        assert render_kwargs["state"] == "SUCCESS"
        assert render_kwargs["status_color"] == "green"
        assert render_kwargs["error_info"] is None
        assert "data" in render_kwargs["result_info"]

    def test_retval_success_string(self):
        on_task_postrun(state="SUCCESS", retval="OK")
        render_kwargs = self.mock_template_instance.render.call_args[1]
        assert render_kwargs["state"] == "SUCCESS"
        assert render_kwargs["result_info"] == "OK"


class TestTaskPostrunDelivery:
    @patch("tools.email_report_tool.tasks.settings")
    @patch("tools.email_report_tool.tasks.Path.exists", return_value=True)
    @patch(
        "tools.email_report_tool.tasks.Path.read_text",
        return_value="rendered_html",
    )
    @patch("tools.email_report_tool.tasks.Template")
    @patch("tools.email_report_tool.tasks.send_email")
    def test_delivery_success_first_superuser(
        self, mock_send, mock_template, mock_read, mock_exists, mock_settings
    ):
        mock_settings.smtp.emails_enabled = True
        mock_settings.FIRST_SUPERUSER = "admin@test.com"
        mock_settings.smtp.EMAILS_FROM_EMAIL = "fallback@test.com"

        mock_task = MagicMock()
        mock_task.name = "my_task"

        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "final_html"
        mock_template.return_value = mock_template_instance

        on_task_postrun(state="SUCCESS", retval=True, task=mock_task)

        mock_send.assert_called_once_with(
            email_to="admin@test.com",
            subject="Celery Task Report: my_task - SUCCESS",
            html_content="final_html",
        )

    @patch("tools.email_report_tool.tasks.settings")
    @patch("tools.email_report_tool.tasks.Path.exists", return_value=True)
    @patch(
        "tools.email_report_tool.tasks.Path.read_text",
        return_value="rendered_html",
    )
    @patch("tools.email_report_tool.tasks.Template")
    @patch("tools.email_report_tool.tasks.send_email")
    def test_delivery_fallback_to_from_email(
        self, mock_send, mock_template, mock_read, mock_exists, mock_settings
    ):
        mock_settings.smtp.emails_enabled = True
        mock_settings.FIRST_SUPERUSER = None
        mock_settings.smtp.EMAILS_FROM_EMAIL = "fallback@test.com"

        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "final_html"
        mock_template.return_value = mock_template_instance

        on_task_postrun(state="SUCCESS", sender="fallback_sender")

        mock_send.assert_called_once_with(
            email_to="fallback@test.com",
            subject="Celery Task Report: fallback_sender - SUCCESS",
            html_content="final_html",
        )

    @patch("tools.email_report_tool.tasks.settings")
    @patch("tools.email_report_tool.tasks.Path.exists", return_value=True)
    @patch(
        "tools.email_report_tool.tasks.Path.read_text",
        return_value="rendered_html",
    )
    @patch("tools.email_report_tool.tasks.Template")
    @patch("tools.email_report_tool.tasks.send_email")
    @patch("tools.email_report_tool.tasks.logger.error")
    def test_delivery_send_email_exception(
        self,
        mock_logger,
        mock_send,
        mock_template,
        mock_read,
        mock_exists,
        mock_settings,
    ):
        mock_settings.smtp.emails_enabled = True
        mock_settings.FIRST_SUPERUSER = "admin@test.com"

        mock_template_instance = MagicMock()
        mock_template_instance.render.return_value = "final_html"
        mock_template.return_value = mock_template_instance

        mock_send.side_effect = Exception("SMTP Error")

        on_task_postrun(state="SUCCESS")

        mock_logger.assert_called_once()
        assert "Failed to send task email report" in mock_logger.call_args[0][0]
