import html
import logging
import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import emails
import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings
from app.core.enums import SeniorityLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    if not settings.smtp.emails_enabled:
        raise ValueError("no provided configuration for email variables")
    if not settings.smtp.EMAILS_FROM_EMAIL:
        raise ValueError("emails_from_email is not configured")
    message = emails.message.Message(
        subject=subject,
        html=html_content,
        mail_from=(settings.smtp.EMAILS_FROM_NAME, settings.smtp.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.smtp.SMTP_HOST, "port": settings.smtp.SMTP_PORT}
    if settings.smtp.SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.smtp.SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.smtp.SMTP_USER:
        smtp_options["user"] = settings.smtp.SMTP_USER
    if settings.smtp.SMTP_PASSWORD:
        smtp_options["password"] = settings.smtp.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None


def name_validator(value: str) -> str:
    pattern = r"^[A-Za-zÀ-ỹ]{2,}( [A-Za-zÀ-ỹ]{2,})*$"
    if not re.match(pattern, value):
        raise ValueError(
            "Name must contain only alphabetical characters (including accents) "
            "and each word/name part must be at least 2 characters long."
        )
    return value


def validate_birthday(v: date) -> date:
    today = date.today()
    age = today.year - v.year
    if (today.month, today.day) < (v.month, v.day):
        age -= 1
    if age < 15:
        raise ValueError("Consultee must be at least 15 years old.")
    return v


def validate_timestamps(created_date: datetime, updated_date: datetime) -> None:
    now = datetime.now(UTC)
    future_limit = now + timedelta(minutes=10)

    if created_date > future_limit:
        raise ValueError("created_date cannot be in the future")

    if updated_date > future_limit:
        raise ValueError("updated_date cannot be in the future")

    if updated_date < created_date:
        raise ValueError("updated_date cannot be earlier than created_date")


def validate_date_range(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise ValueError("end_date cannot be earlier than start_date")


def validate_salary_range(min_salary: float, max_salary: float) -> None:
    if min_salary < 0:
        raise ValueError("min_salary cannot be negative")
    if max_salary < 0:
        raise ValueError("max_salary cannot be negative")
    if min_salary > max_salary:
        raise ValueError("min_salary cannot be greater than max_salary")


def clean_field(val: str | None) -> str:
    val = val or ""
    val = html.unescape(val)
    normalized = unicodedata.normalize("NFKC", val or "")
    return re.sub(r"\s+", " ", normalized).lower().strip()


def parse_seniority_level(title: str, raw_seniority: str = "") -> SeniorityLevel:
    combined = f"{title} {raw_seniority}".lower()
    if re.search(r"\bintern(ship)?s?\b", combined) or re.search(
        r"\bthực tập( sinh)?\b", combined
    ):
        return SeniorityLevel.INTERN
    elif re.search(r"\bfreshers?\b", combined):
        return SeniorityLevel.FRESHER
    elif re.search(r"\bjuniors?\b", combined):
        return SeniorityLevel.JUNIOR
    elif re.search(r"\bseniors?\b", combined):
        return SeniorityLevel.SENIOR
    elif re.search(r"\blead(er)?s?\b", combined):
        return SeniorityLevel.LEAD
    elif re.search(r"\bmanagers?\b", combined) or re.search(r"\bquản lý\b", combined):
        return SeniorityLevel.MANAGER
    elif re.search(r"\bdirectors?\b", combined) or re.search(r"\bgiám đốc\b", combined):
        return SeniorityLevel.DIRECTOR
    elif re.search(r"\bexecutives?\b", combined):
        return SeniorityLevel.EXECUTIVE
    return SeniorityLevel.MID


def clean_json_string(s: str) -> str:
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()
