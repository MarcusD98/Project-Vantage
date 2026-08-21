import click

from models.article import db

from services.market_intelligence_cli import (
    market_signals_command,
)

from services.corpus_operations_service import (
    run_backfill_operation,
    run_stored_intelligence,
)

from services.date_enrichment_service import (
    run_date_enrichment,
)

from services.extraction_measurement_service import (
    get_extraction_measurements,
)

from services.extraction_replay_service import (
    replay_article_by_id,
)

from services.fleet_cli import (
    runs_command,
    sync_command,
)

from services.investor_intelligence_cli import (
    investor_command,
    investors_command,
)

from services.multi_round_integrity_service import (
    audit_multi_round_integrity,
    repair_multi_round_article,
)

from services.observation_scale_service import (
    get_observation_scale_report,
)


def _format_optional_date(value):
    if value is None:
        return "-"

    return str(
        value.date()
    )


def _format_optional_amount(
    amount,
    currency,
):
    if amount is None:
        return "-"

    prefix = (
        f"{currency} "
        if currency
        else ""
    )

    return (
        prefix
        + f"{amount:,.0f}"
    )


def _format_percentage(value):
    return f"{value:.1f}%"


def _format_ratio_percentage(
    value,
):
    if value is None:
        return "-"

    return f"{value:.1%}"


def _format_coverage_days(
    value,
):
    if value is None:
        return "-"

    return str(
        value
    )


def _format_capability(
    value,
):
    return (
        "yes"
        if value
        else "no"
    )


@click.command(
    "backfill"
)
@click.option(
    "--source",
    required=True,
    type=str,
    help=(
        "Configured source to "
        "historically backfill."
    ),
)
@click.option(
    "--enrichment-limit",
    default=1000,
    type=int,
    show_default=True,
    help=(
        "Maximum undated evidence "
        "documents to enrich."
    ),
)
def backfill_command(
    source,
    enrichment_limit,
):
    """
    Recover historical evidence without LLM processing.
    """

    click.echo("")
    click.echo(
        "Vantage Historical Backfill"
    )
    click.echo(
        "---------------------------"
    )
    click.echo("")

    try:
        result = (
            run_backfill_operation(
                source_name=source,
                enrichment_limit=(
                    enrichment_limit
                ),
            )
        )

    except ValueError as exc:
        raise click.ClickException(
            str(exc)
        ) from exc

    click.echo(
        f"Source:                  "
        f"{result['source']}"
    )

    click.echo("")

    click.echo(
        f"Articles discovered:     "
        f"{result['articles_discovered']}"
    )

    click.echo(
        f"Relevant articles:       "
        f"{result['articles_relevant']}"
    )

    click.echo(
        f"New articles saved:      "
        f"{result['articles_saved']}"
    )

    click.echo("")

    click.echo(
        f"Dates populated:         "
        f"{result['dates_populated']}"
    )

    click.echo(
        f"Remaining undated:       "
        f"{result['remaining_undated']}"
    )

    click.echo("")
    click.echo(
        "Backfill complete."
    )


@click.command(
    "enrich-dates"
)
@click.option(
    "--source",
    required=True,
    type=str,
    help=(
        "Configured source whose stored "
        "undated evidence should be enriched."
    ),
)
@click.option(
    "--limit",
    default=20,
    type=click.IntRange(
        min=0,
    ),
    show_default=True,
    help=(
        "Maximum undated evidence documents "
        "to attempt in this run."
    ),
)
def enrich_dates_command(
    source,
    limit,
):
    """
    Recover publication dates for existing stored evidence.

    This command performs no source discovery, LLM extraction,
    or canonical knowledge mutation.
    """

    click.echo("")
    click.echo(
        "Vantage Date Enrichment"
    )
    click.echo(
        "-----------------------"
    )
    click.echo("")

    try:
        result = run_date_enrichment(
            source_name=source,
            limit=limit,
        )

    except (
        ValueError,
        TypeError,
    ) as exc:
        raise click.ClickException(
            str(exc)
        ) from exc

    click.echo(
        f"Source:                  "
        f"{result['source']}"
    )

    click.echo(
        f"Source key:              "
        f"{result['source_key']}"
    )

    click.echo(
        f"Batch limit:             "
        f"{result['limit']}"
    )

    click.echo("")

    click.echo(
        f"Undated before:          "
        f"{result['undated_before']}"
    )

    click.echo(
        f"Attempted:               "
        f"{result['attempted']}"
    )

    click.echo(
        f"Dates recovered:         "
        f"{result['dates_recovered']}"
    )

    click.echo(
        f"Still undated:           "
        f"{result['remaining_undated']}"
    )

    click.echo(
        f"Recovery rate:           "
        f"{_format_percentage(result['recovery_rate'])}"
    )

    click.echo("")

    if (
        result[
            "attempted"
        ]
        == 0
    ):
        click.echo(
            "No undated evidence was selected."
        )

    elif (
        result[
            "dates_recovered"
        ]
        == 0
    ):
        click.echo(
            "No publication dates were recovered "
            "from the attempted batch."
        )

    elif (
        result[
            "dates_recovered"
        ]
        == result[
            "attempted"
        ]
    ):
        click.echo(
            "Publication dates were recovered for "
            "the entire attempted batch."
        )

    else:
        click.echo(
            "Publication dates were recovered for "
            "part of the attempted batch."
        )

    click.echo("")


