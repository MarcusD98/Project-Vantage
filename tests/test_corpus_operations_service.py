from datetime import (
    datetime,
    timezone,
)

import pytest

from models.article import (
    Article,
    db,
)

from services.corpus_operations_service import (
    _get_live_source,
    _select_stored_articles,
    _validate_source,
)


def _candidate_stats():
    return {
        "stale_articles_skipped":
            0,

        "compound_articles_skipped":
            0,

        "content_retrieved":
            0,

        "content_failed":
            0,
    }


def test_get_live_source():
    source = (
        _get_live_source(
            "TechCrunch"
        )
    )

    assert source is not None

    assert (
        source["name"]
        == "TechCrunch"
    )


def test_get_unknown_live_source():
    source = (
        _get_live_source(
            "Not Real"
        )
    )

    assert source is None


def test_validate_source():
    source = (
        _validate_source(
            "TechCrunch"
        )
    )

    assert (
        source["name"]
        == "TechCrunch"
    )


def test_validate_unknown_source_raises():
    with pytest.raises(
        ValueError
    ):
        _validate_source(
            "Not Real"
        )


def test_zero_limit_selects_no_articles():
    result = (
        _select_stored_articles(
            source_name="TechCrunch",
            category="Funding Round",
            limit=0,
            stats={},
            now=None,
        )
    )

    assert result == []


def test_negative_limit_selects_no_articles():
    result = (
        _select_stored_articles(
            source_name="TechCrunch",
            category="Funding Round",
            limit=-1,
            stats={},
            now=None,
        )
    )

    assert result == []


def test_current_processing_skips_stale_investor_evidence(
    app,
):
    article = Article(
        title=(
            "Example raises Series A"
        ),
        source="Accel",
        source_type="investor",
        discovery_method="sitemap",
        url=(
            "https://example.com/"
            "current-stale"
        ),
        published_at=datetime(
            2025,
            1,
            1,
        ),
        content=(
            "Example announced a "
            "Series A financing."
        ),
        category="Funding Round",
    )

    db.session.add(
        article
    )

    db.session.flush()

    stats = (
        _candidate_stats()
    )

    selected = (
        _select_stored_articles(
            source_name="Accel",
            category="Funding Round",
            limit=10,
            stats=stats,
            now=datetime(
                2026,
                8,
                20,
                tzinfo=timezone.utc,
            ),
            historical=False,
        )
    )

    assert selected == []

    assert (
        stats[
            "stale_articles_skipped"
        ]
        == 1
    )


def test_historical_processing_selects_same_stale_evidence(
    app,
):
    article = Article(
        title=(
            "Example raises Series A"
        ),
        source="Accel",
        source_type="investor",
        discovery_method="sitemap",
        url=(
            "https://example.com/"
            "historical-stale"
        ),
        published_at=datetime(
            2025,
            1,
            1,
        ),
        content=(
            "Example announced a "
            "Series A financing."
        ),
        category="Funding Round",
    )

    db.session.add(
        article
    )

    db.session.flush()

    stats = (
        _candidate_stats()
    )

    selected = (
        _select_stored_articles(
            source_name="Accel",
            category="Funding Round",
            limit=10,
            stats=stats,
            now=datetime(
                2026,
                8,
                20,
                tzinfo=timezone.utc,
            ),
            historical=True,
        )
    )

    assert len(
        selected
    ) == 1

    assert (
        selected[0].id
        == article.id
    )

    assert (
        stats[
            "stale_articles_skipped"
        ]
        == 0
    )