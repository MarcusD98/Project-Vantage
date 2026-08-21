from collections import (
    Counter,
)

from datetime import (
    timezone,
)

from source_registry import (
    SOURCE_REGISTRY,
)

from models.article import (
    Article,
)

from models.extraction_record import (
    ExtractionRecord,
    VALIDATION_STATE_PENDING,
    VALIDATION_STATE_PROMOTE,
    VALIDATION_STATE_REVIEW,
    VALIDATION_STATE_REJECT,
)

from services.canonical_contribution_service import (
    measure_canonical_funding_contribution,
)


HISTORICAL_TARGET_MINIMUM_DAYS = 365
HISTORICAL_TARGET_STRONG_DAYS = 730


def _normalize_datetime(
    value,
):
    """
    Normalize database datetimes to timezone-aware UTC for
    comparison.

    SQLite commonly returns timezone-naive values.
    """

    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc
        )

    return value.astimezone(
        timezone.utc
    )


def _percentage(
    numerator,
    denominator,
):
    """
    Return a percentage rounded to one decimal place.
    """

    if not denominator:
        return 0.0

    return round(
        (
            numerator
            / denominator
        )
        * 100,
        1,
    )


def _historical_coverage_status(
    coverage_days,
):
    """
    Classify observed historical coverage relative to the
    Phase 8 target.

    This describes the discovered Vantage corpus only.

    It must not be interpreted as complete knowledge of all
    real-world activity.
    """

    if coverage_days is None:
        return "no_dated_evidence"

    if (
        coverage_days
        >= HISTORICAL_TARGET_STRONG_DAYS
    ):
        return "24m_plus"

    if (
        coverage_days
        >= HISTORICAL_TARGET_MINIMUM_DAYS
    ):
        return "12m_plus"

    return "under_12m"


def _source_articles(
    source_name,
):
    """
    Return all persisted evidence for one source.
    """

    return (
        Article.query
        .filter_by(
            source=source_name
        )
        .all()
    )


def _source_extraction_records(
    source_name,
):
    """
    Return all ExtractionRecords whose underlying evidence
    belongs to one source.
    """

    return (
        ExtractionRecord.query
        .join(
            ExtractionRecord.article
        )
        .filter(
            Article.source
            == source_name
        )
        .all()
    )


def _date_coverage(
    articles,
):
    """
    Measure the observed publication-date span of one source.

    Coverage is the span between the oldest and newest dated
    evidence documents discovered by Vantage.

    It is not a claim of continuous or complete coverage
    inside that period.
    """

    dates = [
        _normalize_datetime(
            article.published_at
        )
        for article in articles
        if article.published_at
        is not None
    ]

    if not dates:
        return {
            "dated_evidence": 0,

            "undated_evidence":
                len(
                    articles
                ),

            "oldest_evidence_at":
                None,

            "newest_evidence_at":
                None,

            "coverage_days":
                None,

            "coverage_status":
                "no_dated_evidence",
        }

    oldest = min(
        dates
    )

    newest = max(
        dates
    )

    coverage_days = (
        newest
        - oldest
    ).days

    return {
        "dated_evidence":
            len(
                dates
            ),

        "undated_evidence":
            (
                len(
                    articles
                )
                - len(
                    dates
                )
            ),

        "oldest_evidence_at":
            oldest,

        "newest_evidence_at":
            newest,

        "coverage_days":
            coverage_days,

        "coverage_status":
            _historical_coverage_status(
                coverage_days
            ),
    }


def _extraction_summary(
    records,
):
    """
    Measure extraction and validation quality for one source.
    """

    state_counts = Counter(
        record.validation_state
        for record in records
    )

    promoted = sum(
        1
        for record in records
        if record.promoted_at
        is not None
    )

    attempts = len(
        records
    )

    promote_count = (
        state_counts.get(
            VALIDATION_STATE_PROMOTE,
            0,
        )
    )

    review_count = (
        state_counts.get(
            VALIDATION_STATE_REVIEW,
            0,
        )
    )

    reject_count = (
        state_counts.get(
            VALIDATION_STATE_REJECT,
            0,
        )
    )

    pending_count = (
        state_counts.get(
            VALIDATION_STATE_PENDING,
            0,
        )
    )

    quarantine_count = (
        review_count
        + reject_count
    )

    return {
        "extraction_attempts":
            attempts,

        "promote":
            promote_count,

        "review":
            review_count,

        "reject":
            reject_count,

        "pending":
            pending_count,

        "promoted":
            promoted,

        "promotion_rate":
            _percentage(
                promoted,
                promote_count,
            ),

        "quarantine_rate":
            _percentage(
                quarantine_count,
                attempts,
            ),
    }


