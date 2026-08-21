import click

from models.article import db

from services.corpus_operations_service import (
    run_backfill_operation,
    run_stored_intelligence,
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

    Replay ignores legacy Article.llm_processed_at state and
    appends a new ExtractionRecord rather than overwriting
    previous extraction history.
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
    Register corpus, source-platform, integrity, replay, and
    investor-intelligence commands under the Vantage Flask CLI
    group.
    """

    vantage_group.add_command(
        backfill_command
    )

    vantage_group.add_command(
        process_command
    )

    vantage_group.add_command(
        replay_command
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