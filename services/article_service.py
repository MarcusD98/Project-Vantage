import json
import logging
import re

from datetime import datetime, timezone

import requests

from bs4 import BeautifulSoup

from models.article import Article


logger = logging.getLogger(__name__)


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


MIN_CONTENT_LENGTH = 300


# ---------------------------------------------------------
# Shared text helpers
# ---------------------------------------------------------

def clean_text(text):
    if not text:
        return None

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ---------------------------------------------------------
# Publication-date extraction
# ---------------------------------------------------------

def parse_page_datetime(value):
    """
    Parse a page-supplied publication datetime.

    HTML metadata commonly uses ISO-8601 values such as:

        2026-07-08
        2026-07-08T10:30:00
        2026-07-08T10:30:00Z
        2026-07-08T10:30:00+00:00

    Returned datetimes are normalized to timezone-naive UTC
    because Article.published_at currently uses SQLAlchemy's
    timezone-naive DateTime column.

    Invalid or missing values return None.
    """

    if not value:
        return None

    value = value.strip()

    if not value:
        return None

    try:
        if value.endswith("Z"):
            value = (
                value[:-1]
                + "+00:00"
            )

        parsed = datetime.fromisoformat(
            value
        )

    except ValueError:
        return None

    if parsed.tzinfo is not None:
        parsed = (
            parsed
            .astimezone(
                timezone.utc
            )
            .replace(
                tzinfo=None
            )
        )

    return parsed


def _find_json_ld_date(value):
    """
    Recursively search JSON-LD data for datePublished.

    Returns the first parseable value found.
    """

    if isinstance(
        value,
        dict,
    ):
        date_value = value.get(
            "datePublished"
        )

        parsed = parse_page_datetime(
            date_value
        )

        if parsed is not None:
            return parsed

        for child in value.values():
            parsed = _find_json_ld_date(
                child
            )

            if parsed is not None:
                return parsed

    elif isinstance(
        value,
        list,
    ):
        for child in value:
            parsed = _find_json_ld_date(
                child
            )

            if parsed is not None:
                return parsed

    return None


def extract_article_published_at(html):
    """
    Extract a reliable publication datetime from an HTML page.

    Preference order:

    1. article:published_time metadata
    2. other explicit publication-date metadata
    3. JSON-LD datePublished
    4. semantic <time datetime="..."> elements

    The function deliberately does not infer dates from
    arbitrary visible text.
    """

    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    meta_selectors = [
        (
            "meta",
            {
                "property":
                    "article:published_time",
            },
        ),
        (
            "meta",
            {
                "name":
                    "article:published_time",
            },
        ),
        (
            "meta",
            {
                "property":
                    "og:published_time",
            },
        ),
        (
            "meta",
            {
                "name": "date",
            },
        ),
        (
            "meta",
            {
                "name": "pubdate",
            },
        ),
        (
            "meta",
            {
                "name": "publish-date",
            },
        ),
        (
            "meta",
            {
                "name": "published_date",
            },
        ),
    ]

    for tag_name, attrs in meta_selectors:
        tag = soup.find(
            tag_name,
            attrs=attrs,
        )

        if tag is None:
            continue

        parsed = parse_page_datetime(
            tag.get(
                "content"
            )
        )

        if parsed is not None:
            return parsed

    # JSON-LD is common on modern article and news pages.
    json_ld_tags = soup.find_all(
        "script",
        attrs={
            "type":
                "application/ld+json",
        },
    )

    for tag in json_ld_tags:
        raw_json = tag.string

        if not raw_json:
            raw_json = tag.get_text(
                strip=True
            )

        if not raw_json:
            continue

        try:
            data = json.loads(
                raw_json
            )

        except (
            json.JSONDecodeError,
            TypeError,
        ):
            continue

        parsed = _find_json_ld_date(
            data
        )

        if parsed is not None:
            return parsed

    # Prefer a time element inside article/main content before
    # falling back to any time element on the page.
    time_selectors = [
        "article time[datetime]",
        "main time[datetime]",
        "[role='main'] time[datetime]",
        "time[datetime]",
    ]

    for selector in time_selectors:
        tag = soup.select_one(
            selector
        )

        if tag is None:
            continue

        parsed = parse_page_datetime(
            tag.get(
                "datetime"
            )
        )

        if parsed is not None:
            return parsed

    return None


# ---------------------------------------------------------
# Article-body extraction
# ---------------------------------------------------------

def extract_paragraphs(container):
    paragraphs = container.find_all(
        "p"
    )

    text_parts = []
    seen = set()

    for paragraph in paragraphs:
        text = clean_text(
            paragraph.get_text(
                " ",
                strip=True,
            )
        )

        if not text:
            continue

        if len(text) < 25:
            continue

        if text in seen:
            continue

        seen.add(
            text
        )

        text_parts.append(
            text
        )

    if not text_parts:
        return None

    return "\n".join(
        text_parts
    )


