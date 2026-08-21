from datetime import datetime

import pytest

from models.article import (
    Article,
    db,
)
from models.company import Company
from models.funding_round import FundingRound
from models.investor import Investor

from services.multi_round_integrity_service import (
    audit_multi_round_integrity,
    plan_multi_round_repair,
    repair_multi_round_article,
)


def _review_article(
    source="Sequoia Capital",
    suffix="one",
):
    article = Article(
        title="Partnering with Example",
        source=source,
        source_type="investor",
        discovery_method="sitemap",
        url=(
            "https://example.com/"
            f"multi-round-{suffix}"
        ),
        published_at=datetime(
            2026,
            1,
            10,
        ),
        content=(
            "Example raised a seed round led by Sequoia and "
            "a subsequent Series A led by Another Capital."
        ),
        category="Funding Round",
        llm_processed_at=datetime(
            2026,
            8,
            20,
        ),
        llm_is_funding_round=True,
    )

    db.session.add(
        article
    )
    db.session.flush()

    return article


def _blocking_article(
    suffix="collection",
):
    article = Article(
        title=(
            "Weekly Funding Roundup: "
            "The biggest deals this week"
        ),
        source="Test",
        source_type="publication",
        discovery_method="rss",
        url=(
            "https://example.com/"
            f"{suffix}"
        ),
        published_at=datetime(
            2026,
            1,
            10,
        ),
        content=(
            "Several companies announced new funding."
        ),
        category="Funding Round",
        llm_processed_at=datetime(
            2026,
            8,
            20,
        ),
        llm_is_funding_round=True,
    )

    db.session.add(
        article
    )
    db.session.flush()

    return article


def _round(
    article,
    company_name="Example",
):
    company = Company(
        name=company_name
    )

    investor = Investor(
        name=(
            "Sequoia Capital "
            f"{article.id}"
        )
    )

    db.session.add_all(
        [
            company,
            investor,
        ]
    )
    db.session.flush()

    funding_round = FundingRound(
        company=company,
        event_evidence=(
            "Synthetic financing event."
        ),
        amount=10_000_000,
        currency="USD",
        round_type="Series A",
        canonical_round_type="Series A",
        announced_at=article.published_at,
        article=article,
    )

    funding_round.investors.append(
        investor
    )
    funding_round.lead_investors.append(
        investor
    )
    funding_round.articles.append(
        article
    )

    db.session.add(
        funding_round
    )
    db.session.flush()

    return funding_round


def test_review_signal_with_sole_support_is_not_auto_delete(
    app,
):
    article = _review_article()
    funding_round = _round(
        article
    )

    result = (
        audit_multi_round_integrity(
            source_name="Sequoia Capital"
        )
    )

    assert (
        result[
            "review_only_candidates"
        ]
        == 1
    )

    assert (
        result[
            "automatic_repair_candidates"
        ]
        == 0
    )

    row = result[
        "rows"
    ][0]

    assert (
        row[
            "round_id"
        ]
        == funding_round.id
    )

    assert (
        row[
            "recommended_action"
        ]
        == "review_only"
    )


def test_review_only_repair_requires_explicit_confirmation(
    app,
):
    article = _review_article(
        suffix="confirm"
    )
    _round(
        article
    )

    plan = (
        plan_multi_round_repair(
            article.id
        )
    )

    assert (
        plan[
            "can_apply"
        ]
        is False
    )

    confirmed_plan = (
        plan_multi_round_repair(
            article.id,
            confirmed_invalid=True,
        )
    )

    assert (
        confirmed_plan[
            "can_apply"
        ]
        is True
    )


def test_confirmed_review_only_apply_deletes_sole_supported_round(
    app,
):
    article = _review_article(
        suffix="apply"
    )
    funding_round = _round(
        article
    )

    round_id = funding_round.id

    result = (
        repair_multi_round_article(
            article_id=article.id,
            apply=True,
            confirmed_invalid=True,
        )
    )

    assert (
        result[
            "rounds_deleted"
        ]
        == 1
    )

    assert (
        db.session.get(
            FundingRound,
            round_id,
        )
        is None
    )

    assert (
        article.llm_processed_at
        is None
    )


def test_blocking_collection_can_be_automatic_repair_candidate(
    app,
):
    article = _blocking_article()
    _round(
        article
    )

    plan = (
        plan_multi_round_repair(
            article.id
        )
    )

    assert (
        plan[
            "can_apply"
        ]
        is True
    )

    assert (
        plan[
            "blocking_reasons"
        ]
        == ["collection"]
    )


def test_shared_support_refuses_repair_even_when_confirmed(
    app,
):
    article = _review_article(
        suffix="shared"
    )
    funding_round = _round(
        article
    )

    second = Article(
        title="Independent confirmation",
        source="TechCrunch",
        source_type="publication",
        discovery_method="rss",
        url=(
            "https://example.com/"
            "independent-confirmation"
        ),
        published_at=datetime(
            2026,
            1,
            11,
        ),
        content=(
            "Example raised one Series A funding round."
        ),
        category="Funding Round",
    )

    db.session.add(
        second
    )
    db.session.flush()

    funding_round.articles.append(
        second
    )
    db.session.flush()

    plan = (
        plan_multi_round_repair(
            article.id,
            confirmed_invalid=True,
        )
    )

    assert (
        plan[
            "can_apply"
        ]
        is False
    )

    with pytest.raises(
        ValueError
    ):
        repair_multi_round_article(
            article_id=article.id,
            apply=True,
            confirmed_invalid=True,
        )