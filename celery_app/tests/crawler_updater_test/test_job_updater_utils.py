from app.modules.company.models import Company
from app.modules.job.models import Job
from utils.job_updater_utils import has_duplicate_job_description, is_garbage_job


def test_is_garbage_job_unknown_title_empty_desc_unknown_company():
    company = Company(name="Unknown Company")
    job = Job(
        title="Unknown Title",
        job_description="",
        company=company,
    )
    assert is_garbage_job(job) is True


def test_is_garbage_job_unknown_title_placeholder_desc_vietnamworks():
    company = Company(name="Vietnamworks")
    job = Job(
        title="Unknown Title",
        job_description="Responsibilities: - No description provided",
        company=company,
    )
    assert is_garbage_job(job) is True


def test_is_garbage_job_unknown_title_with_valid_desc():
    company = Company(name="Unknown Company")
    job = Job(
        title="Unknown Title",
        job_description="We are looking for a software engineer",
        company=company,
    )
    assert is_garbage_job(job) is False


def test_is_garbage_job_unknown_title_without_company():
    job = Job(
        title="Unknown Title",
        job_description="",
        company=None,
    )
    assert is_garbage_job(job) is False


def test_is_garbage_job_unknown_title_with_other_company():
    company = Company(name="Google")
    job = Job(
        title="Unknown Title",
        job_description="",
        company=company,
    )
    assert is_garbage_job(job) is False


def test_is_garbage_job_error_page_title_vietnamese():
    company = Company(name="Valid Tech")
    job = Job(
        title="404 - Trang bạn đang tìm kiếm không tồn tại",
        job_description="Detailed software description here",
        company=company,
    )
    assert is_garbage_job(job) is True


def test_is_garbage_job_error_page_description_vietnamese():
    company = Company(name="Valid Tech")
    job = Job(
        title="Python Backend Developer",
        job_description="Xem Tất cả danh mục việc làm IT trên trang tuyển dụng",
        company=company,
    )
    assert is_garbage_job(job) is True


def test_is_garbage_job_valid_job():
    company = Company(name="VinFast")
    job = Job(
        title="Senior Python Engineer",
        job_description="Design and maintain high-throughput backend services using FastAPI.",
        company=company,
    )
    assert is_garbage_job(job) is False


def test_has_duplicate_job_description_empty_or_whitespace():
    assert has_duplicate_job_description("") is False
    assert has_duplicate_job_description("    \n\t  ") is False


def test_has_duplicate_job_description_punctuation_only():
    assert has_duplicate_job_description("... ??? !!! ,, ;;") is False


def test_has_duplicate_job_description_unique_content():
    text = "We are seeking a senior machine learning engineer to build innovative distributed AI solutions."
    assert has_duplicate_job_description(text) is False


def test_has_duplicate_job_description_repeated_phrases():
    text = (
        "Search job postings on a scale. "
        "Measure job postings on a scale. "
        "Recruitment search on a scale. "
        "Search job postings on a scale. "
        "Measure job postings on a scale. "
        "Recruitment search on a scale."
    )
    assert has_duplicate_job_description(text, threshold=0.6) is True


def test_has_duplicate_job_description_custom_threshold():
    text = "alpha beta gamma alpha beta delta"
    assert has_duplicate_job_description(text, threshold=0.3) is True
    assert has_duplicate_job_description(text, threshold=0.8) is False
