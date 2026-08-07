import logging
import threading
from datetime import datetime
from pathlib import Path
from celery.signals import task_prerun, task_postrun
from jinja2 import Template

from app.core.config import settings
from app.utils.utils import send_email

logger = logging.getLogger(__name__)
_local = threading.local()


@task_prerun.connect
def on_task_prerun(sender=None, task_id=None, task=None, **kwargs):
    _local.start_time = datetime.now()


@task_postrun.connect
def on_task_postrun(
    sender=None,
    task_id=None,
    task=None,
    args=None,
    kwargs=None,
    retval=None,
    state=None,
    **cb_kwargs,
):
    end_time = datetime.now()
    start_time = getattr(_local, "start_time", None)

    if hasattr(_local, "start_time"):
        del _local.start_time

    if not settings.smtp.emails_enabled:
        return

    duration_str = "Unknown"
    time_start_str = "Unknown"
    if start_time:
        duration_str = f"{(end_time - start_time).total_seconds():.3f} seconds"
        time_start_str = start_time.strftime("%d-%m-%Y %H:%M:%S")

    time_end_str = end_time.strftime("%d-%m-%Y %H:%M:%S")

    task_name = task.name if task else str(sender)
    subject = f"Celery Task Report: {task_name} - {state}"

    template_path = Path(__file__).parent / "email_templates.html"
    if not template_path.exists():
        logger.error("Email template email_templates.html not found.")
        return

    try:
        template_content = template_path.read_text(encoding="utf-8")
        template = Template(template_content)
        html_content = template.render(
            task_name=task_name,
            task_id=task_id,
            status_color="green" if state == "SUCCESS" else "red",
            state=state,
            args=args,
            error_info=str(retval) if state == "FAILURE" else None,
            time_start=time_start_str,
            time_end=time_end_str,
            run_duration=duration_str,
        )
    except Exception as te:
        logger.error(f"Failed to render HTML email template: {te}")
        return

    recipient = settings.FIRST_SUPERUSER or settings.smtp.EMAILS_FROM_EMAIL
    if recipient:
        try:
            send_email(
                email_to=recipient,
                subject=subject,
                html_content=html_content,
            )
        except Exception as e:
            logger.error(f"Failed to send task email report: {e}")
