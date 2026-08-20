from datetime import datetime, timezone

from services.discovery_service import (
    _extract_sitemap_urls,
    _sitemap_record_is_recent,
    _title_from_url,
    _url_matches_source_rules,
    clean_summary,
    discover_source,
    parse_iso_datetime,
    parse_rss_date,
)

from services.news_service import (
    deduplicate_articles,
    filter_vc_articles,
    sort_articles_by_date,
)


def test_clean_summary_removes_html():
    raw_summary = (
        "<p>Startup raises "
        "<strong>$50M.</strong></p>"
    )

    result = clean_summary(
        raw_summary
    )

    assert (
        result
        == "Startup raises $50M."
    )


def test_parse_rss_date_returns_datetime():
    result = parse_rss_date(
        "Mon, 17 Aug 2026 10:00:00 +0000"
    )

    assert isinstance(
        result,
        datetime,
    )

    assert result.year == 2026


def test_parse_rss_date_returns_none_for_invalid_date():
    result = parse_rss_date(
        "not a real date"
    )

    assert result is None


def test_parse_iso_datetime_date():
    result = parse_iso_datetime(
        "2026-08-17"
    )

    assert isinstance(
        result,
        datetime,
    )

    assert result.year == 2026
    assert result.month == 8
    assert result.day == 17


def test_parse_iso_datetime_with_z_timezone():
    result = parse_iso_datetime(
        "2026-08-17T10:30:00Z"
    )

    assert isinstance(
        result,
        datetime,
    )

    assert (
        result.utcoffset()
        is not None
    )


def test_extract_urlset_sitemap():
    xml = """
    <?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/post-one</loc>
            <lastmod>2026-08-17</lastmod>
        </url>
        <url>
            <loc>https://example.com/post-two</loc>
        </url>
    </urlset>
    """

    result = _extract_sitemap_urls(
        xml
    )

    assert (
        result["type"]
        == "urlset"
    )

    assert (
        len(result["items"])
        == 2
    )

    assert (
        result["items"][0]["url"]
        == "https://example.com/post-one"
    )

    assert isinstance(
        result["items"][0][
            "lastmod"
        ],
        datetime,
    )

    assert (
        result["items"][1][
            "lastmod"
        ]
        is None
    )


def test_extract_sitemap_index():
    xml = """
    <?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap>
            <loc>
                https://example.com/post-sitemap.xml
            </loc>
        </sitemap>
        <sitemap>
            <loc>
                https://example.com/page-sitemap.xml
            </loc>
        </sitemap>
    </sitemapindex>
    """

    result = _extract_sitemap_urls(
        xml
    )

    assert (
        result["type"]
        == "sitemapindex"
    )

    assert (
        len(result["items"])
        == 2
    )


def test_url_rules_keep_matching_url():
    source = {
        "include_url_patterns": [
            "/insights/",
        ],
        "exclude_url_patterns": [],
    }

    assert _url_matches_source_rules(
        "https://example.com/insights/acme",
        source,
    )


def test_url_rules_reject_non_matching_url():
    source = {
        "include_url_patterns": [
            "/insights/",
        ],
        "exclude_url_patterns": [],
    }

    assert not _url_matches_source_rules(
        "https://example.com/team/person",
        source,
    )


def test_url_rules_apply_exclusions():
    source = {
        "include_url_patterns": [],
        "exclude_url_patterns": [
            "/team/",
        ],
    }

    assert not _url_matches_source_rules(
        "https://example.com/team/person",
        source,
    )


def test_sitemap_recency_keeps_recent_record():
    source = {
        "max_age_days": 180,
    }

    record = {
        "lastmod": datetime.now(
            timezone.utc
        ),
    }

    assert _sitemap_record_is_recent(
        record,
        source,
    )


def test_sitemap_recency_rejects_old_record():
    source = {
        "max_age_days": 180,
    }

    record = {
        "lastmod": datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    }

    assert not _sitemap_record_is_recent(
        record,
        source,
    )


def test_sitemap_recency_keeps_unknown_date():
    source = {
        "max_age_days": 180,
    }

    record = {
        "lastmod": None,
    }

    assert _sitemap_record_is_recent(
        record,
        source,
    )


def test_title_from_url():
    result = _title_from_url(
        "https://example.com/"
        "our-investment-in-acme"
    )

    assert (
        result
        == "our investment in acme"
    )


def test_deduplicate_articles_removes_duplicate_urls():
    articles = [
        {
            "title": "Startup raises $50M",
            "url": "https://example.com/article-1",
        },
        {
            "title": "Startup raises $50M",
            "url": "https://example.com/article-1",
        },
        {
            "title": (
                "Another startup raises $20M"
            ),
            "url": "https://example.com/article-2",
        },
    ]

    result = deduplicate_articles(
        articles
    )

    assert len(result) == 2


def test_filter_vc_articles_keeps_relevant_publication_articles():
    articles = [
        {
            "title": (
                "Startup raises $100M Series C"
            ),
            "source_type": "publication",
        },
        {
            "title": (
                "Company launches new mobile app"
            ),
            "source_type": "publication",
        },
        {
            "title": (
                "New VC fund targets "
                "European fintech"
            ),
            "source_type": "publication",
        },
    ]

    result = filter_vc_articles(
        articles
    )

    assert len(result) == 2

    assert (
        result[0]["title"]
        == "Startup raises $100M Series C"
    )

    assert (
        result[1]["title"]
        == (
            "New VC fund targets "
            "European fintech"
        )
    )


def test_filter_vc_articles_keeps_investor_evidence():
    articles = [
        {
            "title": (
                "Partnering with Acme"
            ),
            "source_type": "investor",
        },
        {
            "title": (
                "Building the future of robotics"
            ),
            "source_type": "investor",
        },
    ]

    result = filter_vc_articles(
        articles
    )

    assert len(result) == 2


def test_sort_articles_by_date_newest_first():
    articles = [
        {
            "title": "Older article",
            "published_at": datetime(
                2026,
                8,
                17,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        },
        {
            "title": "Newest article",
            "published_at": datetime(
                2026,
                8,
                17,
                15,
                0,
                tzinfo=timezone.utc,
            ),
        },
        {
            "title": "Middle article",
            "published_at": datetime(
                2026,
                8,
                17,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        },
    ]

    result = sort_articles_by_date(
        articles
    )

    assert (
        result[0]["title"]
        == "Newest article"
    )

    assert (
        result[1]["title"]
        == "Middle article"
    )

    assert (
        result[2]["title"]
        == "Older article"
    )


def test_sort_articles_preserves_undated_items():
    articles = [
        {
            "title": "Undated article",
            "published_at": None,
        },
        {
            "title": "Dated article",
            "published_at": datetime(
                2026,
                8,
                17,
                tzinfo=timezone.utc,
            ),
        },
    ]

    result = sort_articles_by_date(
        articles
    )

    assert len(result) == 2

    assert (
        result[0]["title"]
        == "Dated article"
    )

    assert (
        result[1]["title"]
        == "Undated article"
    )


def test_discover_source_rejects_unknown_method():
    source = {
        "name": "Unsupported Source",
        "url": "https://example.com",
        "type": "publication",
        "region": "Global",
        "method": "something_else",
        "enabled": True,
    }

    result = discover_source(
        source
    )

    assert result is None