def extract_article_content(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "form",
            "nav",
            "footer",
            "aside",
        ]
    ):
        tag.decompose()

    candidate_selectors = [
        "article",
        "main",
        "[role='main']",
        ".article-content",
        ".article-body",
        ".post-content",
        ".post-body",
        ".entry-content",
        ".story-body",
        ".story-content",
    ]

    for selector in candidate_selectors:
        container = soup.select_one(
            selector
        )

        if container is None:
            continue

        content = extract_paragraphs(
            container
        )

        if (
            content
            and len(content)
            >= MIN_CONTENT_LENGTH
        ):
            return content

    content = extract_paragraphs(
        soup
    )

    if (
        content
        and len(content)
        >= MIN_CONTENT_LENGTH
    ):
        return content

    return None


# ---------------------------------------------------------
# Page retrieval
# ---------------------------------------------------------

def fetch_article_html(url):
    """
    Retrieve an HTML article/document page.

    Returns raw HTML when successful, otherwise None.
    """

    try:
        response = requests.get(
            url,
            timeout=15,
            headers=REQUEST_HEADERS,
            allow_redirects=True,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        logger.warning(
            "Could not fetch article page: %s (%s)",
            url,
            exc,
        )

        return None

    content_type = response.headers.get(
        "Content-Type",
        "",
    ).lower()

    if (
        content_type
        and "html" not in content_type
    ):
        logger.warning(
            "Article URL did not return HTML: %s",
            url,
        )

        return None

    return response.text


def extract_article_page_data(html):
    """
    Extract normalized page-level data from one HTML document.

    Content and publication date are deliberately extracted
    independently: a page may yield one even when the other
    cannot be recovered.
    """

    return {
        "content":
            extract_article_content(
                html
            ),

        "published_at":
            extract_article_published_at(
                html
            ),
    }


def fetch_article_page(url):
    """
    Retrieve and parse one article/document page.

    Returns:
        {
            "content": str | None,
            "published_at": datetime | None,
        }

    Returns None when the page itself cannot be retrieved.
    """

    html = fetch_article_html(
        url
    )

    if html is None:
        return None

    return extract_article_page_data(
        html
    )


def fetch_article_content(url):
    """
    Backwards-compatible content-only retrieval helper.
    """

    page = fetch_article_page(
        url
    )

    if page is None:
        return None

    content = page[
        "content"
    ]

    if not content:
        logger.warning(
            "Could not extract useful article content: %s",
            url,
        )

        return None

    return content


# ---------------------------------------------------------
# Article enrichment
# ---------------------------------------------------------

def populate_article_content(article):
    """
    Enrich an Article from its source page.

    Populates missing:

    - Article.content
    - Article.published_at

    Existing values are preserved.

    Transaction ownership belongs to the caller. This function
    deliberately does not commit.
    """

    # Nothing left to enrich.
    if (
        article.content
        and article.published_at
        is not None
    ):
        return article.content

    page = fetch_article_page(
        article.url
    )

    if page is None:
        # Preserve historical behavior for an article whose
        # content was already stored.
        return article.content

    if (
        not article.content
        and page["content"]
    ):
        article.content = (
            page["content"]
        )

    if (
        article.published_at is None
        and page["published_at"]
        is not None
    ):
        article.published_at = (
            page["published_at"]
        )

    return article.content


def populate_missing_article_content(
    limit=10,
):
    """
    Populate page data for a batch of articles missing body
    content.

    Publication dates may also be enriched during the same
    HTTP request.

    This helper mutates records in the current session but
    does not commit.
    """

    articles = (
        Article.query
        .filter(
            Article.content.is_(
                None
            )
        )
        .limit(
            limit
        )
        .all()
    )

    populated_count = 0

    for article in articles:
        content = (
            populate_article_content(
                article
            )
        )

        if content:
            populated_count += 1

    return populated_count


def populate_missing_article_dates(
    source=None,
    limit=100,
):
    """
    Enrich publication dates for persisted Articles whose
    published_at value is missing.

    Optionally restrict the operation to one source.

    Existing content may be reused, but the source page still
    needs to be fetched because publication metadata was not
    historically stored.

    Transaction ownership belongs to the caller.
    """

    query = Article.query.filter(
        Article.published_at.is_(
            None
        )
    )

    if source:
        query = query.filter_by(
            source=source
        )

    articles = (
        query
        .limit(
            limit
        )
        .all()
    )

    populated_count = 0

    for article in articles:
        before = (
            article.published_at
        )

        populate_article_content(
            article
        )

        if (
            before is None
            and article.published_at
            is not None
        ):
            populated_count += 1

    return populated_count