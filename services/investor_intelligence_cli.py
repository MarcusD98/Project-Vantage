import click

from services.investor_intelligence_service import (
    get_investor_profile,
    get_investor_rankings,
)


def _compact_number(
    value,
):
    if value is None:
        return "-"

    value = float(
        value
    )

    absolute = abs(
        value
    )

    if absolute >= 1_000_000_000:
        return (
            f"{value / 1_000_000_000:.1f}B"
        )

    if absolute >= 1_000_000:
        return (
            f"{value / 1_000_000:.1f}M"
        )

    if absolute >= 1_000:
        return (
            f"{value / 1_000:.1f}K"
        )

    return (
        f"{value:,.0f}"
    )


def _format_delta(
    value,
):
    if value > 0:
        return f"+{value}"

    return str(
        value
    )


def _format_volume(
    volumes,
):
    if not volumes:
        return "-"

    return ", ".join(
        (
            f"{item['currency']} "
            f"{_compact_number(item['amount'])}"
        )
        for item
        in volumes
    )


def _print_exposure(
    title,
    items,
    label_key,
    limit=5,
):
    click.echo("")
    click.echo(
        title
    )

    if not items:
        click.echo(
            "  No observed data."
        )

        return

    for item in items[
        :limit
    ]:
        click.echo(
            f"  {item[label_key]}: "
            f"{item['count']}"
        )


@click.command(
    "investors"
)
@click.option(
    "--window",
    "window_days",
    default=90,
    type=int,
    show_default=True,
    help=(
        "Activity window in days."
    ),
)
@click.option(
    "--limit",
    default=20,
    type=int,
    show_default=True,
    help=(
        "Maximum investors to display."
    ),
)
def investors_command(
    window_days,
    limit,
):
    """
    Rank observed investor activity.
    """

    try:
        rankings = (
            get_investor_rankings(
                window_days=window_days,
                limit=limit,
            )
        )

    except ValueError as exc:
        raise click.ClickException(
            str(exc)
        ) from exc

    click.echo("")
    click.echo(
        "Vantage Investor Activity"
    )
    click.echo(
        "-------------------------"
    )
    click.echo("")

    click.echo(
        f"Window: current {window_days} days "
        f"vs previous {window_days} days"
    )

    click.echo(
        "Observed activity from the Vantage "
        "evidence corpus."
    )

    click.echo("")

    if not rankings:
        click.echo(
            "No investor activity found."
        )

        return

    header = (
        f"{'Investor':25} | "
        f"{'Current':>7} | "
        f"{'Previous':>8} | "
        f"{'Δ':>4} | "
        f"{'Leads':>5} | "
        f"{'All-time':>8}"
    )

    click.echo(
        header
    )

    click.echo(
        "-" * len(
            header
        )
    )

    for item in rankings:
        name = (
            item[
                "investor"
            ]
            .name
        )

        if len(name) > 25:
            name = (
                name[:24]
                + "…"
            )

        click.echo(
            f"{name:25} | "
            f"{item['current_investments']:>7} | "
            f"{item['previous_investments']:>8} | "
            f"{_format_delta(item['investment_delta']):>4} | "
            f"{item['current_leads']:>5} | "
            f"{item['all_time_investments']:>8}"
        )

    click.echo("")


