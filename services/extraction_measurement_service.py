from collections import (
    Counter,
    defaultdict,
)

from models.extraction_record import (
    ExtractionRecord,
    VALIDATION_STATE_PENDING,
    VALIDATION_STATE_PROMOTE,
    VALIDATION_STATE_REVIEW,
    VALIDATION_STATE_REJECT,
)


KNOWN_VALIDATION_STATES = (
    VALIDATION_STATE_PENDING,
    VALIDATION_STATE_PROMOTE,
    VALIDATION_STATE_REVIEW,
    VALIDATION_STATE_REJECT,
)


def _percentage(
    numerator,
    denominator,
):
    """
    Return a percentage rounded to one decimal place.

    Empty populations return 0.0 rather than raising a
    division error.
    """

    if denominator == 0:
        return 0.0

    return round(
        (
            numerator
            / denominator
        )
        * 100,
        1,
    )


def _sorted_count_rows(
    counter,
    *,
    key_name,
):
    """
    Convert a Counter into deterministic report rows.

    Rows are ordered by:
    1. descending count
    2. ascending label

    This makes CLI output and tests stable.
    """

    return [
        {
            key_name: key,
            "count": count,
        }
        for key, count
        in sorted(
            counter.items(),
            key=lambda item: (
                -item[1],
                str(item[0]),
            ),
        )
    ]


def _build_validation_summary(
    records,
):
    """
    Count validation states and calculate their share of all
    extraction attempts.
    """

    total = len(
        records
    )

    state_counts = Counter(
        record.validation_state
        for record in records
    )

    summary = {}

    for state in KNOWN_VALIDATION_STATES:
        count = state_counts.get(
            state,
            0,
        )

        summary[state] = {
            "count": count,
            "percentage": _percentage(
                count,
                total,
            ),
        }

    unknown_count = sum(
        count
        for state, count
        in state_counts.items()
        if state
        not in KNOWN_VALIDATION_STATES
    )

    if unknown_count:
        summary[
            "unknown"
        ] = {
            "count": unknown_count,
            "percentage": _percentage(
                unknown_count,
                total,
            ),
        }

    return summary


def _build_promotion_summary(
    records,
):
    """
    Measure promotion state without overstating what the
    current schema can prove.

    A PROMOTE record with promoted_at=None is reported as
    "unpromoted_promote".

    That state may represent:
    - a failed canonical persistence attempt
    - canonicalization returning no canonical object
    - a record awaiting retry

    The current schema does not distinguish those outcomes, so
    this service deliberately does not call all such records
    "failures".
    """

    promote_records = [
        record
        for record in records
        if (
            record.validation_state
            == VALIDATION_STATE_PROMOTE
        )
    ]

    promoted_records = [
        record
        for record in promote_records
        if record.promoted_at is not None
    ]

    unpromoted_records = [
        record
        for record in promote_records
        if record.promoted_at is None
    ]

    promote_count = len(
        promote_records
    )

    promoted_count = len(
        promoted_records
    )

    unpromoted_count = len(
        unpromoted_records
    )

    return {
        "eligible_for_promotion":
            promote_count,

        "promoted":
            promoted_count,

        "unpromoted_promote":
            unpromoted_count,

        "promotion_rate": _percentage(
            promoted_count,
            promote_count,
        ),
    }


def _build_flag_counts(
    records,
):
    """
    Count deterministic validation flags.

    One ExtractionRecord may contribute more than one flag.
    """

    counter = Counter()

    for record in records:
        flags = (
            record.validation_flags
            or []
        )

        for flag in flags:
            counter[
                flag
            ] += 1

    return _sorted_count_rows(
        counter,
        key_name="flag",
    )


def _build_extractor_counts(
    records,
):
    """
    Count extraction attempts by extractor version.
    """

    counter = Counter(
        record.extractor_version
        for record in records
    )

    return _sorted_count_rows(
        counter,
        key_name="extractor_version",
    )


def _build_model_counts(
    records,
):
    """
    Count extraction attempts by underlying model.
    """

    counter = Counter(
        record.model
        for record in records
    )

    return _sorted_count_rows(
        counter,
        key_name="model",
    )


def _build_event_type_counts(
    records,
):
    """
    Count extraction attempts by structured event type.
    """

    counter = Counter(
        record.event_type
        for record in records
    )

    return _sorted_count_rows(
        counter,
        key_name="event_type",
    )


