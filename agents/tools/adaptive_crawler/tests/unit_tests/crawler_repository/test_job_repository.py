import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

# Assuming standard model imports based on the provided architecture
from app.modules.job.models import Job, Skills
from app.modules.company.models import Company
from agents.tools.adaptive_crawler.crawler_repository.job_repository import (
    JobRepository,
)


@pytest.fixture
def mock_session():
    """
    Setup fixture to provide a completely isolated, stateless mock of the AsyncSession.
    Locks down the ORM layer to prevent actual database connections.
    """
    session = AsyncMock(spec=AsyncSession)

    # Mock transaction blocks for begin_nested() used in save_or_update
    mock_transaction = AsyncMock()
    mock_transaction.__aenter__.return_value = mock_transaction
    mock_transaction.__aexit__.return_value = None
    session.begin_nested.return_value = mock_transaction

    # Mock dialect for pg_advisory_xact_lock check
    mock_bind = MagicMock()
    mock_bind.dialect.name = "postgresql"
    session.get_bind.return_value = mock_bind

    return session


@pytest.mark.asyncio
class TestJobRepository:
    async def test_save_new_job_happy_path_and_associations(self, mock_session):
        """
        Locks down the happy path for job creation.
        Explicitly asserts that Company associations and Skills are correctly mapped
        and that their respective primary keys/IDs are attached to the Job before flush.
        """
        repo = JobRepository(mock_session)

        # Simulate empty DB (get_by_url returns None)
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        # Setup payload
        mock_company = Company(id=99, name="Test Corp")
        mock_skill = Skills(id=1, name="Python")
        job = Job(
            url="https://example.com/job/1",
            title="Backend Engineer",
            vector_context="Some context",
        )
        job.company = mock_company
        job.skills = [mock_skill]

        with (
            patch(
                "agents.tools.adaptive_crawler.crawler_repository.job_repository.CompanyRepository.save_or_update",
                new_callable=AsyncMock,
            ) as mock_comp_save,
            patch(
                "agents.tools.adaptive_crawler.crawler_repository.job_repository.generate_embedding_async",
                new_callable=AsyncMock,
            ) as mock_embed,
        ):
            mock_comp_save.return_value = mock_company
            mock_embed.return_value = [0.1, 0.2, 0.3]

            # Act
            saved_job = await repo.save_or_update(job, generate_embedding=True)

            # Assert Associations and Data Integrity
            assert saved_job.url == "https://example.com/job/1"
            assert saved_job.company_id == 99, (
                "Critical: Job must be associated with the persisted Company ID"
            )
            assert len(saved_job.skills) == 1
            assert saved_job.skills[0].name == "Python"
            assert saved_job.embedding == [0.1, 0.2, 0.3], (
                "Critical: Vector embedding was not correctly assigned"
            )

            # Assert DB interactions
            mock_session.add.assert_called()
            mock_session.flush.assert_called()

    async def test_save_job_missing_required_url_boundary(self, mock_session):
        """
        Locks down boundary condition: Job URL is the primary idempotency key.
        Asserts that a ValueError is strictly raised if this constraint is violated.
        """
        repo = JobRepository(mock_session)
        job = Job(url="", title="Ghost Job")

        with pytest.raises(
            ValueError, match="Job URL is required for repository operations."
        ):
            await repo.save_or_update(job)

    async def test_save_job_integrity_error_fallback(self, mock_session):
        """
        Locks down the critical concurrency constraint.
        If an INSERT fails due to a Unique Constraint violation (IntegrityError),
        the repository MUST fallback to fetching and updating the existing record
        to prevent data corruption or application crashes.
        """
        repo = JobRepository(mock_session)
        job = Job(url="https://example.com/duplicate")

        # First get_by_url returns None (looks like a new job)
        # Second get_by_url (inside the except block) returns an existing job
        existing_job = Job(url="https://example.com/duplicate", title="Old Title")

        mock_result_none = MagicMock()
        mock_result_none.first.return_value = None

        mock_result_existing = MagicMock()
        mock_result_existing.first.return_value = existing_job

        mock_session.exec.side_effect = [mock_result_none, mock_result_existing]

        # Force the INSERT block to throw an IntegrityError
        mock_session.flush.side_effect = [
            IntegrityError("Unique constraint failed", params={}, orig=Exception()),
            None,
        ]

        # Act
        result = await repo.save_or_update(job, generate_embedding=False)

        # Assert that the system recovered and updated the existing record
        assert result.title == "Old Title"
        assert (
            mock_session.add.call_count == 2
        )  # Once in try block (failed), once in except block (success)

    async def test_status_transitions_via_update_fields(self, mock_session):
        """
        Locks down status transition logic.
        Validates that `_update_job_fields` correctly overrides properties
        like Job Status (e.g., Draft -> Active) without losing existing data.
        """
        repo = JobRepository(mock_session)
        existing_job = Job(url="http://test.com", status="Draft", min_salary=1000)
        incoming_job = Job(url="http://test.com", status="Active", min_salary=2000)

        # Act
        repo._update_job_fields(existing_job, incoming_job)

        # Assert strict payload mutation
        assert existing_job.status == "Active", "Job status transition failed"
        assert existing_job.min_salary == 2000.0, "Numeric field update failed"

    async def test_get_by_url_malicious_input_sql_injection(self, mock_session):
        """
        Locks down security parameters.
        Ensures that malicious strings passed to get_by_url do not break the ORM
        and properly yield an empty result set (None).
        """
        repo = JobRepository(mock_session)
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        malicious_url = "https://a.com'; DROP TABLE jobs;--"

        # Act
        result = await repo.get_by_url(malicious_url)

        assert result is None
        mock_session.exec.assert_called_once()
