from datetime import datetime, timedelta

from models.article import db, Article
from models.company import Company
from models.funding_round import FundingRound

from services.data_cleanup_service import (
    find_duplicate_funding_rounds,
    reconcile_historical_funding_rounds,
)


def _create_article(
    *,
    title,
    url,
    published_at,
):
    article = Article(
        title=title,
        source="Test Source",
        url=url,
        published_at=published_at,
        summary="Test summary",
        category="Funding Round",
    )

    db.session.add(
        article
    )

    db.session.flush()

    return article


def _create_round(
    *,
    company,
    article,
    announced_at,
):
    funding_round = FundingRound(
        company=company,
        article=article,
        amount=10_000_000,
        currency="USD",
        round_type="Series A",
        canonical_round_type="Series A",
        announced_at=announced_at,
        event_evidence="Funding event.",
    )

    funding_round.articles.append(
        article
    )

    db.session.add(
        funding_round
    )

    db.session.flush()

    return funding_round


def test_dry_run_does_not_modify_database(
    app,
):
    with app.app_context():
        company = Company(
            name="Dry Run Company"
        )

        db.session.add(
            company
        )

        db.session.flush()

        date = datetime(
            2026,
            8,
            10,
        )

        article_a = _create_article(
            title="Article A",
            url="https://example.com/dry-a",
            published_at=date,
        )

        article_b = _create_article(
            title="Article B",
            url="https://example.com/dry-b",
            published_at=(
                date
                + timedelta(days=1)
            ),
        )

        _create_round(
            company=company,
            article=article_a,
            announced_at=date,
        )

        _create_round(
            company=company,
            article=article_b,
            announced_at=(
                date
                + timedelta(days=1)
            ),
        )

        before_count = (
            FundingRound.query.count()
        )

        result = (
            reconcile_historical_funding_rounds(
                apply=False
            )
        )

        after_count = (
            FundingRound.query.count()
        )

        assert before_count == 2
        assert after_count == 2

        assert (
            result["mode"]
            == "dry_run"
        )

        assert (
            result["initial_candidates"]
            == 1
        )

        assert result["merged"] == 0

        db.session.rollback()


def test_apply_merges_duplicate_pair(
    app,
):
    with app.app_context():
        company = Company(
            name="Apply Company"
        )

        db.session.add(
            company
        )

        db.session.flush()

        date = datetime(
            2026,
            8,
            10,
        )

        article_a = _create_article(
            title="Article A",
            url="https://example.com/apply-a",
            published_at=date,
        )

        article_b = _create_article(
            title="Article B",
            url="https://example.com/apply-b",
            published_at=(
                date
                + timedelta(days=1)
            ),
        )

        _create_round(
            company=company,
            article=article_a,
            announced_at=date,
        )

        _create_round(
            company=company,
            article=article_b,
            announced_at=(
                date
                + timedelta(days=1)
            ),
        )

        result = (
            reconcile_historical_funding_rounds(
                apply=True
            )
        )

        assert (
            FundingRound.query.count()
            == 1
        )

        surviving_round = (
            FundingRound.query.one()
        )

        assert len(
            surviving_round.articles
        ) == 2

        assert result["merged"] == 1

        assert (
            result[
                "remaining_candidates"
            ]
            == 0
        )

        db.session.rollback()


def test_apply_handles_overlapping_duplicate_cluster(
    app,
):
    """
    Three articles describing the same event should collapse
    safely into one canonical FundingRound.

    This specifically protects against stale candidate lists.
    """

    with app.app_context():
        company = Company(
            name="Cluster Company"
        )

        db.session.add(
            company
        )

        db.session.flush()

        date = datetime(
            2026,
            8,
            10,
        )

        for index in range(3):
            article = _create_article(
                title=(
                    f"Cluster article "
                    f"{index}"
                ),
                url=(
                    "https://example.com/"
                    f"cluster-{index}"
                ),
                published_at=(
                    date
                    + timedelta(
                        days=index
                    )
                ),
            )

            _create_round(
                company=company,
                article=article,
                announced_at=(
                    date
                    + timedelta(
                        days=index
                    )
                ),
            )

        candidates_before = (
            find_duplicate_funding_rounds()
        )

        assert len(
            candidates_before
        ) == 3

        result = (
            reconcile_historical_funding_rounds(
                apply=True
            )
        )

        assert (
            FundingRound.query.count()
            == 1
        )

        surviving_round = (
            FundingRound.query.one()
        )

        assert len(
            surviving_round.articles
        ) == 3

        assert result["merged"] == 2

        assert (
            result[
                "remaining_candidates"
            ]
            == 0
        )

        db.session.rollback()