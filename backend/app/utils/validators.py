import re
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from email_validator import EmailNotValidError
from email_validator import validate_email as check_email
from pydantic import AfterValidator


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


def validate_xss(value: str) -> str:
    patterns = [
        r"<script[^>]*>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onmouseover\s*=",
        r"</?[a-z][\s\S]*>",
    ]
    for pattern in patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError("Input contains unsafe HTML or script tags.")
    return value


def validate_sql_injection(value: str) -> str:
    patterns = [
        r"['\"`;\-\-]",
        r"\bor\b.*\b\d+\s*=\s*\d+",
        r"\bunion\b.*\bselect\b",
        r"\bselect\b.*\bfrom\b",
        r"\binsert\b.*\binto\b",
        r"\bdelete\b.*\bfrom\b",
        r"\bdrop\b.*\btable\b",
    ]
    for pattern in patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError("Input contains unsafe SQL patterns.")
    return value


def validate_command_injection(value: str) -> str:
    patterns = [
        r"[|;&$`><!]",
        r"\$\(.*\)",
        r"`.*`",
        r"\b(eval|exec|system|sh|bash|cmd|powershell)\b",
    ]
    for pattern in patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError("Input contains unsafe system command patterns.")
    return value


def validate_email_address(value: str) -> str:
    try:
        check_email(value, check_deliverability=False)
    except EmailNotValidError as e:
        raise ValueError("Invalid email address format.") from e
    return value


SafeStr = Annotated[
    str,
    AfterValidator(validate_xss),
    AfterValidator(validate_sql_injection),
    AfterValidator(validate_command_injection),
]


SafeEmailStr = Annotated[
    SafeStr,
    AfterValidator(validate_email_address),
]
