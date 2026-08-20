import pytest

from sqlalchemy.exc import IntegrityError

from models.article import db
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound
from models.fund import Fund
from models.fund_close import FundClose
from models.entity_alias import EntityAlias
from models.entity_resolution_review import (
    EntityResolutionReview,
)


def test_models_can_be_created():
    company = Company(
        name="Test Company"
    )

    investor = Investor(
        name="Test Investor"
    )

    funding_round = FundingRound(
        company=company,
        amount=50_000_000,
        currency="USD",
        round_type="Series B",
    )

    funding_round.investors.append(
        investor
    )

    funding_round.lead_investors.append(
        investor
    )

    fund = Fund(
        name="Test Fund I",
        investor=investor,
        strategy="Early Stage",
        geography="Europe",
        vintage_year=2026,
    )

    fund_close = FundClose(
        fund=fund,
        amount=300_000_000,
        currency="EUR",
        close_type="final_close",
    )

    assert (
        funding_round.company.name
        == "Test Company"
    )

    assert (
        funding_round.amount
        == 50_000_000
    )

    assert (
        funding_round.round_type
        == "Series B"
    )

    assert (
        funding_round.investors[0].name
        == "Test Investor"
    )

    assert (
        funding_round.lead_investors[0].name
        == "Test Investor"
    )

    assert (
        fund.name
        == "Test Fund I"
    )

    assert (
        fund.investor.name
        == "Test Investor"
    )

    assert (
        fund.strategy
        == "Early Stage"
    )

    assert (
        fund_close.fund.name
        == "Test Fund I"
    )

    assert (
        fund_close.amount
        == 300_000_000
    )

    assert (
        fund_close.close_type
        == "final_close"
    )


def test_same_alias_allowed_for_different_entity_types(
    app,
):
    with app.app_context():
        company = Company(
            name="Shared Company"
        )

        investor = Investor(
            name="Shared Investor"
        )

        db.session.add_all(
            [
                company,
                investor,
            ]
        )

        db.session.flush()

        company_alias = EntityAlias(
            alias="Shared Name",
            entity_type="company",
            canonical_name=company.name,
            canonical_company=company,
        )

        investor_alias = EntityAlias(
            alias="Shared Name",
            entity_type="investor",
            canonical_name=investor.name,
            canonical_investor=investor,
        )

        db.session.add_all(
            [
                company_alias,
                investor_alias,
            ]
        )

        db.session.flush()

        assert (
            EntityAlias.query.count()
            == 2
        )

        db.session.rollback()


def test_same_alias_rejected_within_same_entity_type(
    app,
):
    with app.app_context():
        company_a = Company(
            name="Company A"
        )

        company_b = Company(
            name="Company B"
        )

        db.session.add_all(
            [
                company_a,
                company_b,
            ]
        )

        db.session.flush()

        alias_a = EntityAlias(
            alias="Duplicate Name",
            entity_type="company",
            canonical_name=company_a.name,
            canonical_company=company_a,
        )

        alias_b = EntityAlias(
            alias="Duplicate Name",
            entity_type="company",
            canonical_name=company_b.name,
            canonical_company=company_b,
        )

        db.session.add_all(
            [
                alias_a,
                alias_b,
            ]
        )

        with pytest.raises(
            IntegrityError
        ):
            db.session.flush()

        db.session.rollback()


def test_company_alias_requires_company_target(
    app,
):
    with app.app_context():
        company = Company(
            name="Canonical Company"
        )

        db.session.add(
            company
        )

        db.session.flush()

        alias = EntityAlias(
            alias="Company Alias",
            entity_type="company",
            canonical_name=company.name,
            canonical_company=company,
        )

        db.session.add(
            alias
        )

        db.session.flush()

        assert (
            alias.canonical_entity
            is company
        )

        assert (
            alias.canonical_company_id
            == company.id
        )

        assert (
            alias.canonical_investor_id
            is None
        )

        db.session.rollback()


def test_investor_alias_requires_investor_target(
    app,
):
    with app.app_context():
        investor = Investor(
            name="Canonical Investor"
        )

        db.session.add(
            investor
        )

        db.session.flush()

        alias = EntityAlias(
            alias="Investor Alias",
            entity_type="investor",
            canonical_name=investor.name,
            canonical_investor=investor,
        )

        db.session.add(
            alias
        )

        db.session.flush()

        assert (
            alias.canonical_entity
            is investor
        )

        assert (
            alias.canonical_investor_id
            == investor.id
        )

        assert (
            alias.canonical_company_id
            is None
        )

        db.session.rollback()


def test_alias_rejects_wrong_target_type(
    app,
):
    with app.app_context():
        investor = Investor(
            name="Wrong Target Investor"
        )

        db.session.add(
            investor
        )

        db.session.flush()

        alias = EntityAlias(
            alias="Wrong Alias",
            entity_type="company",
            canonical_name=investor.name,
            canonical_investor=investor,
        )

        db.session.add(
            alias
        )

        with pytest.raises(
            IntegrityError
        ):
            db.session.flush()

        db.session.rollback()


def test_resolution_review_uses_stable_candidate_reference(
    app,
):
    with app.app_context():
        investor = Investor(
            name="Candidate Investor"
        )

        db.session.add(
            investor
        )

        db.session.flush()

        review = EntityResolutionReview(
            entity_type="investor",
            raw_name="Candidate Ventures",
            normalized_name="Candidate Ventures",
            candidate_name=investor.name,
            candidate_investor=investor,
            similarity_score=0.88,
            resolution_status="review",
        )

        db.session.add(
            review
        )

        db.session.flush()

        assert (
            review.candidate_entity
            is investor
        )

        assert (
            review.candidate_investor_id
            == investor.id
        )

        assert (
            review.candidate_company_id
            is None
        )

        db.session.rollback()


def test_resolution_review_rejects_multiple_candidates(
    app,
):
    with app.app_context():
        company = Company(
            name="Candidate Company"
        )

        investor = Investor(
            name="Candidate Investor"
        )

        db.session.add_all(
            [
                company,
                investor,
            ]
        )

        db.session.flush()

        review = EntityResolutionReview(
            entity_type="company",
            raw_name="Ambiguous Entity",
            normalized_name="Ambiguous Entity",
            candidate_name=company.name,
            candidate_company=company,
            candidate_investor=investor,
            similarity_score=0.75,
            resolution_status="review",
        )

        db.session.add(
            review
        )

        with pytest.raises(
            IntegrityError
        ):
            db.session.flush()

        db.session.rollback()