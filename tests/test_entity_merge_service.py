from models.article import db
from models.company import Company
from models.entity_alias import EntityAlias
from models.entity_resolution_review import (
    EntityResolutionReview,
)
from models.funding_round import FundingRound
from models.investor import Investor

from services.entity_merge_service import (
    merge_companies,
    merge_investors,
    remove_invalid_investor,
    rename_company,
)
from services.entity_resolution_service import (
    resolve_entity_name,
)


def test_merge_investor_moves_round_relationships(app):
    alias = Investor(name="Index")
    canonical = Investor(name="Index Ventures")
    company = Company(name="Example Company")

    db.session.add_all(
        [alias, canonical, company]
    )
    db.session.flush()

    funding_round = FundingRound(
        company=company
    )
    funding_round.investors.append(alias)
    funding_round.lead_investors.append(alias)

    db.session.add(funding_round)
    db.session.commit()

    assert (
        merge_investors(
            "Index",
            "Index Ventures",
        )
        is True
    )

    db.session.refresh(funding_round)

    assert {
        investor.name
        for investor in funding_round.investors
    } == {"Index Ventures"}

    assert {
        investor.name
        for investor in funding_round.lead_investors
    } == {"Index Ventures"}

    assert (
        Investor.query
        .filter_by(name="Index")
        .first()
        is None
    )


def test_merge_investor_does_not_duplicate_existing_relationship(app):
    alias = Investor(name="Index")
    canonical = Investor(name="Index Ventures")
    company = Company(name="Example Company")

    db.session.add_all(
        [alias, canonical, company]
    )
    db.session.flush()

    funding_round = FundingRound(
        company=company
    )
    funding_round.investors.extend(
        [alias, canonical]
    )
    funding_round.lead_investors.extend(
        [alias, canonical]
    )

    db.session.add(funding_round)
    db.session.commit()

    assert (
        merge_investors(
            "Index",
            "Index Ventures",
        )
        is True
    )

    db.session.refresh(funding_round)

    assert [
        investor.name
        for investor in funding_round.investors
    ] == ["Index Ventures"]

    assert [
        investor.name
        for investor in funding_round.lead_investors
    ] == ["Index Ventures"]


def test_merge_investor_preserves_missing_canonical_metadata(app):
    alias = Investor(
        name="Index",
        website="https://index.example",
        description="Alias description",
        headquarters="London",
    )
    canonical = Investor(
        name="Index Ventures"
    )

    db.session.add_all(
        [alias, canonical]
    )
    db.session.commit()

    assert (
        merge_investors(
            "Index",
            "Index Ventures",
        )
        is True
    )

    preserved = Investor.query.filter_by(
        name="Index Ventures"
    ).one()

    assert preserved.website == (
        "https://index.example"
    )
    assert preserved.description == (
        "Alias description"
    )
    assert preserved.headquarters == "London"


def test_merge_investor_does_not_overwrite_canonical_metadata(app):
    alias = Investor(
        name="Index",
        website="https://alias.example",
        description="Alias description",
        headquarters="Alias HQ",
    )
    canonical = Investor(
        name="Index Ventures",
        website="https://canonical.example",
        description="Canonical description",
        headquarters="Canonical HQ",
    )

    db.session.add_all(
        [alias, canonical]
    )
    db.session.commit()

    merge_investors(
        "Index",
        "Index Ventures",
    )

    preserved = Investor.query.filter_by(
        name="Index Ventures"
    ).one()

    assert preserved.website == (
        "https://canonical.example"
    )
    assert preserved.description == (
        "Canonical description"
    )
    assert preserved.headquarters == (
        "Canonical HQ"
    )


def test_merge_investor_creates_missing_canonical_entity(app):
    alias = Investor(
        name="Index",
        website="https://index.example",
    )

    db.session.add(alias)
    db.session.commit()

    assert (
        merge_investors(
            "Index",
            "Index Ventures",
        )
        is True
    )

    canonical = Investor.query.filter_by(
        name="Index Ventures"
    ).one()

    assert canonical.website == (
        "https://index.example"
    )

    assert (
        Investor.query
        .filter_by(name="Index")
        .first()
        is None
    )


def test_merge_investor_creates_durable_alias(app):
    alias = Investor(name="Index")
    canonical = Investor(
        name="Index Ventures"
    )

    db.session.add_all(
        [alias, canonical]
    )
    db.session.commit()

    merge_investors(
        "Index",
        "Index Ventures",
    )

    entity_alias = (
        EntityAlias.query
        .filter_by(
            alias="Index",
            entity_type="investor",
        )
        .first()
    )

    assert entity_alias is not None
    assert (
        entity_alias.canonical_name
        == "Index Ventures"
    )
    assert (
        entity_alias.canonical_investor
        is not None
    )
    assert (
        entity_alias.canonical_investor.name
        == "Index Ventures"
    )


