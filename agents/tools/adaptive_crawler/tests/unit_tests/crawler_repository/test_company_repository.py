import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.company.models import Company, CompanyBenefit
from agents.tools.adaptive_crawler.crawler_repository.company_repository import (
    CompanyRepository,
)


@pytest.fixture
def mock_session():
    """
    Setup fixture for completely isolated, stateless AsyncSession mock.
    """
    session = AsyncMock(spec=AsyncSession)

    mock_transaction = AsyncMock()
    mock_transaction.__aenter__.return_value = mock_transaction
    mock_transaction.__aexit__.return_value = None
    session.begin_nested.return_value = mock_transaction

    mock_bind = MagicMock()
    mock_bind.dialect.name = "postgresql"
    session.get_bind.return_value = mock_bind

    return session


@pytest.mark.asyncio
class TestCompanyRepository:
    async def test_save_company_missing_name(self, mock_session):
        """
        Locks down fundamental data constraints.
        Company name cannot be null or empty string.
        """
        repo = CompanyRepository(mock_session)
        company = Company(name="", industry="IT")

        with pytest.raises(
            ValueError, match="Company name is required for repository operations."
        ):
            await repo.save_or_update(company)

    async def test_update_company_cascading_benefits_deduplication(self, mock_session):
        """
        Locks down cascading relational logic.
        When updating a company profile, incoming CompanyBenefits must be
        deduplicated against existing benefits (case-insensitive) to prevent
        database bloat and Cartesian explosion on reads.
        """
        repo = CompanyRepository(mock_session)

        target_company = Company(
            name="Tech", benefits=[CompanyBenefit(name="Health Insurance")]
        )
        source_company = Company(
            name="Tech",
            benefits=[
                CompanyBenefit(name="HEALTH insurance "),
                CompanyBenefit(name="Free Lunch"),
            ],
        )

        repo._update_company_fields(target_company, source_company)

        benefit_names = {b.name for b in target_company.benefits}
        assert len(benefit_names) == 2, (
            "Cascading update failed to deduplicate benefits properly"
        )
        assert "Free Lunch" in benefit_names
        assert "HEALTH insurance " not in benefit_names

    async def test_save_company_integrity_error_snapshot_isolation_failure(
        self, mock_session
    ):
        """
        Locks down a highly specific and critical database error state.
        If an IntegrityError occurs during insert, but `get_by_name` subsequently returns None,
        it indicates a severe transaction snapshot isolation issue. The system MUST raise a RuntimeError.
        """
        repo = CompanyRepository(mock_session)
        company = Company(name="Phantom Corp")

        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        mock_session.flush.side_effect = IntegrityError(
            "Unique constraint failed", params={}, orig=Exception()
        )

        expected_error_regex = (
            r"IntegrityError occurred during insert.*but get_by_name returned None"
        )
        with pytest.raises(RuntimeError, match=expected_error_regex):
            await repo.save_or_update(company, generate_embedding=False)

    async def test_get_by_name_soft_delete_and_verification_simulation(
        self, mock_session
    ):
        """
        Locks down the query fetching mechanism.
        Ensures that missing entities (e.g., filtered out via soft-delete logic at the DB view level,
        or simply not found) strictly return a NoneType without throwing index exceptions.
        """
        repo = CompanyRepository(mock_session)

        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        result = await repo.get_by_name("Deleted Company")

        assert result is None
        assert type(result) is not Company

    async def test_save_company_skips_embedding_if_context_unchanged(
        self, mock_session
    ):
        """
        Locks down API cost optimization constraints.
        If the vector_context of a company hasn't changed, the repository MUST skip
        calling the expensive generate_embedding_async service.
        """
        repo = CompanyRepository(mock_session)

        existing_company = Company(
            name="Immutable Corp",
            vector_context="Context A",
            embedding=[0.1],
            embedding_model="v1",
            embedding_version=1,
        )
        incoming_company = Company(name="Immutable Corp", vector_context="Context A")

        mock_result = MagicMock()
        mock_result.first.return_value = existing_company
        mock_session.exec.return_value = mock_result

        with patch(
            "agents.tools.adaptive_crawler.crawler_repository.company_repository.generate_embedding_async",
            new_callable=AsyncMock,
        ) as mock_embed:
            await repo.save_or_update(incoming_company, generate_embedding=True)

            mock_embed.assert_not_called()
