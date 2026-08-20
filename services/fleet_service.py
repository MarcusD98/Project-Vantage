from source_registry import (
    get_discovery_sources,
)

from services.corpus_operations_service import (
    run_stored_intelligence,
)

from services.source_run_service import (
    finish_source_run,
    start_source_run,
)

from services.source_sync_service import (
    run_source_sync,
)


def _normalize_identifier(
    value,
):
    return (
        str(value)
        .strip()
        .casefold()
    )


def select_source_fleet(
    mode="incremental",
    source_type=None,
    source_names=None,
):
    """
    Select enabled sources from the canonical registry.

    Fleet selection can operate by:

        discovery mode
        source type
        explicit source names / keys

    Explicit sources may be addressed by canonical display name
    or source key.
    """

    fleet = (
        get_discovery_sources(
            mode=mode,
            source_type=source_type,
            enabled_only=True,
        )
    )

    if not source_names:
        return fleet

    requested = {
        _normalize_identifier(
            name
        )
        for name in source_names
        if str(name).strip()
    }

    if not requested:
        return fleet

    selected = []
    matched = set()

    for source in fleet:
        identifiers = {
            _normalize_identifier(
                source["name"]
            ),
            _normalize_identifier(
                source.get(
                    "key",
                    "",
                )
            ),
        }

        source_matches = (
            requested
            & identifiers
        )

        if not source_matches:
            continue

        selected.append(
            source
        )

        matched.update(
            source_matches
        )

    unmatched = (
        requested
        - matched
    )

    if unmatched:
        missing = ", ".join(
            sorted(
                unmatched
            )
        )

        raise ValueError(
            "Requested source(s) are not "
            f"available for {mode} sync: "
            f"{missing}"
        )

    return selected


def _empty_totals():
    return {
        "sources_selected": 0,
        "sources_succeeded": 0,
        "sources_warning": 0,
        "sources_partial": 0,
        "sources_failed": 0,

        "articles_discovered": 0,
        "articles_relevant": 0,
        "articles_saved": 0,

        "dates_populated": 0,

        "articles_selected": 0,

        "funding_processed": 0,
        "funding_rounds": 0,

        "fund_news_processed": 0,
        "fund_closes": 0,

        "processing_failed": 0,
    }


def _add_discovery_totals(
    totals,
    result,
):
    for key in [
        "articles_discovered",
        "articles_relevant",
        "articles_saved",
        "dates_populated",
    ]:
        totals[key] += (
            result.get(
                key,
                0,
            )
            or 0
        )


def _add_processing_totals(
    totals,
    result,
):
    for key in [
        "articles_selected",
        "funding_processed",
        "funding_rounds",
        "fund_news_processed",
        "fund_closes",
        "processing_failed",
    ]:
        totals[key] += (
            result.get(
                key,
                0,
            )
            or 0
        )


def _increment_status_total(
    totals,
    status,
):
    if status == "success":
        totals[
            "sources_succeeded"
        ] += 1

    elif status == "warning":
        totals[
            "sources_warning"
        ] += 1

    elif status == "partial":
        totals[
            "sources_partial"
        ] += 1

    elif status == "failed":
        totals[
            "sources_failed"
        ] += 1


def run_source_fleet(
    mode="incremental",
    source_type=None,
    source_names=None,
    process=False,
    enrichment_limit=1000,
    funding_limit=10,
    fund_news_limit=10,
):
    """
    Operate a selected Vantage source fleet.

    Every source execution creates a persistent SourceRun.

    Sources operate independently.

    A failed source does not prevent later sources from
    running.

    Status semantics:

        success
            Discovery succeeded and optional intelligence
            processing completed without recorded failures.

        warning
            The source completed, but one or more evidence
            documents failed intelligence processing.

        partial
            Discovery succeeded but the optional processing
            operation raised an exception.

        failed
            Discovery or persistence failed.

    By default the fleet only discovers and persists evidence.

    Historical mode additionally performs page/date
    enrichment.

    LLM processing occurs only when process=True.
    """

    fleet = (
        select_source_fleet(
            mode=mode,
            source_type=source_type,
            source_names=source_names,
        )
    )

    totals = (
        _empty_totals()
    )

    totals[
        "sources_selected"
    ] = len(
        fleet
    )

    results = []

    for source in fleet:
        source_run = (
            start_source_run(
                source=source,
                mode=mode,
                process_enabled=process,
            )
        )

        source_result = {
            "run_id":
                source_run.id,

            "source":
                source["name"],

            "source_key":
                source.get(
                    "key"
                ),

            "source_type":
                source.get(
                    "type"
                ),

            "mode":
                mode,

            "status":
                "running",

            "error":
                None,

            "discovery":
                None,

            "processing":
                None,
        }

        # -------------------------------------------------
        # Discovery / persistence
        # -------------------------------------------------

        try:
            discovery_result = (
                run_source_sync(
                    source=source,
                    mode=mode,
                    enrichment_limit=(
                        enrichment_limit
                    ),
                )
            )

            source_result[
                "discovery"
            ] = discovery_result

            _add_discovery_totals(
                totals,
                discovery_result,
            )

        except Exception as exc:
            source_result[
                "status"
            ] = "failed"

            source_result[
                "error"
            ] = str(
                exc
            )

            finish_source_run(
                source_run=source_run,
                status="failed",
                discovery=None,
                processing=None,
                error=exc,
            )

            _increment_status_total(
                totals,
                "failed",
            )

            results.append(
                source_result
            )

            continue

        # -------------------------------------------------
        # Optional intelligence processing
        # -------------------------------------------------

        if process:
            try:
                processing_result = (
                    run_stored_intelligence(
                        source_name=(
                            source[
                                "name"
                            ]
                        ),
                        funding_limit=(
                            funding_limit
                        ),
                        fund_news_limit=(
                            fund_news_limit
                        ),
                    )
                )

                source_result[
                    "processing"
                ] = processing_result

                _add_processing_totals(
                    totals,
                    processing_result,
                )

                if (
                    processing_result.get(
                        "processing_failed",
                        0,
                    )
                    > 0
                ):
                    source_result[
                        "status"
                    ] = "warning"

                else:
                    source_result[
                        "status"
                    ] = "success"

            except Exception as exc:
                source_result[
                    "status"
                ] = "partial"

                source_result[
                    "error"
                ] = str(
                    exc
                )

                finish_source_run(
                    source_run=source_run,
                    status="partial",
                    discovery=discovery_result,
                    processing=None,
                    error=exc,
                )

                _increment_status_total(
                    totals,
                    "partial",
                )

                results.append(
                    source_result
                )

                continue

        else:
            source_result[
                "status"
            ] = "success"

        # -------------------------------------------------
        # Persist completed operation
        # -------------------------------------------------

        finish_source_run(
            source_run=source_run,
            status=source_result[
                "status"
            ],
            discovery=discovery_result,
            processing=source_result[
                "processing"
            ],
            error=None,
        )

        _increment_status_total(
            totals,
            source_result[
                "status"
            ],
        )

        results.append(
            source_result
        )

    return {
        "mode":
            mode,

        "source_type":
            source_type,

        "process":
            bool(
                process
            ),

        "results":
            results,

        "totals":
            totals,
    }