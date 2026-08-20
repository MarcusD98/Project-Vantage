from datetime import (
    datetime,
    timezone,
)

from services.discovery_service import (
    _filter_sitemap_records,
    _limit_sitemap_records,
    _sort_sitemap_records,
)


def test_sort_sitemap_records_newest_first():
    records = [
        {
            "url":
                "https://example.com/old",
            "lastmod":
                datetime(
                    2026,
                    1,
                    1,
                    tzinfo=timezone.utc,
                ),
        },
        {
            "url":
                "https://example.com/new",
            "lastmod":
                datetime(
                    2026,
                    8,
                    1,
                    tzinfo=timezone.utc,
                ),
        },
        {
            "url":
                "https://example.com/middle",
            "lastmod":
                datetime(
                    2026,
                    5,
                    1,
                    tzinfo=timezone.utc,
                ),
        },
    ]

    result = _sort_sitemap_records(
        records
    )

    assert [
        record["url"]
        for record in result
    ] == [
        "https://example.com/new",
        "https://example.com/middle",
        "https://example.com/old",
    ]


def test_sort_sitemap_records_puts_missing_lastmod_last():
    records = [
        {
            "url":
                "https://example.com/unknown",
            "lastmod":
                None,
        },
        {
            "url":
                "https://example.com/known",
            "lastmod":
                datetime(
                    2026,
                    8,
                    1,
                    tzinfo=timezone.utc,
                ),
        },
    ]

    result = _sort_sitemap_records(
        records
    )

    assert (
        result[0]["url"]
        == "https://example.com/known"
    )

    assert (
        result[1]["url"]
        == "https://example.com/unknown"
    )


def test_limit_sitemap_records_applies_cap():
    records = [
        {
            "url":
                f"https://example.com/{index}",
            "lastmod":
                None,
        }
        for index in range(10)
    ]

    source = {
        "max_discovery_items": 3,
    }

    result = _limit_sitemap_records(
        records,
        source,
    )

    assert len(result) == 3


def test_limit_sitemap_records_without_cap_keeps_all():
    records = [
        {
            "url":
                f"https://example.com/{index}",
            "lastmod":
                None,
        }
        for index in range(5)
    ]

    result = _limit_sitemap_records(
        records,
        {},
    )

    assert len(result) == 5


def test_filter_sitemap_records_sorts_before_limiting():
    records = [
        {
            "url":
                "https://example.com/perspectives/old",
            "lastmod":
                datetime(
                    2026,
                    3,
                    1,
                    tzinfo=timezone.utc,
                ),
        },
        {
            "url":
                "https://example.com/perspectives/newest",
            "lastmod":
                datetime(
                    2026,
                    8,
                    19,
                    tzinfo=timezone.utc,
                ),
        },
        {
            "url":
                "https://example.com/perspectives/middle",
            "lastmod":
                datetime(
                    2026,
                    7,
                    1,
                    tzinfo=timezone.utc,
                ),
        },
    ]

    source = {
        "include_url_patterns": [
            "/perspectives/",
        ],
        "max_discovery_items": 2,
    }

    result = _filter_sitemap_records(
        records,
        source,
    )

    assert [
        record["url"]
        for record in result
    ] == [
        (
            "https://example.com/"
            "perspectives/newest"
        ),
        (
            "https://example.com/"
            "perspectives/middle"
        ),
    ]


def test_filter_sitemap_records_applies_url_rules_before_cap():
    records = [
        {
            "url":
                "https://example.com/team/person",
            "lastmod":
                datetime(
                    2026,
                    8,
                    20,
                    tzinfo=timezone.utc,
                ),
        },
        {
            "url":
                "https://example.com/perspectives/one",
            "lastmod":
                datetime(
                    2026,
                    8,
                    19,
                    tzinfo=timezone.utc,
                ),
        },
        {
            "url":
                "https://example.com/perspectives/two",
            "lastmod":
                datetime(
                    2026,
                    8,
                    18,
                    tzinfo=timezone.utc,
                ),
        },
    ]

    source = {
        "include_url_patterns": [
            "/perspectives/",
        ],
        "max_discovery_items": 1,
    }

    result = _filter_sitemap_records(
        records,
        source,
    )

    assert len(result) == 1

    assert (
        result[0]["url"]
        == (
            "https://example.com/"
            "perspectives/one"
        )
    )


def test_filter_sitemap_records_excludes_regex_matches():
    records = [
        {
            "url":
                "https://example.com/perspectives/2/",
            "lastmod":
                datetime(
                    2026,
                    8,
                    20,
                    tzinfo=timezone.utc,
                ),
        },
        {
            "url":
                (
                    "https://example.com/perspectives/"
                    "our-investment-in-company/"
                ),
            "lastmod":
                datetime(
                    2026,
                    8,
                    19,
                    tzinfo=timezone.utc,
                ),
        },
    ]

    source = {
        "include_url_patterns": [
            "/perspectives/",
        ],
        "exclude_url_regex_patterns": [
            r"/perspectives/\d+/$",
        ],
    }

    result = _filter_sitemap_records(
        records,
        source,
    )

    assert len(result) == 1

    assert result[0]["url"] == (
        "https://example.com/perspectives/"
        "our-investment-in-company/"
    )


def test_filter_sitemap_records_excludes_exact_landing_page():
    records = [
        {
            "url":
                "https://example.com/perspectives/",
            "lastmod":
                datetime(
                    2026,
                    8,
                    20,
                    tzinfo=timezone.utc,
                ),
        },
        {
            "url":
                (
                    "https://example.com/perspectives/"
                    "real-article/"
                ),
            "lastmod":
                datetime(
                    2026,
                    8,
                    19,
                    tzinfo=timezone.utc,
                ),
        },
    ]

    source = {
        "include_url_patterns": [
            "/perspectives/",
        ],
        "exclude_url_regex_patterns": [
            r"/perspectives/$",
        ],
    }

    result = _filter_sitemap_records(
        records,
        source,
    )

    assert len(result) == 1

    assert result[0]["url"] == (
        "https://example.com/perspectives/"
        "real-article/"
    )




