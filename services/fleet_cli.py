import click

from services.fleet_service import (
    run_source_fleet,
)


@click.command(
    "sync"
)
@click.option(
    "--mode",
    type=click.Choice(
        [
            "incremental",
            "historical",
        ],
        case_sensitive=False,
    ),
    default="incremental",
    show_default=True,
    help=(
        "Discovery strategy to run."
    ),
)
@click.option(
    "--type",
    "source_type",
    type=click.Choice(
        [
            "publication",
            "investor",
            "ecosystem",
            "company",
            "structured",
        ],
        case_sensitive=False,
    ),
    default=None,
    help=(
        "Limit the fleet to one "
        "source type."
    ),
)
@click.option(
    "--source",
    "source_names",
    multiple=True,
    help=(
        "Run only a specific source. "
        "May be supplied multiple times."
    ),
)
@click.option(
    "--process",
    "process_intelligence",
    is_flag=True,
    default=False,
    help=(
        "Also run stored LLM intelligence "
        "processing after source sync."
    ),
)
@click.option(
    "--enrichment-limit",
    default=1000,
    type=int,
    show_default=True,
    help=(
        "Maximum undated documents "
        "to enrich per historical source."
    ),
)
@click.option(
    "--funding-limit",
    default=10,
    type=int,
    show_default=True,
    help=(
        "Maximum Funding Round evidence "
        "documents to process per source "
        "when --process is enabled."
    ),
)
@click.option(
    "--fund-news-limit",
    default=10,
    type=int,
    show_default=True,
    help=(
        "Maximum Fund News evidence "
        "documents to process per source "
        "when --process is enabled."
    ),
)
def sync_command(
    mode,
    source_type,
    source_names,
    process_intelligence,
    enrichment_limit,
    funding_limit,
    fund_news_limit,
):
    """
    Sync a configured Vantage source fleet.
    """

    click.echo("")
    click.echo(
        "Vantage Source Fleet"
    )
    click.echo(
        "--------------------"
    )
    click.echo("")

    click.echo(
        f"Mode:                    "
        f"{mode}"
    )

    click.echo(
        f"Source type:             "
        f"{source_type or 'all'}"
    )

    click.echo(
        f"Intelligence processing: "
        f"{'yes' if process_intelligence else 'no'}"
    )

    if source_names:
        click.echo(
            "Requested sources:       "
            + ", ".join(
                source_names
            )
        )

    click.echo("")

    try:
        result = (
            run_source_fleet(
                mode=mode,
                source_type=source_type,
                source_names=(
                    source_names
                    or None
                ),
                process=(
                    process_intelligence
                ),
                enrichment_limit=(
                    enrichment_limit
                ),
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

    for source_result in result[
        "results"
    ]:
        status = (
            source_result[
                "status"
            ]
            .upper()
        )

        click.echo(
            f"[{status}] "
            f"{source_result['source']}"
        )

        discovery = (
            source_result.get(
                "discovery"
            )
        )

        if discovery is not None:
            click.echo(
                "  Discovered: "
                f"{discovery['articles_discovered']} | "
                "Relevant: "
                f"{discovery['articles_relevant']} | "
                "Saved: "
                f"{discovery['articles_saved']}"
            )

            if (
                mode
                == "historical"
            ):
                click.echo(
                    "  Dates populated: "
                    f"{discovery['dates_populated']} | "
                    "Remaining undated: "
                    f"{discovery['remaining_undated']}"
                )

        processing = (
            source_result.get(
                "processing"
            )
        )

        if processing is not None:
            click.echo(
                "  Funding: "
                f"{processing['funding_processed']} "
                "processed / "
                f"{processing['funding_rounds']} events | "
                "Fund news: "
                f"{processing['fund_news_processed']} "
                "processed / "
                f"{processing['fund_closes']} closes"
            )

            if (
                processing[
                    "processing_failed"
                ]
            ):
                click.echo(
                    "  Processing failures: "
                    f"{processing['processing_failed']}"
                )

        if source_result[
            "error"
        ]:
            click.echo(
                "  Error: "
                f"{source_result['error']}"
            )

        click.echo("")

    totals = result[
        "totals"
    ]

    click.echo(
        "Fleet Summary"
    )
    click.echo(
        "-------------"
    )
    click.echo("")

    click.echo(
        f"Sources selected:        "
        f"{totals['sources_selected']}"
    )

    click.echo(
        f"Sources succeeded:       "
        f"{totals['sources_succeeded']}"
    )

    click.echo(
        f"Sources partial:         "
        f"{totals['sources_partial']}"
    )

    click.echo(
        f"Sources failed:          "
        f"{totals['sources_failed']}"
    )

    click.echo("")

    click.echo(
        f"Articles discovered:     "
        f"{totals['articles_discovered']}"
    )

    click.echo(
        f"Relevant articles:       "
        f"{totals['articles_relevant']}"
    )

    click.echo(
        f"New articles saved:      "
        f"{totals['articles_saved']}"
    )

    if (
        mode
        == "historical"
    ):
        click.echo(
            f"Dates populated:         "
            f"{totals['dates_populated']}"
        )

    if process_intelligence:
        click.echo("")

        click.echo(
            f"Articles selected:       "
            f"{totals['articles_selected']}"
        )

        click.echo(
            f"Funding processed:       "
            f"{totals['funding_processed']}"
        )

        click.echo(
            f"Funding events:          "
            f"{totals['funding_rounds']}"
        )

        click.echo(
            f"Fund news processed:     "
            f"{totals['fund_news_processed']}"
        )

        click.echo(
            f"Fund closes:             "
            f"{totals['fund_closes']}"
        )

        click.echo(
            f"Processing failures:     "
            f"{totals['processing_failed']}"
        )

    click.echo("")
    click.echo(
        "Fleet sync complete."
    )