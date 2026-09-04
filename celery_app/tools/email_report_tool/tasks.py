import logging
import threading
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import settings
from app.utils.utils import send_email
from celery.signals import task_postrun, task_prerun
from jinja2 import Template, TemplateError
from utils.email_report_utils import build_email_report_info

logger = logging.getLogger(__name__)
thread_local = threading.local()


@task_prerun.connect
def on_task_prerun(sender=None, task_id=None, task=None, **kwargs):
    thread_local.start_time = datetime.now(UTC)


@task_postrun.connect
def on_task_postrun(
    sender=None,
    task_id=None,
    task=None,
    args=None,
    kwargs=None,
    retval=None,
    state=None,
    return_value=None,
    **cb_kwargs,
):
    end_time = datetime.now(UTC)
    start_time = getattr(thread_local, "start_time", None)
    if hasattr(thread_local, "start_time"):
        del thread_local.start_time

    if not settings.smtp.emails_enabled:
        return

    actual_return_value = retval if return_value is None else return_value
    report_info = build_email_report_info(
        sender=sender,
        task=task,
        start_time=start_time,
        end_time=end_time,
        state=state,
        return_value=actual_return_value,
    )

    template_path = Path(__file__).parent / "email_templates.html"
    if not template_path.exists():
        logger.error("Email template email_templates.html not found.")
        return

    try:
        template_content = template_path.read_text(encoding="utf-8")
        template = Template(template_content)
        html_content = template.render(
            task_name=report_info["task_name"],
            task_id=task_id,
            status_color=report_info["status_color"],
            state=report_info["effective_state"],
            args=args,
            result_info=report_info["result_info"],
            error_info=report_info["error_info"],
            time_start=report_info["time_start_str"],
            time_end=report_info["time_end_str"],
            run_duration=report_info["duration_str"],
        )
    except (TemplateError, TypeError, ValueError) as te:
        logger.error(f"Failed to render HTML email template: {te}")
        return

    recipient = settings.FIRST_SUPERUSER or settings.smtp.EMAILS_FROM_EMAIL
    if recipient:
        try:
            send_email(
                email_to=recipient,
                subject=report_info["subject"],
                html_content=html_content,
            )
        except (OSError, ConnectionError, RuntimeError, ValueError) as err:
            logger.error(f"Failed to send task email report: {err}")