@click.command(
    "investor"
)
@click.option(
    "--name",
    required=True,
    type=str,
    help=(
        "Canonical investor name."
    ),
)
@click.option(
    "--window",
    "window_days",
    default=90,
    type=int,
    show_default=True,
    help=(
        "Activity window in days."
    ),
)
@click.option(
    "--recent",
    "recent_limit",
    default=8,
    type=int,
    show_default=True,
    help=(
        "Recent investments to display."
    ),
)
def investor_command(
    name,
    window_days,
    recent_limit,
):
    """
    Show one investor's observed behaviour profile.
    """

    try:
        profile = (
            get_investor_profile(
                identifier=name,
                window_days=window_days,
                recent_limit=recent_limit,
            )
        )

    except ValueError as exc:
        raise click.ClickException(
            str(exc)
        ) from exc

    if profile is None:
        raise click.ClickException(
            f"Investor not found: {name}"
        )

    investor = (
        profile[
            "investor"
        ]
    )

    current = (
        profile[
            "current_window"
        ]
    )

    previous = (
        profile[
            "previous_window"
        ]
    )

    all_time = (
        profile[
            "all_time"
        ]
    )

    change = (
        profile[
            "change"
        ]
    )

    coverage = (
        profile[
            "coverage"
        ]
    )

    click.echo("")
    click.echo(
        "Vantage Investor Intelligence"
    )
    click.echo(
        "-----------------------------"
    )
    click.echo("")

    click.echo(
        f"Investor:                 "
        f"{investor.name}"
    )

    click.echo(
        f"Window:                   "
        f"{window_days} days"
    )

    click.echo(
        f"As of:                    "
        f"{profile['as_of'].date()}"
    )

    click.echo("")
    click.echo(
        "Observed Activity"
    )
    click.echo(
        "-----------------"
    )

    click.echo(
        f"Current investments:      "
        f"{current['investment_count']}"
    )

    click.echo(
        f"Previous investments:     "
        f"{previous['investment_count']}"
    )

    click.echo(
        f"Investment change:        "
        f"{_format_delta(change['investment_delta'])}"
    )

    click.echo(
        f"Current leads:            "
        f"{current['lead_count']}"
    )

    click.echo(
        f"Previous leads:           "
        f"{previous['lead_count']}"
    )

    click.echo("")
    click.echo(
        f"Observed rounds all-time: "
        f"{all_time['investment_count']}"
    )

    click.echo(
        f"Observed companies:       "
        f"{all_time['company_count']}"
    )

    click.echo(
        f"Observed lead rounds:     "
        f"{all_time['lead_count']}"
    )

    click.echo(
        f"Dated / undated rounds:   "
        f"{coverage['dated_rounds']} / "
        f"{coverage['undated_rounds']}"
    )

    click.echo("")
    click.echo(
        "Observed financing-round volume "
        "participated in:"
    )

    click.echo(
        "  "
        + _format_volume(
            all_time[
                "round_volume_by_currency"
            ]
        )
    )

    click.echo(
        "  (This is total round size, "
        "not investor capital deployed.)"
    )

    _print_exposure(
        "Stage Exposure",
        profile[
            "stage_exposure"
        ][
            "all_time"
        ],
        "stage",
    )

    _print_exposure(
        "Sector Exposure",
        profile[
            "sector_exposure"
        ][
            "all_time"
        ],
        "sector",
    )

    _print_exposure(
        "Geographic Exposure",
        profile[
            "geography_exposure"
        ][
            "all_time"
        ],
        "location",
    )

    click.echo("")
    click.echo(
        "Frequent Co-Investors"
    )

    co_investors = (
        profile[
            "co_investors"
        ]
    )

    if not co_investors:
        click.echo(
            "  No observed co-investors."
        )

    else:
        for item in (
            co_investors[:5]
        ):
            click.echo(
                f"  {item['investor']}: "
                f"{item['shared_rounds']} "
                f"shared round(s)"
            )

    click.echo("")
    click.echo(
        "Recent Investments"
    )

    recent = (
        profile[
            "recent_investments"
        ]
    )

    if not recent:
        click.echo(
            "  No dated investments."
        )

    for item in recent:
        announced = (
            item[
                "announced_at"
            ]
            .date()
        )

        amount = "-"

        if (
            item[
                "amount"
            ]
            is not None
        ):
            currency = (
                item[
                    "currency"
                ]
                or ""
            )

            amount = (
                f"{currency} "
                f"{_compact_number(item['amount'])}"
            ).strip()

        lead_marker = (
            " | LEAD"
            if item[
                "is_lead"
            ]
            else ""
        )

        click.echo("")
        click.echo(
            f"  {announced} | "
            f"{item['company']} | "
            f"{item['stage']} | "
            f"{amount}"
            f"{lead_marker}"
        )

        sources = (
            ", ".join(
                item[
                    "evidence_sources"
                ]
            )
            or "none"
        )

        click.echo(
            f"    Evidence sources "
            f"({item['evidence_count']}): "
            f"{sources}"
        )

    click.echo("")