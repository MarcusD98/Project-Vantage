from datetime import datetime

from pydantic import (
    BaseModel,
)

from models.article import (
    Article,
    db,
)

from models.extraction_record import (
    EVENT_TYPE_FUNDING_ROUND,
    EVENT_TYPE_FUND_CLOSE,
    VALIDATION_STATE_PROMOTE,
    VALIDATION_STATE_REVIEW,
    VALIDATION_STATE_REJECT,
)

from services.extraction_record_service import (
    create_extraction_record,
)

from services.extraction_measurement_service import (
    get_extraction_measurements,
)


class _Extraction(BaseModel):
    is_funding_round: bool = True

    event_evidence: str | None = (
        "Example evidence"
    )

    company_name: str | None = (
        "Example"
    )


def _persist_article(
    *,
    title,
    source,
):
    article = Article(
        title=title,
        source=source,
        source_type="publication",
        discovery_method="rss",
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
    )

    db.session.add(
        article
    )

    db.session.flush()

    return article


def _record(
    *,
    article,
    event_type=(
        EVENT_TYPE_FUNDING_ROUND
    ),
    extractor_version="funding-v1",
    model="model-a",
    validation_state=(
        VALIDATION_STATE_PROMOTE
    ),
    validation_flags=None,
    promoted=False,
):
    record = create_extraction_record(
        article=article,
        event_type=event_type,
        extraction=_Extraction(),
        extractor_version=(
            extractor_version
        ),
        model=model,
    )

    record.validation_state = (
        validation_state
    )

    record.validation_flags = (
        validation_flags
        or []
    )

    record.validator_version = (
        "deterministic-v1"
    )

    record.validated_at = datetime(
        2026,
        8,
        21,
        12,
        0,
    )

    if promoted:
        record.promoted_at = datetime(
            2026,
            8,
            21,
            12,
            1,
        )

    db.session.flush()

    return record


def test_empty_measurement_report(
    app,
):
    with app.app_context():
        report = (
            get_extraction_measurements()
        )

        assert (
            report[
                "extraction_attempts"
            ]
            == 0
        )

        assert (
            report[
                "validation"
            ][
                "promote"
            ][
                "count"
            ]
            == 0
        )

        assert (
            report[
                "promotion"
            ][
                "promoted"
            ]
            == 0
        )

        assert (
            report[
                "promotion"
            ][
                "promotion_rate"
            ]
            == 0.0
        )

        assert (
            report[
                "replay"
            ][
                "replay_attempts"
            ]
            == 0
        )


def test_measurement_counts_validation_outcomes(
    app,
):
    with app.app_context():
        article = _persist_article(
            title="Validation measurement",
            source="Source A",
        )

        _record(
            article=article,
            validation_state=(
                VALIDATION_STATE_PROMOTE
            ),
            promoted=True,
        )

        _record(
            article=article,
            validation_state=(
                VALIDATION_STATE_REVIEW
            ),
            validation_flags=[
                "missing_company_name",
            ],
        )

        _record(
            article=article,
            validation_state=(
                VALIDATION_STATE_REJECT
            ),
            validation_flags=[
                "not_funding_round",
            ],
        )

        db.session.commit()

        report = (
            get_extraction_measurements()
        )

        assert (
            report[
                "extraction_attempts"
            ]
            == 3
        )

        assert (
            report[
                "validation"
            ][
                "promote"
            ][
                "count"
            ]
            == 1
        )

        assert (
            report[
                "validation"
            ][
                "review"
            ][
                "count"
            ]
            == 1
        )

        assert (
            report[
                "validation"
            ][
                "reject"
            ][
                "count"
            ]
            == 1
        )

        assert (
            report[
                "quarantined"
            ][
                "count"
            ]
            == 2
        )

        assert (
            report[
                "quarantined"
            ][
                "percentage"
            ]
            == 66.7
        )


def test_measurement_distinguishes_promoted_and_unpromoted_promote(
    app,
):
    with app.app_context():
        article = _persist_article(
            title="Promotion measurement",
            source="Source A",
        )

        _record(
            article=article,
            validation_state=(
                VALIDATION_STATE_PROMOTE
            ),
            promoted=True,
        )

        _record(
            article=article,
            validation_state=(
                VALIDATION_STATE_PROMOTE
            ),
            promoted=False,
        )

        db.session.commit()

        report = (
            get_extraction_measurements()
        )

        promotion = report[
            "promotion"
        ]

        assert (
            promotion[
                "eligible_for_promotion"
            ]
            == 2
        )

        assert (
            promotion[
                "promoted"
            ]
            == 1
        )

        assert (
            promotion[
                "unpromoted_promote"
            ]
            == 1
        )

        assert (
            promotion[
                "promotion_rate"
            ]
            == 50.0
        )


def test_measurement_counts_validation_flags(
    app,
):
    with app.app_context():
        article = _persist_article(
            title="Flag measurement",
            source="Source A",
        )

        _record(
            article=article,
            validation_state=(
                VALIDATION_STATE_REVIEW
            ),
            validation_flags=[
                "missing_company_name",
                "invalid_currency",
            ],
        )

        _record(
            article=article,
            validation_state=(
                VALIDATION_STATE_REJECT
            ),
            validation_flags=[
                "missing_company_name",
                "not_funding_round",
            ],
        )

        db.session.commit()

        report = (
            get_extraction_measurements()
        )

        rows = report[
            "validation_flags"
        ]

        assert rows[
            0
        ] == {
            "flag":
                "missing_company_name",

            "count":
                2,
        }

        assert {
            row[
                "flag"
            ]:
                row[
                    "count"
                ]
            for row in rows
        } == {
            "missing_company_name":
                2,

            "invalid_currency":
                1,

            "not_funding_round":
                1,
        }