@click.command(
    "process"
)
@click.option(
    "--source",
    required=True,
    type=str,
    help=(
        "Process stored evidence "
        "from this source only."
    ),
)
@click.option(
    "--historical",
    is_flag=True,
    default=False,
    help=(
        "Process historical stored evidence "
        "without applying the source's current "
        "publication-age cutoff."
    ),
)
@click.option(
    "--funding-limit",
    default=10,
    type=int,
    show_default=True,
    help=(
        "Maximum stored Funding Round "
        "articles to process."
    ),
)
@click.option(
    "--fund-news-limit",
    default=10,
    type=int,
    show_default=True,
    help=(
        "Maximum stored Fund News "
        "articles to process."
    ),
)
def process_command(
    source,
    historical,
    funding_limit,
    fund_news_limit,
):
    """
    Process existing stored evidence without discovery.
    """

    click.echo("")
    click.echo(
        "Vantage Stored Intelligence"
    )
    click.echo(
        "---------------------------"
    )
    click.echo("")

    try:
        result = (
            run_stored_intelligence(
                source_name=source,
                funding_limit=(
                    funding_limit
                ),
                fund_news_limit=(
                    fund_news_limit
                ),
                historical=historical,
            )
        )

    except ValueError as exc:
        raise click.ClickException(
            str(exc)
        ) from exc

    click.echo(
        f"Source:                  "
        f"{result['source']}"
    )

    click.echo(
        f"Mode:                    "
        f"{'historical' if result['historical'] else 'current'}"
    )

    click.echo("")

    click.echo(
        f"Articles selected:       "
        f"{result['articles_selected']}"
    )

    click.echo(
        f"Stale articles skipped:  "
        f"{result['stale_articles_skipped']}"
    )

    click.echo(
        f"Compound articles skipped:"
        f" {result['compound_articles_skipped']}"
    )

    click.echo(
        f"Content retrieved:       "
        f"{result['content_retrieved']}"
    )

    click.echo(
        f"Content failures:        "
        f"{result['content_failed']}"
    )

    click.echo("")

    click.echo(
        f"Funding processed:       "
        f"{result['funding_processed']}"
    )

    click.echo(
        f"Funding rounds saved:    "
        f"{result['funding_rounds']}"
    )

    click.echo("")

    click.echo(
        f"Fund news processed:     "
        f"{result['fund_news_processed']}"
    )

    click.echo(
        f"Fund closes saved:       "
        f"{result['fund_closes']}"
    )

    click.echo("")

    click.echo(
        f"Processing failures:     "
        f"{result['processing_failed']}"
    )

    click.echo("")
    click.echo(
        "Stored intelligence processing complete."
    )


