from services.discovery_service import (
    discover_source,
)

from services.news_service import (
    clean_summary,
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


def test_filter_vc_articles_keeps_relevant_articles():
    articles = [
        {
            "title": (
                "Startup raises $100M Series C"
            ),
        },
        {
            "title": (
                "Company launches new mobile app"
            ),
        },
        {
            "title": (
                "New VC fund targets "
                "European fintech"
            ),
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


def test_sort_articles_by_date_newest_first():
    articles = [
        {
            "title": "Older article",
            "published_at": (
                "Mon, 17 Aug 2026 "
                "10:00:00 +0000"
            ),
        },
        {
            "title": "Newest article",
            "published_at": (
                "Mon, 17 Aug 2026 "
                "15:00:00 +0000"
            ),
        },
        {
            "title": "Middle article",
            "published_at": (
                "Mon, 17 Aug 2026 "
                "12:00:00 +0000"
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