from models.article import db

from models.company import Company
from models.entity_alias import EntityAlias
from models.funding_round import FundingRound
from models.investor import Investor

from services.entity_merge_service import (
    merge_investors,
)

from services.entity_resolution_service import (
    resolve_entity_name,
)


def test_merge_investor_moves_round_relationships(
    app,
):
    alias = Investor(
        name="Index"
    )

    canonical = Investor(
        name="Index Ventures"
    )

    company = Company(
        name="Example Company"
    )

    db.session.add_all(
        [
            alias,
            canonical,
            company,
        ]
    )

    db.session.flush()

    funding_round = FundingRound(
        company=company
    )

    funding_round.investors.append(
        alias
    )

    funding_round.lead_investors.append(
        alias
    )

    db.session.add(
        funding_round
    )

    db.session.commit()

    assert (
        merge_investors(
            "Index",
            "Index Ventures",
        )
        is True
    )

    db.session.refresh(
        funding_round
    )

    investor_names = {
        investor.name
        for investor
        in funding_round.investors
    }

    lead_names = {
        investor.name
        for investor
        in funding_round.lead_investors
    }

    assert investor_names == {
        "Index Ventures",
    }

    assert lead_names == {
        "Index Ventures",
    }

    assert (
        Investor.query
        .filter_by(
            name="Index"
        )
        .first()
        is None
    )


def test_merge_investor_creates_durable_alias(
    app,
):
    alias = Investor(
        name="Index"
    )

    canonical = Investor(
        name="Index Ventures"
    )

    db.session.add_all(
        [
            alias,
            canonical,
        ]
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
        entity_alias
        .canonical_investor
        .name
        == "Index Ventures"
    )


def test_merged_name_resolves_to_canonical_investor(
    app,
):
    alias = Investor(
        name="Index"
    )

    canonical = Investor(
        name="Index Ventures"
    )

    db.session.add_all(
        [
            alias,
            canonical,
        ]
    )

    db.session.commit()

    merge_investors(
        "Index",
        "Index Ventures",
    )

    resolution = (
        resolve_entity_name(
            "Index",
            "investor",
        )
    )

    assert (
        resolution[
            "status"
        ]
        == "alias"
    )

    assert (
        resolution[
            "entity"
        ].name
        == "Index Ventures"
    )


def test_merge_repoints_existing_aliases(
    app,
):
    alias = Investor(
        name="Index"
    )

    canonical = Investor(
        name="Index Ventures"
    )

    db.session.add_all(
        [
            alias,
            canonical,
        ]
    )

    db.session.flush()

    previous_alias = EntityAlias(
        alias="Index VC",
        entity_type="investor",
        canonical_name="Index",
        canonical_investor=alias,
    )

    db.session.add(
        previous_alias
    )

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
        preserved
        .canonical_investor
        .name
        == "Index Ventures"
    )