def test_merged_name_resolves_to_canonical_investor(app):
    alias = Investor(name="Index")
    canonical = Investor(
        name="Index Ventures"
    )

    db.session.add_all(
        [alias, canonical]
    )
    db.session.commit()

    merge_investors(
        "Index",
        "Index Ventures",
    )

    resolution = resolve_entity_name(
        "Index",
        "investor",
    )

    assert resolution["status"] == "alias"
    assert (
        resolution["entity"].name
        == "Index Ventures"
    )


def test_merge_repoints_existing_aliases(app):
    alias = Investor(name="Index")
    canonical = Investor(
        name="Index Ventures"
    )

    db.session.add_all(
        [alias, canonical]
    )
    db.session.flush()

    previous_alias = EntityAlias(
        alias="Index VC",
        entity_type="investor",
        canonical_name="Index",
        canonical_investor=alias,
    )

    db.session.add(previous_alias)
    db.session.commit()

    merge_investors(
        "Index",
        "Index Ventures",
    )

    preserved = (
        EntityAlias.query
        .filter_by(
            alias="Index VC",
            entity_type="investor",
        )
        .first()
    )

    assert preserved is not None
    assert (
        preserved.canonical_name
        == "Index Ventures"
    )
    assert (
        preserved.canonical_investor.name
        == "Index Ventures"
    )


def test_merge_investor_repoints_resolution_reviews(app):
    alias = Investor(name="Index")
    canonical = Investor(
        name="Index Ventures"
    )

    db.session.add_all(
        [alias, canonical]
    )
    db.session.flush()

    review = EntityResolutionReview(
        entity_type="investor",
        raw_name="Index Ventures",
        normalized_name="Index Ventures",
        candidate_name="Index",
        candidate_investor=alias,
        similarity_score=1.0,
        resolution_status="strong_candidate",
    )

    db.session.add(review)
    db.session.commit()

    assert (
        merge_investors(
            "Index",
            "Index Ventures",
        )
        is True
    )

    db.session.refresh(review)

    assert (
        review.candidate_investor_id
        == canonical.id
    )
    assert (
        review.candidate_investor.name
        == "Index Ventures"
    )
    assert (
        review.candidate_name
        == "Index Ventures"
    )


def test_invalid_investor_merges_do_not_mutate(app):
    investor = Investor(name="Index")

    db.session.add(investor)
    db.session.commit()

    assert merge_investors(
        None,
        "Index Ventures",
    ) is False

    assert merge_investors(
        "Index",
        None,
    ) is False

    assert merge_investors(
        "   ",
        "Index Ventures",
    ) is False

    assert merge_investors(
        "Index",
        "Index",
    ) is False

    assert merge_investors(
        "Missing Investor",
        "Index Ventures",
    ) is False

    assert Investor.query.count() == 1
    assert (
        Investor.query.one().name
        == "Index"
    )


def test_merge_company_moves_funding_rounds(app):
    alias = Company(name="Acme AI")
    canonical = Company(name="Acme")

    db.session.add_all(
        [alias, canonical]
    )
    db.session.flush()

    funding_round = FundingRound(
        company=alias
    )

    db.session.add(funding_round)
    db.session.commit()

    assert (
        merge_companies(
            "Acme AI",
            "Acme",
        )
        is True
    )

    db.session.refresh(funding_round)

    assert funding_round.company.name == "Acme"

    assert (
        Company.query
        .filter_by(name="Acme AI")
        .first()
        is None
    )


def test_merge_company_preserves_missing_canonical_metadata(app):
    alias = Company(
        name="Acme AI",
        website="https://acme.example",
        description="Alias description",
        sector="AI",
        canonical_sector="Artificial Intelligence",
        headquarters="London",
        city="London",
        country="United Kingdom",
        founded_year=2020,
    )
    canonical = Company(name="Acme")

    db.session.add_all(
        [alias, canonical]
    )
    db.session.commit()

    merge_companies(
        "Acme AI",
        "Acme",
    )

    preserved = Company.query.filter_by(
        name="Acme"
    ).one()

    assert preserved.website == (
        "https://acme.example"
    )
    assert preserved.description == (
        "Alias description"
    )
    assert preserved.sector == "AI"
    assert preserved.canonical_sector == (
        "Artificial Intelligence"
    )
    assert preserved.headquarters == "London"
    assert preserved.city == "London"
    assert preserved.country == (
        "United Kingdom"
    )
    assert preserved.founded_year == 2020


