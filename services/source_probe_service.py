from services.discovery_service import (
    discover_source,
)


SUPPORTED_PROBE_METHODS = {
    "rss",
    "sitemap",
    "html",
}


def _clean_patterns(values):
    if not values:
        return []

    result = []

    for value in values:
        value = str(
            value
        ).strip()

        if value:
            result.append(
                value
            )

    return result


def probe_source_candidate(
    *,
    name,
    method,
    url,
    source_type="investor",
    link_selector=None,
    include_url_patterns=None,
    exclude_url_patterns=None,
    exclude_url_regex_patterns=None,
    sitemap_include_patterns=None,
    max_discovery_items=50,
    max_discovery_pages=1,
):
    """
    Run one candidate source through Vantage's existing generic
    discovery layer without requiring registry configuration and
    without writing anything to the database.

    This is a compatibility probe, not source onboarding.

    The purpose is to answer:

        Can Vantage already discover useful evidence from this
        source using an existing generic acquisition method?
    """

    name = str(
        name
    ).strip()

    method = (
        str(
            method
        )
        .strip()
        .lower()
    )

    url = str(
        url
    ).strip()

    if not name:
        raise ValueError(
            "name is required."
        )

    if (
        method
        not in SUPPORTED_PROBE_METHODS
    ):
        raise ValueError(
            "Unsupported probe method: "
            f"{method}"
        )

    if not url:
        raise ValueError(
            "url is required."
        )

    try:
        max_discovery_items = int(
            max_discovery_items
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "max_discovery_items must be an integer."
        ) from exc

    if max_discovery_items <= 0:
        raise ValueError(
            "max_discovery_items must be greater than zero."
        )

    try:
        max_discovery_pages = int(
            max_discovery_pages
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "max_discovery_pages must be an integer."
        ) from exc

    if max_discovery_pages <= 0:
        raise ValueError(
            "max_discovery_pages must be greater than zero."
        )

    source = {
        "name":
            name,

        "type":
            source_type,

        "method":
            method,

        "url":
            url,

        "max_discovery_items":
            max_discovery_items,

        "max_discovery_pages":
            max_discovery_pages,
    }

    if link_selector:
        source[
            "link_selector"
        ] = str(
            link_selector
        ).strip()

    include_patterns = (
        _clean_patterns(
            include_url_patterns
        )
    )

    exclude_patterns = (
        _clean_patterns(
            exclude_url_patterns
        )
    )

    exclude_regex = (
        _clean_patterns(
            exclude_url_regex_patterns
        )
    )

    sitemap_patterns = (
        _clean_patterns(
            sitemap_include_patterns
        )
    )

    if include_patterns:
        source[
            "include_url_patterns"
        ] = include_patterns

    if exclude_patterns:
        source[
            "exclude_url_patterns"
        ] = exclude_patterns

    if exclude_regex:
        source[
            "exclude_url_regex_patterns"
        ] = exclude_regex

    if sitemap_patterns:
        source[
            "sitemap_include_patterns"
        ] = sitemap_patterns

    items = (
        discover_source(
            source
        )
    )

    if items is None:
        return {
            "name":
                name,

            "method":
                method,

            "url":
                url,

            "status":
                "failed",

            "discovered":
                0,

            "dated":
                0,

            "undated":
                0,

            "items":
                [],

            "source_config":
                source,
        }

    dated = sum(
        1
        for item
        in items
        if item.get(
            "published_at"
        )
        is not None
    )

    discovered = len(
        items
    )

    status = (
        "productive"
        if discovered > 0
        else "empty"
    )

    return {
        "name":
            name,

        "method":
            method,

        "url":
            url,

        "status":
            status,

        "discovered":
            discovered,

        "dated":
            dated,

        "undated":
            discovered - dated,

        "items":
            items,

        "source_config":
            source,
    }