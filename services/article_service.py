import json
import logging
import re

from datetime import (
    datetime,
    timezone,
)

from email.utils import (
    parsedate_to_datetime,
)

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

def _normalize_page_datetime(
    parsed,
):
    """
    Normalize a parsed page datetime to timezone-naive UTC.

    Article.published_at currently uses SQLAlchemy's
    timezone-naive DateTime column.
    """

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


def parse_page_datetime(value):
    """
    Parse a structured page-supplied publication datetime.

    Supported forms include common ISO-8601 values:

        2026-07-08
        2026-07-08T10:30:00
        2026-07-08T10:30:00Z
        2026-07-08T10:30:00+00:00

    and common machine-readable HTTP / RFC forms such as:

        Wed, 08 Jul 2026 10:30:00 GMT

    A small number of conventional publication-date formats
    are also accepted when they come from structured page
    elements:

        July 8, 2026
        Jul 8, 2026
        8 July 2026
        08 Jul 2026
        2026/07/08
        07/08/2026

    This helper is used only for explicitly identified
    publication-date metadata or semantic date elements.

    It is not used to scan arbitrary page prose.

    Returned datetimes are normalized to timezone-naive UTC.

    Invalid or missing values return None.
    """

    if not value:
        return None

    value = clean_text(
        str(
            value
        )
    )

    if not value:
        return None

    iso_value = value

    if iso_value.endswith(
        "Z"
    ):
        iso_value = (
            iso_value[
                :-1
            ]
            + "+00:00"
        )

    try:
        parsed = datetime.fromisoformat(
            iso_value
        )

        return _normalize_page_datetime(
            parsed
        )

    except ValueError:
        pass

    try:
        parsed = parsedate_to_datetime(
            value
        )

        if parsed is not None:
            return _normalize_page_datetime(
                parsed
            )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        pass

    structured_formats = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%A, %B %d, %Y",
        "%a, %B %d, %Y",
        "%A, %b %d, %Y",
        "%a, %b %d, %Y",
        "%Y/%m/%d",
        "%m/%d/%Y",
    ]

    for date_format in structured_formats:
        try:
            return datetime.strptime(
                value,
                date_format,
            )

        except ValueError:
            continue

    return None


