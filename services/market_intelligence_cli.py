import click

from services.market_signal_service import (
    get_sector_momentum,
)


def _format_date(value):
    if value is None:
        return "-"

    return str(
        value.date()
    )


def _format_change(value):
    if value is None:
        return "-"

    return (
        f"{value:+.1f}%"
    )


def _format_confidence(value):
    if not value:
        return "-"

    return (
        value
        .replace(
            "_",
            " ",
        )
        .upper()
    )


@click.command(
    "market-signals"
)
@click.option(
    "--window",
    "window_days",
    default=180,
    type=click.IntRange(
        min=1,
    ),
    show_default=True,
    help=(
        "Number of days in each "
        "comparison window."
    ),
)
@click.option(
    "--limit",
    default=10,
    type=click.IntRange(
        min=1,
    ),
    show_default=True,
    help=(
        "Maximum supported sector "
        "signals to display."
    ),
)
@click.option(
    "--investor",
    "investor_names",
    multiple=True,
    help=(
        "Restrict the analysis to one or more "
        "configured investors. Repeat the option "
        "to specify multiple investors."
    ),
)
def market_signals_command(
    window_days,
    limit,
    investor_names,
):
    """
    Show evidence-backed market signals from the canonical
    Vantage activity graph.
    """

    selected_investors = (
        list(
            investor_names
        )
        if investor_names
        else None
    )

    try:
        result = (
            get_sector_momentum(
                window_days=(
                    window_days
                ),
                investor_names=(
                    selected_investors
                ),
                limit=limit,
            )
        )

    except ValueError as exc:
        raise click.ClickException(
            str(exc)
        ) from exc

    window = (
        result[
            "window"
        ]
    )

    cohort = (
        result[
            "cohort"
        ]
    )

    coverage = (
        result[
            "coverage"
        ]
    )

    confidence = (
        result[
            "confidence"
        ]
    )

    click.echo("")
    click.echo(
        "Vantage Market Signals"
    )
    click.echo(
        "----------------------"
    )
    click.echo("")

    click.echo(
        "Signal:                  "
        "Sector Momentum"
    )

    click.echo(
        f"Window:                  "
        f"{window['days']} days"
    )

    click.echo(
        f"As of:                   "
        f"{_format_date(result['as_of'])}"
    )

    click.echo("")

    click.echo(
        "Current period:          "
        f"{_format_date(window['current_start'])}"
        " → "
        f"{_format_date(window['current_end'])}"
    )

    click.echo(
        "Previous period:         "
        f"{_format_date(window['previous_start'])}"
        " → "
        f"{_format_date(window['previous_end'])}"
    )

    click.echo("")

    click.echo(
        "Comparable Cohort"
    )
    click.echo(
        "-----------------"
    )

    click.echo(
        f"Requested investors:     "
        f"{len(cohort['requested_investors'])}"
    )

    click.echo(
        f"Resolved investors:      "
        f"{cohort['resolved_investor_count']}"
    )

    click.echo(
        f"Comparable investors:    "
        f"{cohort['comparable_investor_count']}"
    )

    click.echo(
        f"Comparable ratio:        "
        f"{cohort['comparable_ratio']:.1%}"
    )

    click.echo("")

    if (
        cohort[
            "comparable_investor_names"
        ]
    ):
        click.echo(
            "Included:"
        )

        for investor_name in (
            cohort[
                "comparable_investor_names"
            ]
        ):
            click.echo(
                f"  - {investor_name}"
            )

    else:
        click.echo(
            "Included: none"
        )

    click.echo("")

    excluded = [
        row
        for row
        in cohort[
            "coverage_by_investor"
        ]
        if not row[
            "comparable"
        ]
    ]

    if excluded:
        click.echo(
            "Excluded:"
        )

        for row in excluded:
            click.echo(
                f"  - "
                f"{row['investor_name']}: "
                f"{row['temporal_status']}"
            )

            if row[
                "temporal_reason"
            ]:
                click.echo(
                    f"      "
                    f"{row['temporal_reason']}"
                )

        click.echo("")

    if (
        cohort[
            "unresolved_investors"
        ]
    ):
        click.echo(
            "Unresolved:"
        )

        for investor_name in (
            cohort[
                "unresolved_investors"
            ]
        ):
            click.echo(
                f"  - {investor_name}"
            )

        click.echo("")

    click.echo(
        "Observation Coverage"
    )
    click.echo(
        "--------------------"
    )

    click.echo(
        f"Current canonical rounds: "
        f"{result['current_round_count']}"
    )

    click.echo(
        f"Previous canonical rounds:"
        f" {result['previous_round_count']}"
    )

    click.echo(
        f"Current sector coverage:  "
        f"{coverage['current']['percent']:.1f}%"
    )

    click.echo(
        f"Previous sector coverage: "
        f"{coverage['previous']['percent']:.1f}%"
    )

    click.echo(
        f"Combined sector coverage: "
        f"{coverage['combined']['percent']:.1f}%"
    )

    click.echo("")

    click.echo(
        "Signal Confidence"
    )
    click.echo(
        "-----------------"
    )

    click.echo(
        f"Overall confidence:       "
        f"{_format_confidence(confidence['label'])}"
    )

    if confidence[
        "reason"
    ]:
        click.echo(
            f"Reason:                   "
            f"{confidence['reason']}"
        )

    click.echo("")

    click.echo(
        "Sector Momentum"
    )
    click.echo(
        "---------------"
    )

    if not result[
        "signals"
    ]:
        click.echo(
            "No supported sector momentum "
            "signals were produced."
        )

    else:
        header = (
            f"{'Sector':28} | "
            f"{'Current':>7} | "
            f"{'Previous':>8} | "
            f"{'Delta':>6} | "
            f"{'Change':>9} | "
            f"{'Investors':>9} | "
            f"{'Confidence':>17}"
        )

        click.echo(
            header
        )

        click.echo(
            "-" * len(
                header
            )
        )

        for signal in (
            result[
                "signals"
            ]
        ):
            click.echo(
                f"{signal['value'][:28]:28} | "
                f"{signal['current_event_count']:>7} | "
                f"{signal['previous_event_count']:>8} | "
                f"{signal['delta']:>+6} | "
                f"{_format_change(signal['change_pct']):>9} | "
                f"{signal['current_investor_count']:>9} | "
                f"{_format_confidence(signal['confidence']):>17}"
            )

            if (
                signal[
                    "contributing_investors"
                ]
            ):
                click.echo(
                    "  Investors: "
                    + ", ".join(
                        signal[
                            "contributing_investors"
                        ]
                    )
                )

            click.echo(
                "  Canonical events: "
                + ", ".join(
                    str(
                        event_id
                    )
                    for event_id
                    in signal[
                        "current_event_ids"
                    ]
                )
            )

    click.echo("")

    click.echo(
        "Measurement Notes"
    )
    click.echo(
        "-----------------"
    )

    click.echo(
        "Signals compare canonical funding events "
        "across equal time windows."
    )

    click.echo(
        "Only investors with complete matched "
        "first-party corpus coverage across both "
        "windows enter the comparable cohort."
    )

    click.echo(
        "Observed activity is not a claim of "
        "complete real-world market activity."
    )

    click.echo("")