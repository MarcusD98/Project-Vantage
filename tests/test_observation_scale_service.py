from datetime import (
    datetime,
    timedelta,
    timezone,
)

from pydantic import BaseModel

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

from models.extraction_record import (
    EVENT_TYPE_FUNDING_ROUND,
    VALIDATION_STATE_PROMOTE,
    VALIDATION_STATE_REVIEW,
)

from services.extraction_record_service import (
    create_extraction_record,
)

from services.observation_scale_service import (
    _date_coverage,
    _historical_coverage_status,
    _extraction_summary,
    get_observation_scale_report,
)


class _Extraction(BaseModel):
    is_funding_round: bool = True
    event_evidence: str | None = "Evidence"
    company_name: str | None = "Example"


def _article(
    *,
    title,
    source,
    published_at=None,
):
    article = Article(
        title=title,
        source=source,
        source_type="investor",
        discovery_method="sitemap",
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
        published_at=published_at,
    )

    db.session.add(
        article
    )

    db.session.flush()

    return article


def _record(
    *,
    article,
    validation_state,
    promoted=False,
):
    record = (
        create_extraction_record(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
            extraction=_Extraction(),
            extractor_version="funding-v1",
            model="test-model",
        )
    )

    record.validation_state = (
        validation_state
    )

    if promoted:
        record.promoted_at = (
            datetime(
                2026,
                8,
                21,
                12,
                0,
            )
        )

    db.session.flush()

    return record


def test_historical_coverage_status():
    assert (
        _historical_coverage_status(
            None
        )
        == "no_dated_evidence"
    )

    assert (
        _historical_coverage_status(
            200
        )
        == "under_12m"
    )

    assert (
        _historical_coverage_status(
            365
        )
        == "12m_plus"
    )

    assert (
        _historical_coverage_status(
            730
        )
        == "24m_plus"
    )


def test_date_coverage_measures_observed_span(
    app,
):
    with app.app_context():
        start = datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        )

        end = (
            start
            + timedelta(
                days=400
            )
        )

        articles = [
            _article(
                title="Old evidence",
                source="Test Source",
                published_at=start,
            ),

            _article(
                title="New evidence",
                source="Test Source",
                published_at=end,
            ),

            _article(
                title="Undated evidence",
                source="Test Source",
                published_at=None,
            ),
        ]

        coverage = (
            _date_coverage(
                articles
            )
        )

        assert (
            coverage[
                "dated_evidence"
            ]
            == 2
        )

        assert (
            coverage[
                "undated_evidence"
            ]
            == 1
        )

        assert (
            coverage[
                "coverage_days"
            ]
            == 400
        )

        assert (
            coverage[
                "coverage_status"
            ]
            == "12m_plus"
        )


def test_date_coverage_handles_no_dates(
    app,
):
    with app.app_context():
        articles = [
            _article(
                title="Unknown date",
                source="Test Source",
            )
        ]

        coverage = (
            _date_coverage(
                articles
            )
        )

        assert (
            coverage[
                "coverage_days"
            ]
            is None
        )

        assert (
            coverage[
                "coverage_status"
            ]
            == "no_dated_evidence"
        )


def test_extraction_summary_measures_quality(
    app,
):
    with app.app_context():
        article = _article(
            title="Extraction evidence",
            source="Test Source",
        )

        records = [
            _record(
                article=article,
                validation_state=(
                    VALIDATION_STATE_PROMOTE
                ),
                promoted=True,
            ),

            _record(
                article=article,
                validation_state=(
                    VALIDATION_STATE_REVIEW
                ),
            ),
        ]

        summary = (
            _extraction_summary(
                records
            )
        )

        assert (
            summary[
                "extraction_attempts"
            ]
            == 2
        )

        assert (
            summary[
                "promote"
            ]
            == 1
        )

        assert (
            summary[
                "review"
            ]
            == 1
        )

        assert (
            summary[
                "promoted"
            ]
            == 1
        )

        assert (
            summary[
                "promotion_rate"
            ]
            == 100.0
        )

        assert (
            summary[
                "quarantine_rate"
            ]
            == 50.0
        )


def test_observation_report_describes_registry_baseline(
    app,
):
    with app.app_context():
        report = (
            get_observation_scale_report()
        )

        summary = report[
            "summary"
        ]

        assert (
            summary[
                "sources"
            ]
            > 0
        )

        assert (
            summary[
                "incremental_capable"
            ]
            > 0
        )

        assert (
            summary[
                "historical_capable"
            ]
            >= 1
        )

        assert (
            len(
                report[
                    "sources"
                ]
            )
            == summary[
                "sources"
            ]
        )


def test_observation_report_can_filter_investors(
    app,
):
    with app.app_context():
        report = (
            get_observation_scale_report(
                source_type="investor"
            )
        )

        assert (
            report[
                "summary"
            ][
                "sources"
            ]
            > 0
        )

        assert all(
            row[
                "source_type"
            ]
            == "investor"
            for row in report[
                "sources"
            ]
        )


def test_observation_report_excludes_disabled_sources_by_default(
    app,
):
    with app.app_context():
        enabled_report = (
            get_observation_scale_report()
        )

        all_report = (
            get_observation_scale_report(
                enabled_only=False
            )
        )

        assert (
            all_report[
                "summary"
            ][
                "sources"
            ]
            >= enabled_report[
                "summary"
            ][
                "sources"
            ]
        )

        assert all(
            row[
                "enabled"
            ]
            is True
            for row in enabled_report[
                "sources"
            ]
        )


def test_observation_report_counts_historical_canonical_events(
    app,
):
    """
    Phase 8 canonical contribution must not disappear merely
    because the supporting evidence is older than the source's
    incremental recency window.
    """

    with app.app_context():
        article = _article(
            title="Historical Greylock Event",
            source="Greylock",
            published_at=datetime(
                2020,
                1,
                1,
            ),
        )

        company = Company(
            name="Historical Greylock Company"
        )

        db.session.add(
            company
        )

        db.session.flush()

        funding_round = FundingRound(
            company=company,
            article=article,
            event_evidence=(
                "Historical funding event."
            ),
            amount=10_000_000,
            currency="USD",
            round_type="Series A",
            announced_at=(
                article.published_at
            ),
        )

        funding_round.articles.append(
            article
        )

        db.session.add(
            funding_round
        )

        db.session.flush()

        report = (
            get_observation_scale_report(
                source_type="investor",
                now=datetime(
                    2026,
                    8,
                    21,
                    tzinfo=timezone.utc,
                ),
            )
        )

        greylock = next(
            row
            for row in report[
                "sources"
            ]
            if row[
                "name"
            ]
            == "Greylock"
        )

        assert (
            greylock[
                "supported_funding_events"
            ]
            == 1
        )

        assert (
            greylock[
                "unique_funding_events"
            ]
            == 1
        )

        db.session.rollback()