@click.command(
    "replay"
)
@click.option(
    "--article-id",
    required=True,
    type=int,
    help=(
        "Stored Article ID to reprocess."
    ),
)
@click.option(
    "--event-type",
    required=True,
    type=click.Choice(
        [
            "funding_round",
            "fund_close",
        ],
        case_sensitive=True,
    ),
    help=(
        "Structured event extractor to replay."
    ),
)
def replay_command(
    article_id,
    event_type,
):
    """
    Reprocess one stored evidence document using the current
    extractor version.
    """

    click.echo("")
    click.echo(
        "Vantage Extraction Replay"
    )
    click.echo(
        "-------------------------"
    )
    click.echo("")

    try:
        result = replay_article_by_id(
            article_id=article_id,
            event_type=event_type,
        )

    except (
        ValueError,
        RuntimeError,
    ) as exc:
        raise click.ClickException(
            str(exc)
        ) from exc

    click.echo(
        f"Article ID:              "
        f"{result['article_id']}"
    )

    click.echo(
        f"Event type:              "
        f"{result['event_type']}"
    )

    click.echo(
        f"Extraction record:       "
        f"#{result['record_id']}"
    )

    click.echo(
        f"Extractor version:       "
        f"{result['extractor_version']}"
    )

    click.echo(
        f"Model:                   "
        f"{result['model']}"
    )

    click.echo("")

    click.echo(
        f"Validation state:        "
        f"{result['validation_state'].upper()}"
    )

    flags = (
        result[
            "validation_flags"
        ]
        or []
    )

    click.echo(
        "Validation flags:        "
        + (
            ", ".join(
                flags
            )
            if flags
            else "none"
        )
    )

    click.echo("")

    click.echo(
        f"Promoted:                "
        f"{'yes' if result['promoted'] else 'no'}"
    )

    click.echo("")

    if result[
        "promoted"
    ]:
        click.echo(
            "Replay successfully reached "
            "canonical knowledge."
        )

    elif (
        result[
            "validation_state"
        ]
        in {
            "review",
            "reject",
        }
    ):
        click.echo(
            "Replay was durably recorded but "
            "quarantined from canonical knowledge."
        )

    else:
        click.echo(
            "Replay completed without canonical "
            "promotion."
        )

    click.echo("")