def measure_observation_source(
    source,
    now=None,
):
    """
    Build one Phase 8 observation-scale measurement row.

    The row combines:

    - source registry capability
    - persisted evidence coverage
    - historical span
    - ExtractionRecord quality
    - canonical funding knowledge supported by the full
      observed source corpus

    Canonical contribution deliberately ignores current
    publication-recency policy.

    Phase 8 asks what Vantage has learned from the observed
    corpus, not merely what belongs to the current operating
    window.

    The now argument is retained for API compatibility.
    """

    source_name = (
        source[
            "name"
        ]
    )

    discovery = source.get(
        "discovery",
        {},
    )

    incremental_capable = (
        "incremental"
        in discovery
    )

    historical_capable = (
        "historical"
        in discovery
    )

    articles = (
        _source_articles(
            source_name
        )
    )

    extraction_records = (
        _source_extraction_records(
            source_name
        )
    )

    coverage = (
        _date_coverage(
            articles
        )
    )

    extraction = (
        _extraction_summary(
            extraction_records
        )
    )

    contribution = (
        measure_canonical_funding_contribution(
            source_name
        )
    )

    return {
        "key":
            source[
                "key"
            ],

        "name":
            source_name,

        "source_type":
            source[
                "type"
            ],

        "region":
            source[
                "region"
            ],

        "enabled":
            source[
                "enabled"
            ],

        "incremental_capable":
            incremental_capable,

        "historical_capable":
            historical_capable,

        "incremental_method":
            (
                discovery
                .get(
                    "incremental",
                    {},
                )
                .get(
                    "method"
                )
            ),

        "historical_method":
            (
                discovery
                .get(
                    "historical",
                    {},
                )
                .get(
                    "method"
                )
            ),

        "stored_evidence":
            len(
                articles
            ),

        **coverage,

        **extraction,

        "supported_funding_events":
            contribution[
                "supported_funding_events"
            ],

        "unique_funding_events":
            contribution[
                "unique_funding_events"
            ],

        "multi_source_funding_events":
            contribution[
                "multi_source_funding_events"
            ],

        "funding_overlap_rate":
            contribution[
                "funding_overlap_rate"
            ],
    }


def get_observation_scale_report(
    *,
    enabled_only=True,
    source_type=None,
    now=None,
):
    """
    Measure the current Vantage observation network.

    This report describes:

    - source-network capability
    - observed corpus scale
    - historical span
    - extraction quality
    - canonical knowledge contribution across the full
      observed corpus

    Optional filters:

    - enabled_only
    - source_type
    """

    sources = []

    for source in SOURCE_REGISTRY:
        if (
            enabled_only
            and not source[
                "enabled"
            ]
        ):
            continue

        if (
            source_type is not None
            and source[
                "type"
            ]
            != source_type
        ):
            continue

        sources.append(
            source
        )

    rows = [
        measure_observation_source(
            source,
            now=now,
        )
        for source in sources
    ]

    rows = sorted(
        rows,
        key=lambda row: (
            row[
                "source_type"
            ],
            row[
                "name"
            ],
        ),
    )

    type_counts = Counter(
        row[
            "source_type"
        ]
        for row in rows
    )

    historical_capable = sum(
        1
        for row in rows
        if row[
            "historical_capable"
        ]
    )

    incremental_capable = sum(
        1
        for row in rows
        if row[
            "incremental_capable"
        ]
    )

    sources_with_evidence = sum(
        1
        for row in rows
        if row[
            "stored_evidence"
        ]
        > 0
    )

    sources_with_12m = sum(
        1
        for row in rows
        if row[
            "coverage_status"
        ]
        in {
            "12m_plus",
            "24m_plus",
        }
    )

    sources_with_24m = sum(
        1
        for row in rows
        if row[
            "coverage_status"
        ]
        == "24m_plus"
    )

    total_evidence = sum(
        row[
            "stored_evidence"
        ]
        for row in rows
    )

    total_extractions = sum(
        row[
            "extraction_attempts"
        ]
        for row in rows
    )

    total_promoted = sum(
        row[
            "promoted"
        ]
        for row in rows
    )

    total_unique_events = sum(
        row[
            "unique_funding_events"
        ]
        for row in rows
    )

    return {
        "filters": {
            "enabled_only":
                enabled_only,

            "source_type":
                source_type,
        },

        "summary": {
            "sources":
                len(
                    rows
                ),

            "incremental_capable":
                incremental_capable,

            "historical_capable":
                historical_capable,

            "historical_capability_rate":
                _percentage(
                    historical_capable,
                    len(
                        rows
                    ),
                ),

            "sources_with_evidence":
                sources_with_evidence,

            "sources_with_12m_coverage":
                sources_with_12m,

            "sources_with_24m_coverage":
                sources_with_24m,

            "stored_evidence":
                total_evidence,

            "extraction_attempts":
                total_extractions,

            "promoted_extractions":
                total_promoted,

            "unique_funding_events":
                total_unique_events,
        },

        "by_source_type": [
            {
                "source_type":
                    source_type_name,

                "count":
                    count,
            }
            for (
                source_type_name,
                count,
            )
            in sorted(
                type_counts.items()
            )
        ],

        "sources":
            rows,
    }