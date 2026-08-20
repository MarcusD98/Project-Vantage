import click

from services.corpus_operations_service import (
    run_backfill_operation,
    run_stored_intelligence,
)

from services.fleet_cli import (
    runs_command,
    sync_command,
)

from services.investor_intelligence_cli import (
    investor_command,
    investors_command,
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


def register_corpus_commands(
    vantage_group,
):
    """
    Register corpus, source-platform and investor-intelligence
    commands under the Vantage Flask CLI group.
    """

    vantage_group.add_command(
        backfill_command
    )

    vantage_group.add_command(
        process_command
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