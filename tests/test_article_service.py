from datetime import datetime
from types import SimpleNamespace

from services import article_service

from services.article_service import (
    extract_article_page_data,
    extract_article_published_at,
    parse_page_datetime,
    populate_article_content,
)


LONG_PARAGRAPH = (
    "This is a sufficiently long article paragraph used "
    "to exercise the generic Vantage article extraction "
    "pipeline during automated tests. It contains enough "
    "text to pass the minimum content threshold. "
) * 4


def test_parse_page_datetime_iso_date():
    result = parse_page_datetime(
        "2026-07-08"
    )

    assert result == datetime(
        2026,
        7,
        8,
    )


def test_parse_page_datetime_normalizes_utc():
    result = parse_page_datetime(
        "2026-07-08T12:30:00Z"
    )

    assert result == datetime(
        2026,
        7,
        8,
        12,
        30,
    )

    assert result.tzinfo is None


def test_parse_page_datetime_rfc_date():
    result = parse_page_datetime(
        "Wed, 08 Jul 2026 10:30:00 GMT"
    )

    assert result == datetime(
        2026,
        7,
        8,
        10,
        30,
    )


def test_parse_page_datetime_human_structured_date():
    result = parse_page_datetime(
        "July 8, 2026"
    )

    assert result == datetime(
        2026,
        7,
        8,
    )


def test_parse_page_datetime_day_first_date():
    result = parse_page_datetime(
        "8 July 2026"
    )

    assert result == datetime(
        2026,
        7,
        8,
    )


def test_parse_page_datetime_invalid_returns_none():
    result = parse_page_datetime(
        "not-a-date"
    )

    assert result is None


def test_extract_published_at_from_article_meta():
    html = """
    <html>
        <head>
            <meta
                property="article:published_time"
                content="2026-07-08T10:30:00Z"
            >
        </head>
        <body></body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result == datetime(
        2026,
        7,
        8,
        10,
        30,
    )


def test_extract_published_at_from_itemprop_meta():
    html = """
    <html>
        <head>
            <meta
                itemprop="datePublished"
                content="July 8, 2026"
            >
        </head>
        <body></body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result == datetime(
        2026,
        7,
        8,
    )


def test_extract_published_at_from_json_ld():
    html = """
    <html>
        <head>
            <script type="application/ld+json">
                {
                    "@context":
                        "https://schema.org",
                    "@type":
                        "NewsArticle",
                    "datePublished":
                        "2026-06-18T09:15:00+00:00"
                }
            </script>
        </head>
        <body></body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result == datetime(
        2026,
        6,
        18,
        9,
        15,
    )


def test_extract_published_at_from_nested_json_ld_graph():
    html = """
    <html>
        <head>
            <script type="application/ld+json">
                {
                    "@context":
                        "https://schema.org",
                    "@graph": [
                        {
                            "@type":
                                "Organization",
                            "name":
                                "Example"
                        },
                        {
                            "@type":
                                "Article",
                            "datePublished":
                                "2026-04-12"
                        }
                    ]
                }
            </script>
        </head>
        <body></body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result == datetime(
        2026,
        4,
        12,
    )


def test_extract_published_at_from_json_ld_date_created():
    html = """
    <html>
        <head>
            <script type="application/ld+json">
                {
                    "@context":
                        "https://schema.org",
                    "@type":
                        "Article",
                    "dateCreated":
                        "2026-03-05"
                }
            </script>
        </head>
        <body></body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result == datetime(
        2026,
        3,
        5,
    )


def test_json_ld_does_not_use_date_modified_as_publication():
    html = """
    <html>
        <head>
            <script type="application/ld+json">
                {
                    "@context":
                        "https://schema.org",
                    "@type":
                        "Article",
                    "dateModified":
                        "2026-08-20"
                }
            </script>
        </head>
        <body></body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result is None


def test_extract_published_at_from_time_element():
    html = """
    <html>
        <body>
            <article>
                <time datetime="2026-05-26">
                    May 26, 2026
                </time>
            </article>
        </body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result == datetime(
        2026,
        5,
        26,
    )


def test_extract_published_at_from_time_visible_text():
    html = """
    <html>
        <body>
            <article>
                <time>
                    July 8, 2026
                </time>
            </article>
        </body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result == datetime(
        2026,
        7,
        8,
    )


def test_extract_published_at_from_time_data_attribute():
    html = """
    <html>
        <body>
            <main>
                <time
                    data-published-at="2026-02-14"
                >
                    Publication date
                </time>
            </main>
        </body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result == datetime(
        2026,
        2,
        14,
    )


def test_extract_published_at_from_schema_visible_text():
    html = """
    <html>
        <body>
            <span itemprop="datePublished">
                8 July 2026
            </span>
        </body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result == datetime(
        2026,
        7,
        8,
    )


def test_extract_published_at_does_not_guess_visible_text():
    html = """
    <html>
        <body>
            <article>
                <p>
                    Published July 8, 2026
                </p>
            </article>
        </body>
    </html>
    """

    result = extract_article_published_at(
        html
    )

    assert result is None


def test_extract_article_page_data():
    html = f"""
    <html>
        <head>
            <meta
                property="article:published_time"
                content="2026-07-08"
            >
        </head>

        <body>
            <article>
                <p>
                    {LONG_PARAGRAPH}
                </p>
            </article>
        </body>
    </html>
    """

    result = extract_article_page_data(
        html
    )

    assert result[
        "published_at"
    ] == datetime(
        2026,
        7,
        8,
    )

    assert result[
        "content"
    ] is not None


def test_populate_article_content_enriches_missing_date(
    monkeypatch,
):
    article = SimpleNamespace(
        url="https://example.com/article",
        content=None,
        published_at=None,
    )

    page = {
        "content":
            LONG_PARAGRAPH,

        "published_at":
            datetime(
                2026,
                7,
                8,
            ),
    }

    monkeypatch.setattr(
        article_service,
        "fetch_article_page",
        lambda url: page,
    )

    result = populate_article_content(
        article
    )

    assert result == LONG_PARAGRAPH

    assert (
        article.content
        == LONG_PARAGRAPH
    )

    assert (
        article.published_at
        == datetime(
            2026,
            7,
            8,
        )
    )


def test_populate_article_content_preserves_existing_date(
    monkeypatch,
):
    existing_date = datetime(
        2026,
        7,
        1,
    )

    article = SimpleNamespace(
        url="https://example.com/article",
        content=None,
        published_at=existing_date,
    )

    page = {
        "content":
            LONG_PARAGRAPH,

        "published_at":
            datetime(
                2026,
                7,
                8,
            ),
    }

    monkeypatch.setattr(
        article_service,
        "fetch_article_page",
        lambda url: page,
    )

    populate_article_content(
        article
    )

    assert (
        article.published_at
        == existing_date
    )


def test_existing_content_can_still_gain_missing_date(
    monkeypatch,
):
    article = SimpleNamespace(
        url="https://example.com/article",
        content=LONG_PARAGRAPH,
        published_at=None,
    )

    page = {
        "content":
            LONG_PARAGRAPH,

        "published_at":
            datetime(
                2026,
                7,
                8,
            ),
    }

    monkeypatch.setattr(
        article_service,
        "fetch_article_page",
        lambda url: page,
    )

    result = populate_article_content(
        article
    )

    assert result == LONG_PARAGRAPH

    assert (
        article.published_at
        == datetime(
            2026,
            7,
            8,
        )
    )