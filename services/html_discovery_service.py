from urllib.parse import (
    urljoin,
)

import requests

from bs4 import BeautifulSoup

from services.discovery_service import (
    REQUEST_HEADERS,
    _url_matches_source_rules,
)


def _build_page_url(
    source,
    page_number,
):
    """
    Build the listing URL for one configured page.

    Page 1 uses the source URL directly unless an explicit
    pagination pattern is configured for all pages.
    """

    pagination_pattern = source.get(
        "pagination_url_pattern"
    )

    if page_number == 1:
        return source["url"]

    if not pagination_pattern:
        return None

    return pagination_pattern.format(
        page=page_number
    )


def _extract_listing_links(
    html,
    page_url,
    source,
):
    """
    Extract normalized candidate links from one HTML listing.

    Website-specific structure remains configuration rather
    than Python implementation through link_selector.
    """

    if not html:
        return []

    link_selector = source.get(
        "link_selector",
        "a[href]",
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    items = []

    for element in soup.select(
        link_selector
    ):
        href = element.get(
            "href"
        )

        if not href:
            continue

        url = urljoin(
            page_url,
            href,
        )

        if not _url_matches_source_rules(
            url,
            source,
        ):
            continue

        title = element.get_text(
            " ",
            strip=True,
        )

        if not title:
            continue

        items.append(
            {
                "title": title,
                "url": url,
            }
        )

    return items


def _deduplicate_listing_items(
    items,
):
    """
    Deduplicate listing candidates by canonical URL while
    preserving discovery order.
    """

    seen_urls = set()
    unique = []

    for item in items:
        url = item["url"]

        if url in seen_urls:
            continue

        seen_urls.add(
            url
        )

        unique.append(
            item
        )

    return unique


def _limit_listing_items(
    items,
    source,
):
    """
    Apply an optional source-level discovery cap.
    """

    max_items = source.get(
        "max_discovery_items"
    )

    if max_items is None:
        return items

    try:
        max_items = int(
            max_items
        )

    except (
        TypeError,
        ValueError,
    ):
        return items

    if max_items <= 0:
        return []

    return items[
        :max_items
    ]


def discover_html_source(
    source,
):
    """
    Discover normalized evidence from paginated HTML listing
    pages.

    This adapter performs discovery only.

    It deliberately does not fetch every article page or infer
    publication dates. Actual page publication metadata remains
    the responsibility of the existing article enrichment
    pipeline.

    Supported source configuration:

        url
        link_selector
        pagination_url_pattern
        max_discovery_pages
        max_discovery_items
        include_url_patterns
        exclude_url_patterns
        exclude_url_regex_patterns
    """

    max_pages = source.get(
        "max_discovery_pages",
        1,
    )

    try:
        max_pages = int(
            max_pages
        )

    except (
        TypeError,
        ValueError,
    ):
        max_pages = 1

    if max_pages <= 0:
        return []

    discovered = []

    for page_number in range(
        1,
        max_pages + 1,
    ):
        page_url = _build_page_url(
            source,
            page_number,
        )

        if page_url is None:
            break

        try:
            response = requests.get(
                page_url,
                timeout=15,
                headers=REQUEST_HEADERS,
                allow_redirects=True,
            )

            response.raise_for_status()

        except requests.RequestException:
            continue

        page_items = (
            _extract_listing_links(
                response.text,
                page_url,
                source,
            )
        )

        discovered.extend(
            page_items
        )

        discovered = (
            _deduplicate_listing_items(
                discovered
            )
        )

        max_items = source.get(
            "max_discovery_items"
        )

        if (
            max_items is not None
            and len(discovered)
            >= int(max_items)
        ):
            break

    discovered = (
        _limit_listing_items(
            discovered,
            source,
        )
    )

    return [
        {
            "title":
                item["title"],

            "url":
                item["url"],

            "published_at":
                None,

            "summary":
                "",

            "source":
                source.get(
                    "canonical_source",
                    source["name"],
                ),

            "source_type":
                source.get(
                    "type",
                    "publication",
                ),

            "discovery_method":
                "html",
        }
        for item in discovered
    ]