@click.command(
    "pipeline-report"
)
@click.option(
    "--source",
    default=None,
    type=str,
    help=(
        "Restrict measurements to one "
        "evidence source."
    ),
)
@click.option(
    "--event-type",
    default=None,
    type=click.Choice(
        [
            "funding_round",
            "fund_close",
        ],
        case_sensitive=True,
    ),
    help=(
        "Restrict measurements to one "
        "structured event type."
    ),
)
@click.option(
    "--extractor-version",
    default=None,
    type=str,
    help=(
        "Restrict measurements to one "
        "extractor version."
    ),
)
def pipeline_report_command(
    source,
    event_type,
    extractor_version,
):
    """
    Report extraction, validation, promotion, replay, and source
    quality measurements for the knowledge pipeline.
    """

    report = get_extraction_measurements(
        source=source,
        event_type=event_type,
        extractor_version=(
            extractor_version
        ),
    )

    click.echo("")
    click.echo(
        "Vantage Knowledge Pipeline"
    )
    click.echo(
        "--------------------------"
    )
    click.echo("")

    filters = report[
        "filters"
    ]

    if any(
        value is not None
        for value in filters.values()
    ):
        click.echo(
            "Filters"
        )
        click.echo(
            "-------"
        )

        click.echo(
            f"Source:                  "
            f"{filters['source'] or 'all'}"
        )

        click.echo(
            f"Event type:              "
            f"{filters['event_type'] or 'all'}"
        )

        click.echo(
            f"Extractor version:       "
            f"{filters['extractor_version'] or 'all'}"
        )

        click.echo("")

    attempts = report[
        "extraction_attempts"
    ]

    click.echo(
        f"Extraction attempts:     "
        f"{attempts}"
    )

    click.echo("")

    click.echo(
        "Validation"
    )
    click.echo(
        "----------"
    )

    for state in (
        "promote",
        "review",
        "reject",
        "pending",
    ):
        row = report[
            "validation"
        ][
            state
        ]

        click.echo(
            f"{state.upper():<24}"
            f"{row['count']:>6}   "
            f"{_format_percentage(row['percentage']):>6}"
        )

    if (
        "unknown"
        in report[
            "validation"
        ]
    ):
        row = report[
            "validation"
        ][
            "unknown"
        ]

        click.echo(
            f"{'UNKNOWN':<24}"
            f"{row['count']:>6}   "
            f"{_format_percentage(row['percentage']):>6}"
        )

    click.echo("")

    quarantine = report[
        "quarantined"
    ]

    click.echo(
        f"Quarantined:             "
        f"{quarantine['count']} "
        f"({_format_percentage(quarantine['percentage'])})"
    )

    click.echo("")

    promotion = report[
        "promotion"
    ]

    click.echo(
        "Promotion"
    )
    click.echo(
        "---------"
    )

    click.echo(
        f"Eligible for promotion:  "
        f"{promotion['eligible_for_promotion']}"
    )

    click.echo(
        f"Successfully promoted:   "
        f"{promotion['promoted']}"
    )

    click.echo(
        f"Unpromoted PROMOTE:      "
        f"{promotion['unpromoted_promote']}"
    )

    click.echo(
        f"Promotion rate:          "
        f"{_format_percentage(promotion['promotion_rate'])}"
    )

    click.echo("")

    replay = report[
        "replay"
    ]

    click.echo(
        "Replay / Reprocessing"
    )
    click.echo(
        "---------------------"
    )

    click.echo(
        f"Evidence/event pairs:    "
        f"{replay['unique_evidence_event_pairs']}"
    )

    click.echo(
        f"Pairs replayed:          "
        f"{replay['replayed_evidence_event_pairs']}"
    )

    click.echo(
        f"Replay attempts:         "
        f"{replay['replay_attempts']}"
    )

    click.echo("")

    click.echo(
        "By Event Type"
    )
    click.echo(
        "-------------"
    )

    if report[
        "by_event_type"
    ]:
        for row in report[
            "by_event_type"
        ]:
            click.echo(
                f"{row['event_type']:<24}"
                f"{row['count']:>6}"
            )

    else:
        click.echo(
            "No extraction records."
        )

    click.echo("")

    click.echo(
        "By Extractor Version"
    )
    click.echo(
        "--------------------"
    )

    if report[
        "by_extractor_version"
    ]:
        for row in report[
            "by_extractor_version"
        ]:
            click.echo(
                f"{row['extractor_version']:<24}"
                f"{row['count']:>6}"
            )

    else:
        click.echo(
            "No extraction records."
        )

    click.echo("")

    click.echo(
        "By Model"
    )
    click.echo(
        "--------"
    )

    if report[
        "by_model"
    ]:
        for row in report[
            "by_model"
        ]:
            click.echo(
                f"{row['model']:<24}"
                f"{row['count']:>6}"
            )

    else:
        click.echo(
            "No extraction records."
        )

    click.echo("")

    click.echo(
        "Validation Flags"
    )
    click.echo(
        "----------------"
    )

    if report[
        "validation_flags"
    ]:
        for row in report[
            "validation_flags"
        ]:
            click.echo(
                f"{row['flag']:<32}"
                f"{row['count']:>6}"
            )

    else:
        click.echo(
            "No validation flags."
        )

    click.echo("")

    click.echo(
        "By Source"
    )
    click.echo(
        "---------"
    )

    if report[
        "by_source"
    ]:
        for row in report[
            "by_source"
        ]:
            click.echo(
                row[
                    "source"
                ]
            )

            click.echo(
                f"  Attempts:              "
                f"{row['attempts']}"
            )

            click.echo(
                f"  PROMOTE / REVIEW / REJECT / PENDING: "
                f"{row['promote']} / "
                f"{row['review']} / "
                f"{row['reject']} / "
                f"{row['pending']}"
            )

            click.echo(
                f"  Promoted:              "
                f"{row['promoted']}"
            )

            click.echo(
                f"  Unpromoted PROMOTE:    "
                f"{row['unpromoted_promote']}"
            )

            click.echo(
                f"  Promotion rate:        "
                f"{_format_percentage(row['promotion_rate'])}"
            )

            click.echo("")

    else:
        click.echo(
            "No source measurements."
        )
        click.echo("")

    click.echo(
        "Note: 'Unpromoted PROMOTE' does not necessarily "
        "mean promotion failure."
    )

    click.echo(
        "The current schema cannot distinguish a failed "
        "canonical write from a PROMOTE record that produced "
        "no canonical object."
    )

    click.echo("")


