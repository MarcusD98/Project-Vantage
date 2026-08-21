import click

from services.source_probe_service import (
    probe_source_candidate,
)


def _format_optional_date(
    value,
):
    if value is None:
        return "-"

    try:
        return str(
            value.date()
        )

    except AttributeError:
        return str(
            value
        )


@click.command(
    "source-probe"
)
@click.option(
    "--name",
    required=True,
    type=str,
    help=(
        "Display name for the candidate source."
    ),
)
@click.option(
    "--method",
    required=True,
    type=click.Choice(
        [
            "rss",
            "sitemap",
            "html",
        ],
        case_sensitive=False,
    ),
    help=(
        "Existing Vantage discovery method "
        "to test."
    ),
)
@click.option(
    "--url",
    required=True,
    type=str,
    help=(
        "Candidate feed, sitemap, or HTML "
        "listing URL."
    ),
)
@click.option(
    "--selector",
    "link_selector",
    default=None,
    type=str,
    help=(
        "HTML link selector. Only relevant "
        "for HTML discovery."
    ),
)
@click.option(
    "--include",
    "include_url_patterns",
    multiple=True,
    help=(
        "URL substring that discovered pages "
        "must contain. Repeat as needed."
    ),
)
@click.option(
    "--exclude",
    "exclude_url_patterns",
    multiple=True,
    help=(
        "URL substring to exclude. "
        "Repeat as needed."
    ),
)
@click.option(
    "--exclude-regex",
    "exclude_url_regex_patterns",
    multiple=True,
    help=(
        "Regex pattern for URLs to exclude. "
        "Repeat as needed."
    ),
)
@click.option(
    "--sitemap-include",
    "sitemap_include_patterns",
    multiple=True,
    help=(
        "When probing a sitemap index, only "
        "traverse child sitemaps containing "
        "this substring."
    ),
)
@click.option(
    "--max-items",
    "max_discovery_items",
    default=50,
    type=click.IntRange(
        min=1,
    ),
    show_default=True,
    help=(
        "Maximum discovered candidates "
        "returned by the probe."
    ),
)
@click.option(
    "--max-pages",
    "max_discovery_pages",
    default=1,
    type=click.IntRange(
        min=1,
    ),
    show_default=True,
    help=(
        "Maximum HTML listing pages to inspect."
    ),
)
@click.option(
    "--show",
    "show_items",
    default=10,
    type=click.IntRange(
        min=0,
    ),
    show_default=True,
    help=(
        "Maximum discovered candidate URLs "
        "to print."
    ),
)
def source_probe_command(
    name,
    method,
    url,
    link_selector,
    include_url_patterns,
    exclude_url_patterns,
    exclude_url_regex_patterns,
    sitemap_include_patterns,
    max_discovery_items,
    max_discovery_pages,
    show_items,
):
    """
    Test a candidate source through Vantage's existing discovery
    platform without registering or persisting it.
    """

    try:
        result = (
            probe_source_candidate(
                name=name,
                method=method,
                url=url,
                link_selector=(
                    link_selector
                ),
                include_url_patterns=(
                    include_url_patterns
                ),
                exclude_url_patterns=(
                    exclude_url_patterns
                ),
                exclude_url_regex_patterns=(
                    exclude_url_regex_patterns
                ),
                sitemap_include_patterns=(
                    sitemap_include_patterns
                ),
                max_discovery_items=(
                    max_discovery_items
                ),
                max_discovery_pages=(
                    max_discovery_pages
                ),
            )
        )

    except ValueError as exc:
        raise click.ClickException(
            str(exc)
        ) from exc

    click.echo("")
    click.echo(
        "Vantage Source Compatibility Probe"
    )
    click.echo(
        "----------------------------------"
    )
    click.echo("")

    click.echo(
        f"Source:                  "
        f"{result['name']}"
    )

    click.echo(
        f"Method:                  "
        f"{result['method']}"
    )

    click.echo(
        f"URL:                     "
        f"{result['url']}"
    )

    click.echo("")

    click.echo(
        f"Probe status:            "
        f"{result['status'].upper()}"
    )

    click.echo(
        f"Candidates discovered:   "
        f"{result['discovered']}"
    )

    click.echo(
        f"Already dated:           "
        f"{result['dated']}"
    )

    click.echo(
        f"Undated:                 "
        f"{result['undated']}"
    )

    click.echo("")

    if (
        result[
            "status"
        ]
        == "productive"
    ):
        click.echo(
            "Candidate Sample"
        )
        click.echo(
            "----------------"
        )

        click.echo("")

        for item in (
            result[
                "items"
            ][
                :show_items
            ]
        ):
            click.echo(
                f"{item.get('title') or 'Untitled'}"
            )

            click.echo(
                f"  Date: "
                f"{_format_optional_date(item.get('published_at'))}"
            )

            click.echo(
                f"  URL:  "
                f"{item.get('url') or '-'}"
            )

            click.echo("")

    elif (
        result[
            "status"
        ]
        == "empty"
    ):
        click.echo(
            "The discovery document was readable, "
            "but no candidates survived the "
            "configured rules."
        )

        click.echo("")

    else:
        click.echo(
            "The candidate could not be discovered "
            "with this method/configuration."
        )

        click.echo("")

    click.echo(
        "This command is read-only."
    )

    click.echo(
        "No source was registered and no evidence "
        "was written to the database."
    )

    click.echo("")