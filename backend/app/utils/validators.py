import math
import re
import shlex
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from email_validator import EmailNotValidError
from email_validator import validate_email as check_email
from pydantic import AfterValidator


def name_validator(value: str) -> str:
    pattern = r"^[A-Za-zÀ-ỹ]{2,}( [A-Za-zÀ-ỹ]{2,})*$"
    if not re.match(pattern, value):
        raise ValueError(
            "Name must contain only alphabetical characters and at least 2 characters long"
        )

    return value


def validate_birthday(birthday: date) -> date:
    today = date.today()
    age = today.year - birthday.year
    if (today.month, today.day) < (birthday.month, birthday.day):
        age -= 1

    if age < 16:
        raise ValueError("Consultee must be at least 16 years old.")

    return birthday


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
        r"(?i)\b(or|and)\b\s+(['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?|\d+\s*=\s*\d+)",
        r"['\"];?\s*(--|#|/\*)",
        r";\s*(select|insert|update|delete|drop|alter|truncate|create|grant|exec)\b",
        r"(?i)\bunion\s+(all\s+)?select\b",
    ]
    for pattern in patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValueError("Input contains unsafe SQL patterns.")

    return value


def validate_command_injection(value: str) -> str:
    if re.search(r"\$\(.*\)|`.*`", value):
        raise ValueError("Input contains unsafe system command patterns.")

    try:
        tokens = shlex.split(value, posix=False)
    except ValueError as e:
        raise ValueError("Input contains unsafe system command patterns.") from e

    disallowed_tokens = {"|", "||", ";", "&&", ">", ">>", "<", "<<"}
    dangerous_binaries = {"sh", "bash", "cmd", "powershell", "exec", "eval"}
    for i, token in enumerate(tokens):
        clean_token = token.strip().lower()
        if clean_token in disallowed_tokens:
            raise ValueError("Input contains unsafe system command patterns.")
        if clean_token.endswith(";") and len(clean_token) > 1:
            raise ValueError("Input contains unsafe system command patterns.")
        if (
            clean_token in dangerous_binaries
            and i > 0
            and tokens[i - 1].strip() in {"|", ";", "&&"}
        ):
            raise ValueError("Input contains unsafe system command patterns.")

    return value


def validate_email_address(value: str) -> str:
    try:
        check_email(value, check_deliverability=False)
    except EmailNotValidError as e:
        raise ValueError("Invalid email address format.") from e
    return value


def vector_validator(vector: object) -> bool:
    if not isinstance(vector, list) or len(vector) == 0:
        return False
    for item in vector:
        if not isinstance(item, (int, float)):
            return False
        if isinstance(item, float) and (math.isnan(item) or math.isinf(item)):
            return False
    return True


def validate_password_strength(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if len(value) > 40:
        raise ValueError("Password must not exceed 40 characters.")
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one number.")
    if not re.search(r"\W", value):
        raise ValueError("Password must contain at least one special character.")
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

SafePasswordStr = Annotated[
    SafeStr,
    AfterValidator(validate_password_strength),
]