@click.command(
    "observation-report"
)
@click.option(
    "--source-type",
    default=None,
    type=click.Choice(
        [
            "publication",
            "investor",
            "ecosystem",
            "company",
            "structured",
        ],
        case_sensitive=True,
    ),
    help=(
        "Restrict the observation baseline "
        "to one source type."
    ),
)
@click.option(
    "--include-disabled",
    is_flag=True,
    default=False,
    help=(
        "Include disabled registry sources "
        "in the observation baseline."
    ),
)
def observation_report_command(
    source_type,
    include_disabled,
):
    """
    Report the current scale and historical readiness of the
    Vantage observation network.
    """

    report = get_observation_scale_report(
        enabled_only=(
            not include_disabled
        ),
        source_type=source_type,
    )

    summary = report[
        "summary"
    ]

    click.echo("")
    click.echo(
        "Vantage Observation Baseline"
    )
    click.echo(
        "----------------------------"
    )
    click.echo("")

    if source_type is not None:
        click.echo(
            f"Source type:             "
            f"{source_type}"
        )

    click.echo(
        f"Enabled only:            "
        f"{'no' if include_disabled else 'yes'}"
    )

    click.echo("")

    click.echo(
        "Network"
    )
    click.echo(
        "-------"
    )

    click.echo(
        f"Sources:                 "
        f"{summary['sources']}"
    )

    click.echo(
        f"Incremental-capable:     "
        f"{summary['incremental_capable']}"
    )

    click.echo(
        f"Historical-capable:      "
        f"{summary['historical_capable']}"
    )

    click.echo(
        f"Historical capability:   "
        f"{_format_percentage(summary['historical_capability_rate'])}"
    )

    click.echo("")

    click.echo(
        "Observed Corpus"
    )
    click.echo(
        "---------------"
    )

    click.echo(
        f"Sources with evidence:   "
        f"{summary['sources_with_evidence']}"
    )

    click.echo(
        f"Sources with >=12m span: "
        f"{summary['sources_with_12m_coverage']}"
    )

    click.echo(
        f"Sources with >=24m span: "
        f"{summary['sources_with_24m_coverage']}"
    )

    click.echo(
        f"Stored evidence:         "
        f"{summary['stored_evidence']}"
    )

    click.echo("")

    click.echo(
        "Knowledge Production"
    )
    click.echo(
        "--------------------"
    )

    click.echo(
        f"Extraction attempts:     "
        f"{summary['extraction_attempts']}"
    )

    click.echo(
        f"Promoted extractions:    "
        f"{summary['promoted_extractions']}"
    )

    click.echo(
        f"Unique funding events:   "
        f"{summary['unique_funding_events']}"
    )

    click.echo("")

    click.echo(
        "Source Cohort"
    )
    click.echo(
        "-------------"
    )

    if report[
        "by_source_type"
    ]:
        for row in report[
            "by_source_type"
        ]:
            click.echo(
                f"{row['source_type']:<24}"
                f"{row['count']:>6}"
            )

    else:
        click.echo(
            "No sources."
        )

    click.echo("")

    click.echo(
        "Source Detail"
    )
    click.echo(
        "-------------"
    )

    if not report[
        "sources"
    ]:
        click.echo(
            "No sources match the selected filters."
        )
        click.echo("")
        return

    for row in report[
        "sources"
    ]:
        click.echo(
            f"{row['name']} "
            f"[{row['source_type']}] "
            f"({row['region']})"
        )

        click.echo(
            f"  Discovery:             "
            f"incremental="
            f"{_format_capability(row['incremental_capable'])}"
            f" ({row['incremental_method'] or '-'})"
            f" | historical="
            f"{_format_capability(row['historical_capable'])}"
            f" ({row['historical_method'] or '-'})"
        )

        click.echo(
            f"  Stored evidence:       "
            f"{row['stored_evidence']}"
        )

        click.echo(
            f"  Dated / undated:       "
            f"{row['dated_evidence']} / "
            f"{row['undated_evidence']}"
        )

        click.echo(
            f"  Oldest evidence:       "
            f"{_format_optional_date(row['oldest_evidence_at'])}"
        )

        click.echo(
            f"  Newest evidence:       "
            f"{_format_optional_date(row['newest_evidence_at'])}"
        )

        click.echo(
            f"  Observed span days:    "
            f"{_format_coverage_days(row['coverage_days'])}"
        )

        click.echo(
            f"  Coverage class:        "
            f"{row['coverage_status']}"
        )

        click.echo(
            f"  Extraction attempts:   "
            f"{row['extraction_attempts']}"
        )

        click.echo(
            f"  P / R / X / Pending:   "
            f"{row['promote']} / "
            f"{row['review']} / "
            f"{row['reject']} / "
            f"{row['pending']}"
        )

        click.echo(
            f"  Promoted:              "
            f"{row['promoted']}"
        )

        click.echo(
            f"  Promotion rate:        "
            f"{_format_percentage(row['promotion_rate'])}"
        )

        click.echo(
            f"  Quarantine rate:       "
            f"{_format_percentage(row['quarantine_rate'])}"
        )

        click.echo(
            f"  Funding events:        "
            f"{row['supported_funding_events']}"
        )

        click.echo(
            f"  Unique events:         "
            f"{row['unique_funding_events']}"
        )

        click.echo(
            f"  Multi-source events:   "
            f"{row['multi_source_funding_events']}"
        )

        click.echo(
            f"  Funding overlap:       "
            f"{_format_ratio_percentage(row['funding_overlap_rate'])}"
        )

        click.echo("")

    click.echo(
        "Observed span describes the dated Vantage corpus "
        "between its oldest and newest evidence documents."
    )

    click.echo(
        "It does not imply continuous coverage or complete "
        "knowledge of real-world activity."
    )

    click.echo("")


