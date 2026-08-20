from services.html_discovery_service import (
    _build_page_url,
    _deduplicate_listing_items,
    _extract_listing_links,
    _limit_listing_items,
)


def test_build_first_page_uses_source_url():
    source = {
        "url": "https://example.com/archive/",
        "pagination_url_pattern": (
            "https://example.com/archive/page/{page}/"
        ),
    }

    assert (
        _build_page_url(
            source,
            1,
        )
        == "https://example.com/archive/"
    )


def test_build_paginated_page_url():
    source = {
        "url": "https://example.com/archive/",
        "pagination_url_pattern": (
            "https://example.com/archive/page/{page}/"
        ),
    }

    assert (
        _build_page_url(
            source,
            3,
        )
        == "https://example.com/archive/page/3/"
    )


def test_extract_listing_links():
    html = """
    <html>
        <body>
            <h3>
                <a href="/2026/08/20/acme-raises/">
                    Acme raises $20M
                </a>
            </h3>

            <h3>
                <a href="/2026/08/19/other-story/">
                    Other story
                </a>
            </h3>
        </body>
    </html>
    """

    source = {
        "link_selector": "h3 a",
        "include_url_patterns": [
            "/2026/",
        ],
    }

    result = _extract_listing_links(
        html,
        "https://example.com/2026/",
        source,
    )

    assert len(result) == 2

    assert (
        result[0]["title"]
        == "Acme raises $20M"
    )

    assert (
        result[0]["url"]
        == (
            "https://example.com/"
            "2026/08/20/acme-raises/"
        )
    )


def test_extract_listing_links_applies_exclusion():
    html = """
    <h3>
        <a href="/2026/page/2/">
            Archive Page
        </a>
    </h3>

    <h3>
        <a href="/2026/08/20/acme-raises/">
            Acme raises $20M
        </a>
    </h3>
    """

    source = {
        "link_selector": "h3 a",
        "include_url_patterns": [
            "/2026/",
        ],
        "exclude_url_patterns": [
            "/page/",
        ],
    }

    result = _extract_listing_links(
        html,
        "https://example.com/2026/",
        source,
    )

    assert len(result) == 1

    assert (
        result[0]["title"]
        == "Acme raises $20M"
    )


def test_deduplicate_listing_items():
    items = [
        {
            "title": "Acme",
            "url": "https://example.com/acme",
        },
        {
            "title": "Acme duplicate",
            "url": "https://example.com/acme",
        },
    ]

    result = (
        _deduplicate_listing_items(
            items
        )
    )

    assert len(result) == 1

    assert (
        result[0]["title"]
        == "Acme"
    )


def test_limit_listing_items():
    items = [
        {
            "title": f"Article {index}",
            "url": (
                f"https://example.com/{index}"
            ),
        }
        for index in range(10)
    ]

    source = {
        "max_discovery_items": 3,
    }

    result = _limit_listing_items(
        items,
        source,
    )

    assert len(result) == 3