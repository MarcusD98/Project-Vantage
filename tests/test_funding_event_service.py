from datetime import datetime

from models.article import (
    Article,
    db,
)

from models.company import Company
from models.funding_round import FundingRound

from services.funding_event_service import (
    get_funding_event_detail,
)


def _article(
    *,
    title,
    source,
    url,
    published_at,
):
    return Article(
        title=title,
        source=source,
        source_type="publication",
        discovery_method="rss",
        url=url,
        published_at=published_at,
        category="Funding Round",
    )


def test_event_detail_returns_all_unique_evidence(
    app,
):
    with app.app_context():
        company = Company(
            name="Example"
        )

        primary = _article(
            title="Example raises $10M",
            source="Source A",
            url="https://example.com/a",
            published_at=datetime(
                2026,
                8,
                20,
                10,
                0,
            ),
        )

        supporting = _article(
            title="Example funding announced",
            source="Source B",
            url="https://example.com/b",
            published_at=datetime(
                2026,
                8,
                20,
                11,
                0,
            ),
        )

        funding_round = FundingRound(
            company=company,
            amount=10_000_000,
            currency="USD",
            round_type="Seed",
            canonical_round_type="Seed",
            announced_at=datetime(
                2026,
                8,
                20,
            ),
            event_evidence=(
                "Example raised $10 million."
            ),
            article=primary,
        )

        funding_round.articles.extend(
            [
                primary,
                supporting,
            ]
        )

        db.session.add_all(
            [
                company,
                primary,
                supporting,
                funding_round,
            ]
        )

        db.session.commit()

        result = (
            get_funding_event_detail(
                funding_round.id
            )
        )

        assert result is not None

        assert (
            result["funding_round"].id
            == funding_round.id
        )

        assert (
            result["evidence_count"]
            == 2
        )

        assert {
            item[
                "article"
            ].source
            for item
            in result["evidence"]
        } == {
            "Source A",
            "Source B",
        }

        primary_rows = [
            item
            for item
            in result["evidence"]
            if item["is_primary"]
        ]

        assert (
            len(primary_rows)
            == 1
        )

        assert (
            primary_rows[0][
                "article"
            ].id
            == primary.id
        )


def test_missing_event_returns_none(
    app,
):
    with app.app_context():
        assert (
            get_funding_event_detail(
                999999
            )
            is None
        )