def _find_json_ld_date(value):
    """
    Recursively search JSON-LD data for an explicit published
    date.

    datePublished is preferred.

    Some publishers use dateCreated when datePublished is
    absent. dateModified is deliberately not accepted because
    it may describe a later edit rather than publication.

    Returns the first parseable value found.
    """

    if isinstance(
        value,
        dict,
    ):
        for key in [
            "datePublished",
            "dateCreated",
        ]:
            date_value = value.get(
                key
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


def _extract_date_from_tag(
    tag,
    attributes,
):
    """
    Try a sequence of structured date-bearing attributes on one
    HTML tag.
    """

    if tag is None:
        return None

    for attribute in attributes:
        value = tag.get(
            attribute
        )

        parsed = parse_page_datetime(
            value
        )

        if parsed is not None:
            return parsed

    return None


def _extract_semantic_visible_date(
    soup,
):
    """
    Extract a publication date from short visible-text elements
    whose DOM attributes explicitly indicate date semantics.

    This is a conservative fallback for sites that expose a
    publication date visually but do not use standard metadata,
    JSON-LD, schema.org attributes, or <time> elements.

    Arbitrary page text is deliberately not scanned.
    """

    semantic_tokens = {
        "date",
        "published",
        "publication",
        "publishdate",
        "publish-date",
        "publisheddate",
        "published-date",
        "postdate",
        "post-date",
        "articledate",
        "article-date",
        "authordate",
        "author-date",
    }

    for tag in soup.find_all(True):
        attribute_values = []

        tag_id = tag.get(
            "id"
        )

        if tag_id:
            attribute_values.append(
                str(tag_id)
            )

        classes = tag.get(
            "class",
            [],
        )

        if isinstance(
            classes,
            str,
        ):
            classes = [
                classes
            ]

        attribute_values.extend(
            str(value)
            for value in classes
        )

        for key, value in (
            tag.attrs.items()
        ):
            normalized_key = (
                str(key)
                .strip()
                .lower()
            )

            if (
                "date" in normalized_key
                or "publish" in normalized_key
            ):
                attribute_values.append(
                    normalized_key
                )

                if isinstance(
                    value,
                    list,
                ):
                    attribute_values.extend(
                        str(item)
                        for item in value
                    )

                elif value:
                    attribute_values.append(
                        str(value)
                    )

        normalized_attributes = " ".join(
            attribute_values
        ).lower()

        normalized_compact = re.sub(
            r"[^a-z0-9]+",
            "",
            normalized_attributes,
        )

        has_date_semantics = any(
            (
                token in normalized_attributes
                or re.sub(
                    r"[^a-z0-9]+",
                    "",
                    token,
                ) in normalized_compact
            )
            for token in semantic_tokens
        )

        if not has_date_semantics:
            continue

        text = clean_text(
            tag.get_text(
                " ",
                strip=True,
            )
        )

        if not text:
            continue

        # Reject large containers whose class happens to contain
        # a date-related word. We only trust compact semantic
        # elements that plausibly represent a date label/value.
        if len(text) > 100:
            continue

        parsed = parse_page_datetime(
            text
        )

        if parsed is not None:
            return parsed

    return None


def extract_article_published_at(html):
    """
    Extract a reliable publication datetime from an HTML page.

    Preference order:

    1. explicit publication metadata
    2. schema.org / itemprop datePublished metadata
    3. JSON-LD datePublished / dateCreated
    4. semantic <time> elements
    5. explicit date-bearing attributes on semantic elements

    The function deliberately does not infer dates by scanning
    arbitrary visible page text.

    A visible date is accepted only when the website has
    explicitly marked the containing element as a semantic
    publication/date element.
    """

    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # -----------------------------------------------------
    # Explicit publication metadata
    # -----------------------------------------------------

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
                "property":
                    "og:article:published_time",
            },
        ),
        (
            "meta",
            {
                "name":
                    "date",
            },
        ),
        (
            "meta",
            {
                "name":
                    "pubdate",
            },
        ),
        (
            "meta",
            {
                "name":
                    "publish-date",
            },
        ),
        (
            "meta",
            {
                "name":
                    "published_date",
            },
        ),
        (
            "meta",
            {
                "name":
                    "datePublished",
            },
        ),
        (
            "meta",
            {
                "property":
                    "datePublished",
            },
        ),
        (
            "meta",
            {
                "itemprop":
                    "datePublished",
            },
        ),
        (
            "meta",
            {
                "itemprop":
                    "dateCreated",
            },
        ),
    ]

    for tag_name, attrs in meta_selectors:
        tags = soup.find_all(
            tag_name,
            attrs=attrs,
        )

        for tag in tags:
            parsed = (
                _extract_date_from_tag(
                    tag,
                    [
                        "content",
                        "datetime",
                        "value",
                    ],
                )
            )

            if parsed is not None:
                return parsed

    # -----------------------------------------------------
    # JSON-LD
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Semantic <time> elements
    # -----------------------------------------------------

    time_selectors = [
        "article time",
        "main time",
        "[role='main'] time",
        "time[itemprop='datePublished']",
        "time[itemprop='dateCreated']",
        "time",
    ]

    for selector in time_selectors:
        tags = soup.select(
            selector
        )

        for tag in tags:
            parsed = (
                _extract_date_from_tag(
                    tag,
                    [
                        "datetime",
                        "content",
                        "data-date",
                        "data-published",
                        "data-published-at",
                    ],
                )
            )

            if parsed is not None:
                return parsed

            # Visible text inside an actual semantic <time>
            # element is sufficiently explicit to parse.
            parsed = parse_page_datetime(
                tag.get_text(
                    " ",
                    strip=True,
                )
            )

            if parsed is not None:
                return parsed

    # -----------------------------------------------------
    # Explicit schema.org date elements
    # -----------------------------------------------------

    schema_date_selectors = [
        "[itemprop='datePublished']",
        "[itemprop='dateCreated']",
    ]

    for selector in schema_date_selectors:
        tags = soup.select(
            selector
        )

        for tag in tags:
            parsed = (
                _extract_date_from_tag(
                    tag,
                    [
                        "content",
                        "datetime",
                        "value",
                        "data-date",
                        "data-published",
                        "data-published-at",
                    ],
                )
            )

            if parsed is not None:
                return parsed

            parsed = parse_page_datetime(
                tag.get_text(
                    " ",
                    strip=True,
                )
            )

            if parsed is not None:
                return parsed

    # -----------------------------------------------------
    # Explicitly date-labelled visible elements
    # -----------------------------------------------------

    parsed = _extract_semantic_visible_date(
        soup
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
        return article.content

    if (
        not article.content
        and page[
            "content"
        ]
    ):
        article.content = page[
            "content"
        ]

    if (
        article.published_at
        is None
        and page[
            "published_at"
        ]
        is not None
    ):
        article.published_at = page[
            "published_at"
        ]

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
        before = article.published_at

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