from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

# Assuming these are available in your project structure
from app.core.enums import (
    CompanyType,
    Currency,
    JobStatus,
    SeniorityLevel,
    WorkingModel,
)
from app.modules.company.models import Company, CompanyBenefit
from app.modules.job.models import Job, Skills


def create_valid_company(name: str = "Test Company") -> Company:
    """Helper to create a company with required fields."""
    return Company(
        name=name,
        industry="Technology",
        size="10-50",
        location="Remote",
        description="A great place to work.",
        website="https://testcompany.com",
        vector_context="company context",
        company_type=CompanyType.PRODUCT,
    )


def create_valid_job(
    title: str = "Software Engineer", url: str = "http://job.com/1"
) -> Job:
    """Helper to create a job with required fields and constraints."""
    return Job(
        title=title,
        job_description="Write clean code.",
        expired_date=datetime.now(UTC) + timedelta(days=30),
        seniority=SeniorityLevel.MID,
        min_salary=1000.0,
        max_salary=2000.0,  # Respects min_salary <= max_salary constraint
        currency=Currency.USD,
        working_hours="9-5",
        working_model=WorkingModel.REMOTE,
        status=JobStatus.OPEN,
        vector_context="job context",
        source="career_page",
        url=url,
    )


class TestModelRelationships:
    def test_job_company_n_to_1_relationship(self, db_session: Session) -> None:
        # Arrange: Create a single company and multiple jobs
        company = create_valid_company("Tech Hub Inc")
        job1 = create_valid_job(title="Backend Developer", url="http://job.com/backend")
        job2 = create_valid_job(
            title="Frontend Developer", url="http://job.com/frontend"
        )

        # Link jobs to the company (N-1)
        job1.company = company
        job2.company = company

        db_session.add(company)
        db_session.add(job1)
        db_session.add(job2)
        db_session.commit()

        # Act: Retrieve the jobs from the database
        db_job1 = db_session.exec(
            select(Job).where(Job.title == "Backend Developer")
        ).first()
        db_job2 = db_session.exec(
            select(Job).where(Job.title == "Frontend Developer")
        ).first()

        # Assert: Both jobs correctly point to the same company instance
        assert db_job1 is not None
        assert db_job2 is not None
        assert db_job1.company_id == company.id
        assert db_job2.company_id == company.id

        # Verify the bidirectional 1-N relationship loaded via 'selectin'
        assert db_job1.company.name == "Tech Hub Inc"
        assert len(db_job1.company.jobs) == 2
        assert {j.title for j in db_job1.company.jobs} == {
            "Backend Developer",
            "Frontend Developer",
        }

    def test_company_benefit_cascade_delete(self, db_session: Session) -> None:
        # Arrange
        company = create_valid_company("Benefits Corp")
        benefit1 = CompanyBenefit(name="Health Insurance")
        benefit2 = CompanyBenefit(name="Gym Membership")

        company.benefits = [benefit1, benefit2]
        db_session.add(company)
        db_session.commit()

        company_id = company.id

        # Act: Delete the company
        db_session.delete(company)
        db_session.commit()

        # Assert: Benefits should be orphaned and deleted due to cascade="all, delete-orphan"
        benefits_in_db = db_session.exec(
            select(CompanyBenefit).where(CompanyBenefit.company_id == company_id)
        ).all()
        assert len(benefits_in_db) == 0

    def test_job_skills_many_to_many_relationship(self, db_session: Session) -> None:
        # Arrange
        job = create_valid_job(title="Data Scientist", url="http://job.com/data")
        skill_python = Skills(name="Python", category="Programming")
        skill_sql = Skills(name="SQL", category="Database")

        # Append skills to the job
        job.skills.append(skill_python)
        job.skills.append(skill_sql)

        db_session.add(job)
        db_session.commit()

        # Act
        db_job = db_session.exec(select(Job).where(Job.id == job.id)).first()
        db_python = db_session.exec(
            select(Skills).where(Skills.name == "Python")
        ).first()

        # Assert: Job has the skills
        assert db_job is not None
        assert len(db_job.skills) == 2
        assert {s.name for s in db_job.skills} == {"Python", "SQL"}

        # Assert: Bidirectional relationship (Skill knows its jobs)
        assert db_python is not None
        assert db_python.jobs is not None
        assert db_python.jobs.title == "Data Scientist"

    def test_job_company_foreign_key_cascade_delete(self, db_session: Session) -> None:
        # Arrange
        company = create_valid_company("Temporary Corp")
        job = create_valid_job(title="Temp Worker", url="http://job.com/temp")
        job.company = company

        db_session.add(company)
        db_session.add(job)
        db_session.commit()

        job_id = job.id

        # Act: Force execution of SQLite foreign key cascades
        # SQLite needs PRAGMA foreign_keys = ON; normally handled by the test engine setup,
        # but we simulate the deletion to check DB-level constraint
        from sqlmodel import delete

        db_session.execute(delete(Company).where(Company.id == company.id))
        db_session.commit()
        db_session.expire_all()

        # Assert: Job should be deleted because job.company_id has ondelete="CASCADE"
        db_job = db_session.exec(select(Job).where(Job.id == job_id)).first()
        assert db_job is None
