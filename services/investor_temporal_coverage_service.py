from datetime import timezone

from models.article import Article
from models.source_run import SourceRun

from services.compound_evidence_service import (
    is_compound_funding_evidence,
)

from source_registry import (
    get_discovery_config,
    get_source,
)


COMPLETED_DISCOVERY_STATUSES = {
    "success",
    "warning",
    "partial",
}


def _normalize_datetime(value):
    """
    Normalize datetimes to naive UTC to match the existing
    Vantage SQLite datetime convention.
    """

    if value is None:
        return None

    if value.tzinfo is not None:
        return (
            value.astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

    return value


def _latest_historical_run(source_name):
    """
    Return the latest historical source operation whose
    discovery phase completed.

    A partial run still counts as completed discovery because
    the partial status is used when discovery succeeded but
    optional intelligence processing later raised an error.
    """

    return (
        SourceRun.query
        .filter(
            SourceRun.source_name
            == source_name,

            SourceRun.mode
            == "historical",

            SourceRun.status.in_(
                COMPLETED_DISCOVERY_STATUSES
            ),
        )
        .order_by(
            SourceRun.started_at.desc(),
            SourceRun.id.desc(),
        )
        .first()
    )


def _remaining_undated_funding_evidence(
    source_name,
):
    """
    Count undated first-party evidence that could affect
    funding-activity comparison windows.

    Undated evidence outside the Funding Round category does
    not affect funding-activity comparability.
    """

    return (
        Article.query
        .filter(
            Article.source
            == source_name,

            Article.category
            == "Funding Round",

            Article.published_at
            .is_(None),
        )
        .count()
    )


def _window_candidate_coverage(
    source_name,
    start,
    end,
    include_end=False,
):
    """
    Measure processing completeness for discovered first-party
    Funding Round candidates in one analytical time window.

    Compound funding evidence is excluded because Vantage
    deliberately does not send it through the single-event
    extractor.
    """

    start = _normalize_datetime(
        start
    )

    end = _normalize_datetime(
        end
    )

    query = (
        Article.query
        .filter(
            Article.source
            == source_name,

            Article.category
            == "Funding Round",

            Article.published_at
            >= start,
        )
    )

    if include_end:
        query = query.filter(
            Article.published_at
            <= end
        )

    else:
        query = query.filter(
            Article.published_at
            < end
        )

    articles = query.all()

    eligible = [
        article
        for article in articles
        if not is_compound_funding_evidence(
            article
        )
    ]

    total = len(
        eligible
    )

    processed = sum(
        1
        for article in eligible
        if article.llm_processed_at
        is not None
    )

    backlog = (
        total
        - processed
    )

    ratio = (
        processed / total
        if total
        else 0.0
    )

    if total == 0:
        status = "empty"

    elif backlog == 0:
        status = "complete"

    else:
        status = "incomplete"

    return {
        "start":
            start,

        "end":
            end,

        "total_candidates":
            total,

        "processed_candidates":
            processed,

        "backlog":
            backlog,

        "processed_ratio":
            ratio,

        "processed_percent":
            ratio * 100,

        "status":
            status,
    }


def _unavailable_result(
    investor_name,
    reason,
    source_name=None,
):
    return {
        "investor_name":
            investor_name,

        "source_name":
            source_name,

        "source_matched":
            source_name is not None,

        "historical_strategy":
            False,

        "historical_run_id":
            None,

        "historical_run_status":
            None,

        "remaining_undated":
            None,

        "remaining_undated_funding":
            None,

        "current_window":
            None,

        "previous_window":
            None,

        "status":
            "unavailable",

        "reason":
            reason,
    }


def get_temporal_corpus_coverage(
    investor_name,
    current_start,
    current_end,
    previous_start,
    previous_end,
):
    """
    Measure whether Vantage has a matched, reconstructed
    first-party corpus across both activity-comparison windows.

    "complete" means:

    - the investor has a matching enabled first-party source;
    - that source has incremental and historical discovery;
    - a historical discovery run completed;
    - no undated Funding Round evidence remains;
    - each comparison window contains at least one discovered,
      non-compound Funding Round candidate; and
    - every such candidate in both windows has been processed.

    This deliberately measures completeness of the discovered
    Vantage corpus, not completeness of the investor's real-world
    investment activity.

    Undated evidence outside the Funding Round category is
    retained as an overall source-quality measurement but does
    not block funding-activity comparability.
    """

    source = get_source(
        investor_name
    )

    if (
        source is None
        or source.get("type")
        != "investor"
        or not source.get(
            "enabled",
            False,
        )
    ):
        return _unavailable_result(
            investor_name=investor_name,
            reason=(
                "No matched enabled first-party investor "
                "source is configured."
            ),
        )

    source_name = source[
        "name"
    ]

    incremental = (
        get_discovery_config(
            source[
                "key"
            ],
            mode="incremental",
        )
    )

    historical = (
        get_discovery_config(
            source[
                "key"
            ],
            mode="historical",
        )
    )

    if (
        incremental is None
        or historical is None
    ):
        result = _unavailable_result(
            investor_name=investor_name,
            source_name=source_name,
            reason=(
                "Matched first-party source does not have "
                "both incremental and historical discovery "
                "configured."
            ),
        )

        result[
            "historical_strategy"
        ] = historical is not None

        return result

    historical_run = (
        _latest_historical_run(
            source_name
        )
    )

    if historical_run is None:
        result = _unavailable_result(
            investor_name=investor_name,
            source_name=source_name,
            reason=(
                "No completed historical discovery run is "
                "recorded for the matched first-party source."
            ),
        )

        result[
            "historical_strategy"
        ] = True

        return result

    current = (
        _window_candidate_coverage(
            source_name=source_name,
            start=current_start,
            end=current_end,
            include_end=True,
        )
    )

    previous = (
        _window_candidate_coverage(
            source_name=source_name,
            start=previous_start,
            end=previous_end,
            include_end=False,
        )
    )

    remaining_undated_funding = (
        _remaining_undated_funding_evidence(
            source_name
        )
    )

    run_dates_complete = (
        remaining_undated_funding
        == 0
    )

    windows_complete = (
        current[
            "status"
        ]
        == "complete"
        and previous[
            "status"
        ]
        == "complete"
    )

    discovery_produced_evidence = (
        historical_run.articles_discovered
        > 0
    )

    complete = (
        run_dates_complete
        and windows_complete
        and discovery_produced_evidence
    )

    if complete:
        status = "complete"
        reason = None

    else:
        status = "incomplete"

        if not discovery_produced_evidence:
            reason = (
                "Historical discovery did not produce "
                "evidence for this source."
            )

        elif not run_dates_complete:
            reason = (
                "Historical source discovery still has "
                "undated Funding Round evidence."
            )

        elif (
            current[
                "status"
            ]
            == "empty"
            or previous[
                "status"
            ]
            == "empty"
        ):
            reason = (
                "At least one comparison window has no "
                "discovered first-party Funding Round "
                "candidates."
            )

        else:
            reason = (
                "At least one comparison window still has "
                "unprocessed first-party Funding Round "
                "candidates."
            )

    return {
        "investor_name":
            investor_name,

        "source_name":
            source_name,

        "source_matched":
            True,

        "historical_strategy":
            True,

        "historical_run_id":
            historical_run.id,

        "historical_run_status":
            historical_run.status,

        "remaining_undated":
            historical_run.remaining_undated,

        "remaining_undated_funding":
            remaining_undated_funding,

        "current_window":
            current,

        "previous_window":
            previous,

        "status":
            status,

        "reason":
            reason,
    }