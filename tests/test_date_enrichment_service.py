from datetime import datetime

import pytest

from models.article import (
    Article,
    db,
)

from services import (
    date_enrichment_service,
)

from services.date_enrichment_service import (
    run_date_enrichment,
)


def _persist_article(
    *,
    title,
    source,
    published_at=None,
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
        content="Stored evidence.",
        category="Funding Round",
        published_at=published_at,
    )

    db.session.add(
        article
    )

    db.session.flush()

    return article


def test_date_enrichment_reports_recovery(
    app,
    monkeypatch,
):
    with app.app_context():
        first = _persist_article(
            title="First undated",
            source="Andreessen Horowitz",
        )

        second = _persist_article(
            title="Second undated",
            source="Andreessen Horowitz",
        )

        _persist_article(
            title="Already dated",
            source="Andreessen Horowitz",
            published_at=datetime(
                2026,
                8,
                1,
            ),
        )

        db.session.commit()

        def fake_populate(
            source=None,
            limit=100,
        ):
            assert (
                source
                == "Andreessen Horowitz"
            )

            assert limit == 20

            first.published_at = datetime(
                2026,
                7,
                1,
            )

            second.published_at = datetime(
                2026,
                7,
                2,
            )

            return 2

        monkeypatch.setattr(
            date_enrichment_service,
            "populate_missing_article_dates",
            fake_populate,
        )

        result = run_date_enrichment(
            source_name=(
                "Andreessen Horowitz"
            ),
            limit=20,
        )

        assert result == {
            "source":
                "Andreessen Horowitz",

            "source_key":
                "a16z",

            "limit":
                20,

            "undated_before":
                2,

            "attempted":
                2,

            "dates_recovered":
                2,

            "remaining_undated":
                0,

            "recovery_rate":
                100.0,
        }


def test_date_enrichment_measures_partial_recovery(
    app,
    monkeypatch,
):
    with app.app_context():
        first = _persist_article(
            title="Recoverable evidence",
            source="Andreessen Horowitz",
        )

        _persist_article(
            title="Still undated",
            source="Andreessen Horowitz",
        )

        db.session.commit()

        def fake_populate(
            source=None,
            limit=100,
        ):
            first.published_at = datetime(
                2026,
                7,
                1,
            )

            return 1

        monkeypatch.setattr(
            date_enrichment_service,
            "populate_missing_article_dates",
            fake_populate,
        )

        result = run_date_enrichment(
            source_name=(
                "Andreessen Horowitz"
            ),
            limit=20,
        )

        assert (
            result[
                "attempted"
            ]
            == 2
        )

        assert (
            result[
                "dates_recovered"
            ]
            == 1
        )

        assert (
            result[
                "remaining_undated"
            ]
            == 1
        )

        assert (
            result[
                "recovery_rate"
            ]
            == 50.0
        )


def test_date_enrichment_respects_limit(
    app,
    monkeypatch,
):
    with app.app_context():
        for index in range(
            5
        ):
            _persist_article(
                title=(
                    f"Undated {index}"
                ),
                source=(
                    "Andreessen Horowitz"
                ),
            )

        db.session.commit()

        captured = {}

        def fake_populate(
            source=None,
            limit=100,
        ):
            captured[
                "source"
            ] = source

            captured[
                "limit"
            ] = limit

            return 0

        monkeypatch.setattr(
            date_enrichment_service,
            "populate_missing_article_dates",
            fake_populate,
        )

        result = run_date_enrichment(
            source_name=(
                "Andreessen Horowitz"
            ),
            limit=2,
        )

        assert captured == {
            "source":
                "Andreessen Horowitz",

            "limit":
                2,
        }

        assert (
            result[
                "undated_before"
            ]
            == 5
        )

        assert (
            result[
                "attempted"
            ]
            == 2
        )

        assert (
            result[
                "dates_recovered"
            ]
            == 0
        )

        assert (
            result[
                "remaining_undated"
            ]
            == 5
        )

        assert (
            result[
                "recovery_rate"
            ]
            == 0.0
        )


def test_date_enrichment_zero_limit_is_read_only(
    app,
    monkeypatch,
):
    with app.app_context():
        _persist_article(
            title="Undated evidence",
            source="Andreessen Horowitz",
        )

        db.session.commit()

        called = {
            "value":
                False,
        }

        def fake_populate(
            source=None,
            limit=100,
        ):
            called[
                "value"
            ] = True

            return 0

        monkeypatch.setattr(
            date_enrichment_service,
            "populate_missing_article_dates",
            fake_populate,
        )

        result = run_date_enrichment(
            source_name=(
                "Andreessen Horowitz"
            ),
            limit=0,
        )

        assert (
            called[
                "value"
            ]
            is False
        )

        assert (
            result[
                "attempted"
            ]
            == 0
        )

        assert (
            result[
                "remaining_undated"
            ]
            == 1
        )


def test_date_enrichment_accepts_source_key(
    app,
    monkeypatch,
):
    with app.app_context():
        _persist_article(
            title="Undated evidence",
            source="Andreessen Horowitz",
        )

        db.session.commit()

        captured = {}

        def fake_populate(
            source=None,
            limit=100,
        ):
            captured[
                "source"
            ] = source

            return 0

        monkeypatch.setattr(
            date_enrichment_service,
            "populate_missing_article_dates",
            fake_populate,
        )

        result = run_date_enrichment(
            source_name="a16z",
            limit=1,
        )

        assert (
            captured[
                "source"
            ]
            == "Andreessen Horowitz"
        )

        assert (
            result[
                "source"
            ]
            == "Andreessen Horowitz"
        )

        assert (
            result[
                "source_key"
            ]
            == "a16z"
        )


def test_date_enrichment_unknown_source_fails_cleanly(
    app,
):
    with app.app_context():
        with pytest.raises(
            ValueError,
            match="Unknown source",
        ):
            run_date_enrichment(
                source_name=(
                    "Imaginary Capital"
                ),
                limit=20,
            )


def test_date_enrichment_rejects_negative_limit(
    app,
):
    with app.app_context():
        with pytest.raises(
            ValueError,
            match=(
                "limit cannot be negative"
            ),
        ):
            run_date_enrichment(
                source_name=(
                    "Andreessen Horowitz"
                ),
                limit=-1,
            )


def test_date_enrichment_rolls_back_on_failure(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            title="Rollback evidence",
            source="Andreessen Horowitz",
        )

        db.session.commit()

        def fake_populate(
            source=None,
            limit=100,
        ):
            article.published_at = (
                datetime(
                    2026,
                    7,
                    1,
                )
            )

            raise RuntimeError(
                "page enrichment failed"
            )

        monkeypatch.setattr(
            date_enrichment_service,
            "populate_missing_article_dates",
            fake_populate,
        )

        with pytest.raises(
            RuntimeError,
            match=(
                "page enrichment failed"
            ),
        ):
            run_date_enrichment(
                source_name=(
                    "Andreessen Horowitz"
                ),
                limit=20,
            )

        refreshed = db.session.get(
            Article,
            article.id,
        )

        assert (
            refreshed.published_at
            is None
        )