@click.command(
    "multi-rounds"
)
@click.option(
    "--source",
    default=None,
    type=str,
    help=(
        "Optionally restrict the integrity audit to one "
        "evidence source."
    ),
)
def multi_rounds_command(
    source,
):
    """
    Audit multi-round risk without treating review signals as
    automatic deletion evidence.
    """

    result = audit_multi_round_integrity(
        source_name=source
    )

    click.echo("")
    click.echo(
        "Vantage Multi-Round Integrity Audit"
    )
    click.echo(
        "-----------------------------------"
    )
    click.echo("")

    click.echo(
        f"Source filter:            "
        f"{source or 'all'}"
    )

    click.echo(
        f"Review-signal articles:   "
        f"{result['suspect_articles']}"
    )

    click.echo(
        f"Attached canonical rounds:"
        f" {result['attached_rounds']}"
    )

    click.echo(
        f"Automatic repair candidates:"
        f" {result['automatic_repair_candidates']}"
    )

    click.echo(
        f"Review-only candidates:  "
        f"{result['review_only_candidates']}"
    )

    click.echo(
        f"Shared-event manual review:"
        f" {result['manual_review_candidates']}"
    )

    click.echo("")
    click.echo(
        "Review signals are diagnostic only. A sole evidence "
        "source does not prove that a canonical round is invalid."
    )
    click.echo("")

    if not result[
        "rows"
    ]:
        click.echo(
            "No multi-round review signals found."
        )
        click.echo("")
        return

    for row in result[
        "rows"
    ]:
        click.echo(
            f"Article #{row['article_id']} | "
            f"{row['source']} | "
            f"{_format_optional_date(row['published_at'])}"
        )

        click.echo(
            f"  {row['title']}"
        )

        if row[
            "blocking_reasons"
        ]:
            click.echo(
                "  Blocking reasons: "
                + ", ".join(
                    row[
                        "blocking_reasons"
                    ]
                )
            )

        diagnostic_only = [
            reason
            for reason in row[
                "review_reasons"
            ]
            if reason not in row[
                "blocking_reasons"
            ]
        ]

        if diagnostic_only:
            click.echo(
                "  Review signals: "
                + ", ".join(
                    diagnostic_only
                )
            )

        if row[
            "round_id"
        ] is None:
            click.echo(
                "  Canonical round: none"
            )

        else:
            click.echo(
                f"  Round #{row['round_id']} | "
                f"{row['company']} | "
                f"{row['round_type']} | "
                f"{_format_optional_amount(row['amount'], row['currency'])} | "
                f"{_format_optional_date(row['announced_at'])}"
            )

            click.echo(
                f"  Other evidence: "
                f"{row['other_evidence_count']}"
                + (
                    " ("
                    + ", ".join(
                        row[
                            "other_evidence_sources"
                        ]
                    )
                    + ")"
                    if row[
                        "other_evidence_sources"
                    ]
                    else ""
                )
            )

        click.echo(
            "  Recommended action: "
            f"{row['recommended_action'].upper()}"
        )

        click.echo(
            f"  URL: {row['url']}"
        )

        click.echo("")