def test_measurement_groups_versions_models_and_event_types(
    app,
):
    with app.app_context():
        article = _persist_article(
            title="Version measurement",
            source="Source A",
        )

        _record(
            article=article,
            extractor_version=(
                "funding-v1"
            ),
            model="model-a",
        )

        _record(
            article=article,
            extractor_version=(
                "funding-v2"
            ),
            model="model-b",
        )

        _record(
            article=article,
            event_type=(
                EVENT_TYPE_FUND_CLOSE
            ),
            extractor_version=(
                "fund-close-v1"
            ),
            model="model-a",
        )

        db.session.commit()

        report = (
            get_extraction_measurements()
        )

        versions = {
            row[
                "extractor_version"
            ]:
                row[
                    "count"
                ]
            for row in report[
                "by_extractor_version"
            ]
        }

        models = {
            row[
                "model"
            ]:
                row[
                    "count"
                ]
            for row in report[
                "by_model"
            ]
        }

        event_types = {
            row[
                "event_type"
            ]:
                row[
                    "count"
                ]
            for row in report[
                "by_event_type"
            ]
        }

        assert versions == {
            "funding-v1":
                1,

            "funding-v2":
                1,

            "fund-close-v1":
                1,
        }

        assert models == {
            "model-a":
                2,

            "model-b":
                1,
        }

        assert event_types == {
            "funding_round":
                2,

            "fund_close":
                1,
        }


def test_measurement_infers_replay_from_append_only_history(
    app,
):
    with app.app_context():
        article = _persist_article(
            title="Replay measurement",
            source="Source A",
        )

        _record(
            article=article,
            extractor_version=(
                "funding-v1"
            ),
        )

        _record(
            article=article,
            extractor_version=(
                "funding-v2"
            ),
        )

        _record(
            article=article,
            extractor_version=(
                "funding-v3"
            ),
        )

        db.session.commit()

        report = (
            get_extraction_measurements()
        )

        replay = report[
            "replay"
        ]

        assert (
            replay[
                "unique_evidence_event_pairs"
            ]
            == 1
        )

        assert (
            replay[
                "replayed_evidence_event_pairs"
            ]
            == 1
        )

        assert (
            replay[
                "replay_attempts"
            ]
            == 2
        )


def test_measurement_builds_source_quality_summary(
    app,
):
    with app.app_context():
        source_a = _persist_article(
            title="Source A evidence",
            source="Source A",
        )

        source_b = _persist_article(
            title="Source B evidence",
            source="Source B",
        )

        _record(
            article=source_a,
            validation_state=(
                VALIDATION_STATE_PROMOTE
            ),
            promoted=True,
        )

        _record(
            article=source_a,
            validation_state=(
                VALIDATION_STATE_REVIEW
            ),
        )

        _record(
            article=source_b,
            validation_state=(
                VALIDATION_STATE_PROMOTE
            ),
            promoted=True,
        )

        db.session.commit()

        report = (
            get_extraction_measurements()
        )

        sources = {
            row[
                "source"
            ]:
                row
            for row in report[
                "by_source"
            ]
        }

        assert (
            sources[
                "Source A"
            ][
                "attempts"
            ]
            == 2
        )

        assert (
            sources[
                "Source A"
            ][
                "review"
            ]
            == 1
        )

        assert (
            sources[
                "Source A"
            ][
                "promoted"
            ]
            == 1
        )

        assert (
            sources[
                "Source B"
            ][
                "attempts"
            ]
            == 1
        )

        assert (
            sources[
                "Source B"
            ][
                "promotion_rate"
            ]
            == 100.0
        )


def test_measurement_filters_by_source_event_and_version(
    app,
):
    with app.app_context():
        source_a = _persist_article(
            title="Filtered evidence A",
            source="Source A",
        )

        source_b = _persist_article(
            title="Filtered evidence B",
            source="Source B",
        )

        _record(
            article=source_a,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
            extractor_version=(
                "funding-v2"
            ),
        )

        _record(
            article=source_a,
            event_type=(
                EVENT_TYPE_FUND_CLOSE
            ),
            extractor_version=(
                "fund-close-v1"
            ),
        )

        _record(
            article=source_b,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
            extractor_version=(
                "funding-v2"
            ),
        )

        db.session.commit()

        report = (
            get_extraction_measurements(
                source="Source A",
                event_type=(
                    EVENT_TYPE_FUNDING_ROUND
                ),
                extractor_version=(
                    "funding-v2"
                ),
            )
        )

        assert (
            report[
                "extraction_attempts"
            ]
            == 1
        )

        assert report[
            "filters"
        ] == {
            "source":
                "Source A",

            "event_type":
                "funding_round",

            "extractor_version":
                "funding-v2",
        }

        assert report[
            "by_source"
        ][
            0
        ][
            "source"
        ] == "Source A"