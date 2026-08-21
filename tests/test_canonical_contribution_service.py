from datetime import (
    datetime,
)

from models.article import (
    Article,
    db,
)

from models.company import (
    Company,
)

from models.funding_round import (
    FundingRound,
)

from services.canonical_contribution_service import (
    measure_canonical_funding_contribution,
)


def _article(
    *,
    title,
    source,
):
    article = Article(
        title=title,
        source=source,
        source_type="investor",
        discovery_method="html",
        url=(
            "https://example.com/"
            + title
            .lower()
            .replace(
                " ",
                "-",
            )
        ),
        content="Evidence.",
        category="Funding Round",
        published_at=datetime(
            2020,
            1,
            1,
        ),
    )

    db.session.add(
        article
    )

    db.session.flush()

    return article


def _company(
    name,
):
    company = Company(
        name=name
    )

    db.session.add(
        company
    )

    db.session.flush()

    return company


def _funding_round(
    *,
    company,
    primary_article,
    supporting_articles=None,
):
    funding_round = FundingRound(
        company=company,
        article=primary_article,
        event_evidence="Funding event.",
        amount=10_000_000,
        currency="USD",
        round_type="Series A",
        announced_at=(
            primary_article
            .published_at
        ),
    )

    db.session.add(
        funding_round
    )

    db.session.flush()

    for article in (
        supporting_articles
        or []
    ):
        funding_round.articles.append(
            article
        )

    db.session.flush()

    return funding_round


def test_single_source_event_is_unique(
    app,
):
    with app.app_context():
        article = _article(
            title="Unique evidence",
            source="Source A",
        )

        company = _company(
            "Unique Company"
        )

        _funding_round(
            company=company,
            primary_article=article,
            supporting_articles=[
                article,
            ],
        )

        result = (
            measure_canonical_funding_contribution(
                "Source A"
            )
        )

        assert (
            result[
                "supported_funding_events"
            ]
            == 1
        )

        assert (
            result[
                "unique_funding_events"
            ]
            == 1
        )

        assert (
            result[
                "multi_source_funding_events"
            ]
            == 0
        )

        assert (
            result[
                "funding_overlap_rate"
            ]
            == 0.0
        )

        db.session.rollback()


def test_multi_source_event_counts_as_overlap(
    app,
):
    with app.app_context():
        article_a = _article(
            title="Source A evidence",
            source="Source A",
        )

        article_b = _article(
            title="Source B evidence",
            source="Source B",
        )

        company = _company(
            "Shared Company"
        )

        _funding_round(
            company=company,
            primary_article=article_a,
            supporting_articles=[
                article_a,
                article_b,
            ],
        )

        result_a = (
            measure_canonical_funding_contribution(
                "Source A"
            )
        )

        result_b = (
            measure_canonical_funding_contribution(
                "Source B"
            )
        )

        for result in [
            result_a,
            result_b,
        ]:
            assert (
                result[
                    "supported_funding_events"
                ]
                == 1
            )

            assert (
                result[
                    "unique_funding_events"
                ]
                == 0
            )

            assert (
                result[
                    "multi_source_funding_events"
                ]
                == 1
            )

            assert (
                result[
                    "funding_overlap_rate"
                ]
                == 1.0
            )

        db.session.rollback()


def test_legacy_primary_article_relationship_is_counted(
    app,
):
    with app.app_context():
        article = _article(
            title="Legacy evidence",
            source="Legacy Source",
        )

        company = _company(
            "Legacy Company"
        )

        _funding_round(
            company=company,
            primary_article=article,
            supporting_articles=[],
        )

        result = (
            measure_canonical_funding_contribution(
                "Legacy Source"
            )
        )

        assert (
            result[
                "supported_funding_events"
            ]
            == 1
        )

        assert (
            result[
                "unique_funding_events"
            ]
            == 1
        )

        db.session.rollback()