@click.command(
    "multi-round-repair"
)
@click.option(
    "--article-id",
    required=True,
    type=int,
    help=(
        "Article ID from the multi-round integrity audit."
    ),
)
@click.option(
    "--confirmed-invalid",
    is_flag=True,
    default=False,
    help=(
        "Explicitly confirm that a REVIEW_ONLY article has been "
        "human-verified as an invalid synthetic event. This does "
        "not override the multi-source safety refusal."
    ),
)
@click.option(
    "--apply",
    "apply_changes",
    is_flag=True,
    default=False,
    help=(
        "Apply the repair. Without this flag the command is "
        "a read-only dry run."
    ),
)
def multi_round_repair_command(
    article_id,
    confirmed_invalid,
    apply_changes,
):
    """
    Repair one reviewed invalid event conservatively.
    """

    try:
        result = repair_multi_round_article(
            article_id=article_id,
            apply=apply_changes,
            confirmed_invalid=(
                confirmed_invalid
            ),
        )

        if apply_changes:
            db.session.commit()

    except ValueError as exc:
        db.session.rollback()

        raise click.ClickException(
            str(exc)
        ) from exc

    except Exception:
        db.session.rollback()
        raise

    article = result[
        "article"
    ]

    click.echo("")
    click.echo(
        "Vantage Multi-Round Repair"
    )
    click.echo(
        "--------------------------"
    )
    click.echo("")

    click.echo(
        f"Mode:                    "
        f"{'APPLY' if apply_changes else 'DRY RUN'}"
    )

    click.echo(
        f"Article:                 "
        f"#{article.id} {article.title}"
    )

    click.echo(
        "Blocking reasons:        "
        + (
            ", ".join(
                result[
                    "blocking_reasons"
                ]
            )
            or "none"
        )
    )

    click.echo(
        "Review signals:          "
        + (
            ", ".join(
                result[
                    "review_reasons"
                ]
            )
            or "none"
        )
    )

    click.echo(
        f"Human-confirmed invalid: "
        f"{'yes' if result['confirmed_invalid'] else 'no'}"
    )

    click.echo(
        f"Attached rounds:         "
        f"{len(result['rounds'])}"
    )

    click.echo(
        f"Repair permitted:        "
        f"{'yes' if result['can_apply'] else 'no'}"
    )

    if result[
        "reason"
    ]:
        click.echo(
            f"Reason:                  "
            f"{result['reason']}"
        )

    for row in result[
        "rows"
    ]:
        click.echo("")
        click.echo(
            f"  Round #{row['round_id']} | "
            f"{row['company']} | "
            f"{row['round_type']} | "
            f"other evidence "
            f"{row['other_evidence_count']}"
        )

    click.echo("")

    if apply_changes:
        click.echo(
            f"Rounds deleted:          "
            f"{result['rounds_deleted']}"
        )

        click.echo(
            "Article returned to an unprocessed evidence state."
        )

    else:
        click.echo(
            "No database changes were made."
        )

        if (
            result[
                "can_apply"
            ]
        ):
            click.echo(
                "Re-run with --apply after reviewing the evidence."
            )

        elif (
            not result[
                "blocking_reasons"
            ]
            and not confirmed_invalid
        ):
            click.echo(
                "For a REVIEW_ONLY case, verify the article first; "
                "only then re-run with --confirmed-invalid."
            )

    click.echo("")


def register_corpus_commands(
    vantage_group,
):
    """
    Register corpus, source-platform, integrity, replay,
    measurement, observation-scale, enrichment, and
    investor-intelligence commands under the Vantage Flask CLI
    group.
    """

    vantage_group.add_command(
        backfill_command
    )

    vantage_group.add_command(
        enrich_dates_command
    )

    vantage_group.add_command(
        process_command
    )

    vantage_group.add_command(
        replay_command
    )

    vantage_group.add_command(
        pipeline_report_command
    )

    vantage_group.add_command(
        observation_report_command
    )

    vantage_group.add_command(
        sync_command
    )

    vantage_group.add_command(
        runs_command
    )

    vantage_group.add_command(
        investors_command
    )

    vantage_group.add_command(
        investor_command
    )

    vantage_group.add_command(
        multi_rounds_command
    )

    vantage_group.add_command(
        multi_round_repair_command
    )

    vantage_group.add_command(
    market_signals_command
    )