import re
from datetime import UTC, date, datetime, timedelta


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
