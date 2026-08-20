from datetime import (
    datetime,
    timedelta,
    timezone,
)

from types import SimpleNamespace

from services import (
    intelligence_pipeline,
)

from services.intelligence_pipeline import (
    _article_is_within_publication_window,
    _normalize_datetime,
    _prepare_candidate_article,
    _source_requires_publication_date,
)


def test_normalize_datetime_makes_naive_utc():
    value = datetime(
        2026,
        7,
        8,
        12,
        30,
    )

    result = _normalize_datetime(
        value
    )

    assert (
        result.tzinfo
        is not None
    )

    assert (
        result.utcoffset()
        == timedelta(0)
    )


def test_source_without_publication_rule_is_eligible():
    article = SimpleNamespace(
        source="TechCrunch",
        published_at=datetime(
            2020,
            1,
            1,
        ),
    )

    assert (
        _article_is_within_publication_window(
            article,
            now=datetime(
                2026,
                8,
                20,
                tzinfo=timezone.utc,
            ),
        )
    )


def test_recent_accel_article_is_eligible():
    article = SimpleNamespace(
        source="Accel",
        published_at=datetime(
            2026,
            7,
            8,
        ),
    )

    assert (
        _article_is_within_publication_window(
            article,
            now=datetime(
                2026,
                8,
                20,
                tzinfo=timezone.utc,
            ),
        )
    )


def test_stale_accel_article_is_not_eligible():
    article = SimpleNamespace(
        source="Accel",
        published_at=datetime(
            2025,
            4,
            2,
        ),
    )

    assert not (
        _article_is_within_publication_window(
            article,
            now=datetime(
                2026,
                8,
                20,
                tzinfo=timezone.utc,
            ),
        )
    )


def test_unknown_accel_date_remains_eligible():
    article = SimpleNamespace(
        source="Accel",
        published_at=None,
    )

    assert (
        _article_is_within_publication_window(
            article,
            now=datetime(
                2026,
                8,
                20,
                tzinfo=timezone.utc,
            ),
        )
    )


def test_accel_requires_publication_date():
    article = SimpleNamespace(
        source="Accel",
    )

    assert (
        _source_requires_publication_date(
            article
        )
    )


def test_publication_source_does_not_require_page_date():
    article = SimpleNamespace(
        source="TechCrunch",
    )

    assert not (
        _source_requires_publication_date(
            article
        )
    )


def test_prepare_candidate_enriches_and_rejects_stale(
    monkeypatch,
):
    article = SimpleNamespace(
        source="Accel",
        content=None,
        published_at=None,
    )

    stats = {
        "content_retrieved": 0,
        "stale_articles_skipped": 0,
    }

    def fake_populate(
        target_article,
    ):
        target_article.content = (
            "Useful article content"
        )

        target_article.published_at = (
            datetime(
                2025,
                4,
                2,
            )
        )

        return target_article.content

    monkeypatch.setattr(
        intelligence_pipeline,
        "populate_article_content",
        fake_populate,
    )

    result = _prepare_candidate_article(
        article,
        stats,
        now=datetime(
            2026,
            8,
            20,
            tzinfo=timezone.utc,
        ),
    )

    assert result is False

    assert (
        article.published_at
        == datetime(
            2025,
            4,
            2,
        )
    )

    assert (
        stats[
            "content_retrieved"
        ]
        == 1
    )

    assert (
        stats[
            "stale_articles_skipped"
        ]
        == 1
    )


def test_prepare_candidate_accepts_recent_article(
    monkeypatch,
):
    article = SimpleNamespace(
        source="Accel",
        content=None,
        published_at=None,
    )

    stats = {
        "content_retrieved": 0,
        "stale_articles_skipped": 0,
    }

    def fake_populate(
        target_article,
    ):
        target_article.content = (
            "Useful article content"
        )

        target_article.published_at = (
            datetime(
                2026,
                7,
                8,
            )
        )

        return target_article.content

    monkeypatch.setattr(
        intelligence_pipeline,
        "populate_article_content",
        fake_populate,
    )

    result = _prepare_candidate_article(
        article,
        stats,
        now=datetime(
            2026,
            8,
            20,
            tzinfo=timezone.utc,
        ),
    )

    assert result is True

    assert (
        stats[
            "content_retrieved"
        ]
        == 1
    )

    assert (
        stats[
            "stale_articles_skipped"
        ]
        == 0
    )