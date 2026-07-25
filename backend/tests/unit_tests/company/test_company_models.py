from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.enums import CompanyType
from app.modules.company.models import Company, CompanyBenefit


class TestCompanyModels:
    def test_create_company_success(self, db_session: Session) -> None:
        company = Company(
            name="Tech Corp",
            industry="IT",
            size="100-500",
            location="Remote",
            description="A great tech company",
            website="https://techcorp.example.com",
            slogan="Innovating the future",
            company_type=CompanyType.PRODUCT,
            vector_context="Tech company focusing on AI",
            embedding=[0.1, 0.2, 0.3],
            addresses=["123 Tech Street"],
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.id is not None
        assert company.name == "Tech Corp"
        assert company.addresses == ["123 Tech Street"]
        assert len(company.embedding) == 3

    def test_company_unique_name_constraint(self, db_session: Session) -> None:
        company1 = Company(
            name="Unique Company",
            industry="Finance",
            size="1-50",
            location="NY",
            description="Desc",
            website="https://unique.example.com",
            vector_context="Context",
        )
        db_session.add(company1)
        db_session.commit()

        company2 = Company(
            name="Unique Company",
            industry="Health",
            size="1-50",
            location="CA",
            description="Desc 2",
            website="https://unique2.example.com",
            vector_context="Context 2",
        )
        db_session.add(company2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_company_benefits_relationship(self, db_session: Session) -> None:
        company = Company(
            name="Benefit Corp",
            industry="HR",
            size="1-50",
            location="Remote",
            description="Desc",
            website="https://benefit.example.com",
            vector_context="Context",
        )
        benefit1 = CompanyBenefit(name="Health Insurance")
        benefit2 = CompanyBenefit(name="Remote Work")

        company.benefits.extend([benefit1, benefit2])
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert len(company.benefits) == 2
        assert company.benefits[0].company_id == company.id

    def test_company_benefits_cascade_delete(self, db_session: Session) -> None:
        company = Company(
            name="Cascade Corp",
            industry="Legal",
            size="1-50",
            location="Remote",
            description="Desc",
            website="https://cascade.example.com",
            vector_context="Context",
        )
        benefit = CompanyBenefit(name="401k")
        company.benefits.append(benefit)

        db_session.add(company)
        db_session.commit()

        assert db_session.get(CompanyBenefit, benefit.id) is not None

        db_session.delete(company)
        db_session.commit()

        assert db_session.get(CompanyBenefit, benefit.id) is None
