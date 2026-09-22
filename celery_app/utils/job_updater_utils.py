from app.modules.job.models import Job


def is_garbage_job(job: Job) -> bool:
    is_unknown_garbage = (
        job.title == "Unknown Title"
        and (
            job.job_description == ""
            or job.job_description == "Responsibilities: - No description provided"
        )
        and job.company is not None
        and job.company.name in ["Unknown Company", "Vietnamworks"]
    )
    is_error_page_garbage = bool(
        job.title
        and (
            "Trang bạn đang tìm kiếm" in job.title
            or "Tất cả danh mục" in job.job_description
        )
    )
    return is_unknown_garbage or is_error_page_garbage


def has_duplicate_job_description(job_description: str, threshold: float = 0.6) -> bool:
    if not job_description or not job_description.strip():
        return False

    words = []
    punctuation_characters = ".,!?;:()[]\"'{}"
    for raw_word in job_description.lower().split():
        cleaned_word = raw_word.strip(punctuation_characters)
        if cleaned_word != "":
            words.append(cleaned_word)

    if not words:
        return False

    unique_words_count = len(set(words))
    duplicate_ratio = 1.0 - (unique_words_count / len(words))
    return duplicate_ratio > threshold