def _build_source_summary(
    records,
):
    """
    Build per-source extraction quality measurements.

    The source comes from the underlying Article evidence
    record.

    Each source row includes:
    - extraction attempts
    - validation outcomes
    - successful promotions
    - unpromoted PROMOTE records
    - promotion rate among PROMOTE records
    """

    grouped = defaultdict(
        list
    )

    for record in records:
        article = record.article

        source = (
            article.source
            if (
                article is not None
                and article.source
            )
            else "unknown"
        )

        grouped[
            source
        ].append(
            record
        )

    rows = []

    for source, source_records in grouped.items():
        validation = (
            _build_validation_summary(
                source_records
            )
        )

        promotion = (
            _build_promotion_summary(
                source_records
            )
        )

        rows.append(
            {
                "source": source,

                "attempts":
                    len(
                        source_records
                    ),

                "promote":
                    validation[
                        VALIDATION_STATE_PROMOTE
                    ][
                        "count"
                    ],

                "review":
                    validation[
                        VALIDATION_STATE_REVIEW
                    ][
                        "count"
                    ],

                "reject":
                    validation[
                        VALIDATION_STATE_REJECT
                    ][
                        "count"
                    ],

                "pending":
                    validation[
                        VALIDATION_STATE_PENDING
                    ][
                        "count"
                    ],

                "promoted":
                    promotion[
                        "promoted"
                    ],

                "unpromoted_promote":
                    promotion[
                        "unpromoted_promote"
                    ],

                "promotion_rate":
                    promotion[
                        "promotion_rate"
                    ],
            }
        )

    return sorted(
        rows,
        key=lambda row: (
            -row[
                "attempts"
            ],
            row[
                "source"
            ],
        ),
    )


def _build_replay_summary(
    records,
):
    """
    Infer replay volume from append-only extraction history.

    The first ExtractionRecord for an
    (article_id, event_type) pair is treated as the initial
    extraction.

    Every subsequent ExtractionRecord for the same pair is
    counted as a replay / reprocessing attempt.

    This is intentionally an inferred metric because the
    current schema does not yet store an explicit replay flag.
    """

    grouped = defaultdict(
        list
    )

    for record in records:
        key = (
            record.article_id,
            record.event_type,
        )

        grouped[
            key
        ].append(
            record
        )

    replay_attempts = 0
    replayed_evidence = 0

    for group_records in grouped.values():
        count = len(
            group_records
        )

        if count > 1:
            replayed_evidence += 1

            replay_attempts += (
                count
                - 1
            )

    return {
        "unique_evidence_event_pairs":
            len(
                grouped
            ),

        "replayed_evidence_event_pairs":
            replayed_evidence,

        "replay_attempts":
            replay_attempts,
    }


def get_extraction_measurements(
    *,
    source=None,
    event_type=None,
    extractor_version=None,
):
    """
    Return a structured measurement report for the Vantage
    knowledge pipeline.

    Optional filters:
    - source
    - event_type
    - extractor_version

    This service is read-only. It does not mutate extraction
    records or canonical knowledge.
    """

    query = (
        ExtractionRecord.query
        .join(
            ExtractionRecord.article
        )
    )

    if source is not None:
        query = query.filter(
            ExtractionRecord.article.has(
                source=source
            )
        )

    if event_type is not None:
        query = query.filter(
            ExtractionRecord.event_type
            == event_type
        )

    if extractor_version is not None:
        query = query.filter(
            ExtractionRecord.extractor_version
            == extractor_version
        )

    records = (
        query
        .order_by(
            ExtractionRecord.id.asc()
        )
        .all()
    )

    validation = (
        _build_validation_summary(
            records
        )
    )

    promotion = (
        _build_promotion_summary(
            records
        )
    )

    quarantine_count = (
        validation[
            VALIDATION_STATE_REVIEW
        ][
            "count"
        ]
        + validation[
            VALIDATION_STATE_REJECT
        ][
            "count"
        ]
    )

    return {
        "filters": {
            "source":
                source,

            "event_type":
                event_type,

            "extractor_version":
                extractor_version,
        },

        "extraction_attempts":
            len(
                records
            ),

        "validation":
            validation,

        "quarantined":
            {
                "count":
                    quarantine_count,

                "percentage":
                    _percentage(
                        quarantine_count,
                        len(
                            records
                        ),
                    ),
            },

        "promotion":
            promotion,

        "replay":
            _build_replay_summary(
                records
            ),

        "by_event_type":
            _build_event_type_counts(
                records
            ),

        "by_extractor_version":
            _build_extractor_counts(
                records
            ),

        "by_model":
            _build_model_counts(
                records
            ),

        "validation_flags":
            _build_flag_counts(
                records
            ),

        "by_source":
            _build_source_summary(
                records
            ),
    }