def test_merge_company_does_not_overwrite_canonical_metadata(app):
    alias = Company(
        name="Acme AI",
        website="https://alias.example",
        description="Alias description",
        sector="Alias sector",
        canonical_sector="Alias canonical sector",
        headquarters="Alias HQ",
        city="Alias City",
        country="Alias Country",
        founded_year=2020,
    )
    canonical = Company(
        name="Acme",
        website="https://canonical.example",
        description="Canonical description",
        sector="Canonical sector",
        canonical_sector="Canonical taxonomy",
        headquarters="Canonical HQ",
        city="Canonical City",
        country="Canonical Country",
        founded_year=2018,
    )

    db.session.add_all(
        [alias, canonical]
    )
    db.session.commit()

    merge_companies(
        "Acme AI",
        "Acme",
    )

    preserved = Company.query.filter_by(
        name="Acme"
    ).one()

    assert preserved.website == (
        "https://canonical.example"
    )
    assert preserved.description == (
        "Canonical description"
    )
    assert preserved.sector == (
        "Canonical sector"
    )
    assert preserved.canonical_sector == (
        "Canonical taxonomy"
    )
    assert preserved.headquarters == (
        "Canonical HQ"
    )
    assert preserved.city == (
        "Canonical City"
    )
    assert preserved.country == (
        "Canonical Country"
    )
    assert preserved.founded_year == 2018


def test_merge_company_creates_missing_canonical_entity(app):
    alias = Company(
        name="Acme AI",
        country="United Kingdom",
    )

    db.session.add(alias)
    db.session.commit()

    assert (
        merge_companies(
            "Acme AI",
            "Acme",
        )
        is True
    )

    canonical = Company.query.filter_by(
        name="Acme"
    ).one()

    assert canonical.country == (
        "United Kingdom"
    )


def test_merge_company_repoints_resolution_reviews(app):
    alias = Company(name="Acme AI")
    canonical = Company(name="Acme")

    db.session.add_all(
        [alias, canonical]
    )
    db.session.flush()

    review = EntityResolutionReview(
        entity_type="company",
        raw_name="Acme",
        normalized_name="Acme",
        candidate_name="Acme AI",
        candidate_company=alias,
        similarity_score=1.0,
        resolution_status="strong_candidate",
    )

    db.session.add(review)
    db.session.commit()

    assert (
        merge_companies(
            "Acme AI",
            "Acme",
        )
        is True
    )

    db.session.refresh(review)

    assert (
        review.candidate_company_id
        == canonical.id
    )
    assert (
        review.candidate_company.name
        == "Acme"
    )
    assert review.candidate_name == "Acme"


def test_remove_invalid_investor_removes_relationships(app):
    investor = Investor(
        name="Invalid Investor"
    )
    company = Company(
        name="Example Company"
    )

    db.session.add_all(
        [investor, company]
    )
    db.session.flush()

    funding_round = FundingRound(
        company=company
    )
    funding_round.investors.append(
        investor
    )
    funding_round.lead_investors.append(
        investor
    )

    db.session.add(funding_round)
    db.session.commit()

    assert (
        remove_invalid_investor(
            "Invalid Investor"
        )
        is True
    )

    db.session.refresh(funding_round)

    assert funding_round.investors == []
    assert funding_round.lead_investors == []

    assert (
        Investor.query
        .filter_by(
            name="Invalid Investor"
        )
        .first()
        is None
    )


def test_remove_invalid_investor_returns_false_when_missing(app):
    assert (
        remove_invalid_investor(
            "Missing Investor"
        )
        is False
    )


def test_rename_company_creates_durable_alias(app):
    company = Company(
        name="Acme AI"
    )

    db.session.add(company)
    db.session.commit()

    assert (
        rename_company(
            "Acme AI",
            "Acme",
        )
        is True
    )

    renamed = Company.query.filter_by(
        name="Acme"
    ).one()

    alias = EntityAlias.query.filter_by(
        alias="Acme AI",
        entity_type="company",
    ).one()

    assert (
        alias.canonical_company_id
        == renamed.id
    )
    assert (
        alias.canonical_name
        == "Acme"
    )


def test_rename_company_refuses_existing_name_collision(app):
    current = Company(
        name="Acme AI"
    )
    existing = Company(
        name="Acme"
    )

    db.session.add_all(
        [current, existing]
    )
    db.session.commit()

    assert (
        rename_company(
            "Acme AI",
            "Acme",
        )
        is False
    )

    assert (
        Company.query
        .filter_by(name="Acme AI")
        .one()
        is current
    )

    assert (
        EntityAlias.query
        .filter_by(
            alias="Acme AI",
            entity_type="company",
        )
        .first()
        is None
    )
