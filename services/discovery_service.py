import re
import logging

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from email.utils import (
    parsedate_to_datetime,
)

from xml.etree import ElementTree

import feedparser
import requests

from bs4 import BeautifulSoup


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


# ---------------------------------------------------------
# Shared normalization helpers
# ---------------------------------------------------------

def clean_summary(summary):
    """
    Convert source-supplied HTML summaries into clean text.
    """

    if not summary:
        return ""

    soup = BeautifulSoup(
        summary,
        "html.parser",
    )

    return soup.get_text(
        " ",
        strip=True,
    )


def parse_rss_date(value):
    """
    Convert an RSS-style publication date into a Python
    datetime.

    Invalid or missing dates return None.
    """

    if not value:
        return None

    try:
        return parsedate_to_datetime(
            value
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return None


def parse_iso_datetime(value):
    """
    Parse common ISO-8601 datetime values.

    Sitemap <lastmod> values commonly use ISO-8601 dates or
    datetimes.

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

        return datetime.fromisoformat(
            value
        )

    except ValueError:
        return None


def fetch_source_document(url):
    """
    Retrieve a source-discovery document.

    Used for XML sitemaps and later reusable discovery
    methods.

    Returns response text when successful, otherwise None.
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
            "Could not fetch discovery document: %s (%s)",
            url,
            exc,
        )

        return None

    return response.text


# ---------------------------------------------------------
# RSS discovery
# ---------------------------------------------------------

def fetch_rss_feed(feed_url):
    """
    Fetch and parse an RSS feed.

    A malformed-but-readable feed may still be usable.
    """

    feed = feedparser.parse(
        feed_url
    )

    if feed.bozo:
        logger.warning(
            "Problem parsing RSS feed: %s",
            feed_url,
        )

    if not feed.entries:
        logger.warning(
            "No entries found in RSS feed: %s",
            feed_url,
        )

        return None

    return feed


def discover_rss_source(source):
    """
    Discover normalized evidence items from one RSS source.
    """

    feed = fetch_rss_feed(
        source["url"]
    )

    if feed is None:
        return None

    items = []

    for entry in feed.entries:
        url = entry.get(
            "link",
            "",
        )

        if not url:
            continue

        items.append(
            {
                "title": entry.get(
                    "title",
                    "Untitled article",
                ),
                "url": url,
                "published_at":
                    parse_rss_date(
                        entry.get(
                            "published",
                            "",
                        )
                    ),
                "summary":
                    clean_summary(
                        entry.get(
                            "summary",
                            "",
                        )
                    ),
                "source":
                    source["name"],
                "source_type":
                    source.get(
                        "type",
                        "publication",
                    ),
                "discovery_method":
                    "rss",
            }
        )

    return items


# ---------------------------------------------------------
# Sitemap discovery
# ---------------------------------------------------------

def _extract_sitemap_urls(xml):
    """
    Extract URL records from one XML sitemap.

    Supports both:

    - standard <urlset> sitemaps
    - <sitemapindex> files that point to child sitemaps

    Sitemap <lastmod> is retained only as discovery metadata.
    It is not treated as the publication date of the page.

    Returns:
        {
            "type":
                "urlset" | "sitemapindex" | None,
            "items":
                [...]
        }
    """

    if not xml:
        return {
            "type": None,
            "items": [],
        }

    try:
        root = ElementTree.fromstring(
            xml.strip()
        )

    except ElementTree.ParseError:
        return {
            "type": None,
            "items": [],
        }

    root_name = (
        root.tag
        .split("}")[-1]
        .lower()
    )

    if root_name == "sitemapindex":
        sitemap_urls = []

        for sitemap in root:
            sitemap_name = (
                sitemap.tag
                .split("}")[-1]
                .lower()
            )

            if sitemap_name != "sitemap":
                continue

            for child in sitemap:
                child_name = (
                    child.tag
                    .split("}")[-1]
                    .lower()
                )

                if child_name != "loc":
                    continue

                if not child.text:
                    continue

                url = child.text.strip()

                if url:
                    sitemap_urls.append(
                        url
                    )

                break

        return {
            "type":
                "sitemapindex",
            "items":
                sitemap_urls,
        }

    if root_name == "urlset":
        records = []

        for url_element in root:
            element_name = (
                url_element.tag
                .split("}")[-1]
                .lower()
            )

            if element_name != "url":
                continue

            loc = None
            lastmod = None

            for child in url_element:
                child_name = (
                    child.tag
                    .split("}")[-1]
                    .lower()
                )

                if child_name == "loc":
                    if child.text:
                        loc = (
                            child.text
                            .strip()
                        )

                elif child_name == "lastmod":
                    if child.text:
                        lastmod = (
                            child.text
                            .strip()
                        )

            if not loc:
                continue

            records.append(
                {
                    "url": loc,
                    "lastmod": (
                        parse_iso_datetime(
                            lastmod
                        )
                        if lastmod
                        else None
                    ),
                }
            )

        return {
            "type": "urlset",
            "items": records,
        }

    return {
        "type": None,
        "items": [],
    }

def _url_matches_source_rules(
    url,
    source,
):
    """
    Apply optional generic URL inclusion/exclusion rules.

    Supports:
    - substring inclusion
    - substring exclusion
    - regex exclusion
    """

    include_patterns = source.get(
        "include_url_patterns",
        [],
    )

    exclude_patterns = source.get(
        "exclude_url_patterns",
        [],
    )

    exclude_regex_patterns = source.get(
        "exclude_url_regex_patterns",
        [],
    )

    if include_patterns:
        if not any(
            pattern.lower()
            in url.lower()
            for pattern
            in include_patterns
        ):
            return False

    if any(
        pattern.lower()
        in url.lower()
        for pattern
        in exclude_patterns
    ):
        return False

    if any(
        re.search(
            pattern,
            url,
            flags=re.IGNORECASE,
        )
        for pattern
        in exclude_regex_patterns
    ):
        return False

    return True


def _sitemap_record_is_recent(
    record,
    source,
):
    """
    Apply an optional sitemap modification-age window.

    Sitemap lastmod is used only as a discovery hint.
    It is not treated as the document's publication date.

    Records without lastmod are retained because absence of
    sitemap metadata should not cause potentially useful
    evidence to disappear.
    """

    max_age_days = source.get(
        "max_age_days"
    )

    if max_age_days is None:
        return True

    lastmod = record.get(
        "lastmod"
    )

    if lastmod is None:
        return True

    if lastmod.tzinfo is None:
        lastmod = lastmod.replace(
            tzinfo=timezone.utc
        )

    cutoff = (
        datetime.now(
            timezone.utc
        )
        - timedelta(
            days=max_age_days
        )
    )

    return lastmod >= cutoff


def _normalize_sitemap_datetime(
    value,
):
    """
    Normalize sitemap timestamps to timezone-aware UTC.

    Missing timestamps sort behind timestamped records.
    """

    if value is None:
        return datetime.min.replace(
            tzinfo=timezone.utc
        )

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc
        )

    return value.astimezone(
        timezone.utc
    )


def _sort_sitemap_records(
    records,
):
    """
    Sort sitemap candidates by lastmod newest-first.

    lastmod remains only a discovery-priority signal.
    """

    return sorted(
        records,
        key=lambda record:
            _normalize_sitemap_datetime(
                record.get(
                    "lastmod"
                )
            ),
        reverse=True,
    )


def _limit_sitemap_records(
    records,
    source,
):
    """
    Apply an optional source-level sitemap candidate cap.

    max_discovery_items limits how many candidate URLs leave
    sitemap discovery after filtering and priority ordering.

    This protects Vantage from very large or heavily modified
    historical sitemaps without confusing sitemap lastmod with
    actual publication recency.
    """

    max_items = source.get(
        "max_discovery_items"
    )

    if max_items is None:
        return records

    try:
        max_items = int(
            max_items
        )

    except (
        TypeError,
        ValueError,
    ):
        return records

    if max_items <= 0:
        return []

    return records[
        :max_items
    ]


def _filter_sitemap_records(
    records,
    source,
):
    """
    Apply generic sitemap discovery rules before evidence
    normalization.
    """

    accepted = []

    for record in records:
        if not _sitemap_record_is_recent(
            record,
            source,
        ):
            continue

        url = record["url"]

        if not _url_matches_source_rules(
            url,
            source,
        ):
            continue

        accepted.append(
            record
        )

    accepted = _sort_sitemap_records(
        accepted
    )

    return _limit_sitemap_records(
        accepted,
        source,
    )


def _title_from_url(url):
    """
    Produce a lightweight fallback title from the URL path.

    Full page titles may later be available when the page
    itself is retrieved.
    """

    path = (
        url
        .rstrip("/")
        .split("/")[-1]
    )

    if not path:
        return "Untitled document"

    title = (
        path
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )

    if not title:
        return "Untitled document"

    return title


def _build_sitemap_evidence_item(
    record,
    source,
):
    """
    Convert one accepted sitemap record into the normalized
    Vantage evidence contract.

    Sitemap lastmod deliberately does not populate
    published_at.
    """

    url = record["url"]

    return {
        "title":
            _title_from_url(
                url
            ),

        "url":
            url,

        "published_at":
            None,

        "summary":
            "",

        "source":
            source["name"],

        "source_type":
            source.get(
                "type",
                "publication",
            ),

        "discovery_method":
            "sitemap",
    }


def _records_to_sitemap_evidence(
    records,
    source,
):
    """
    Apply generic sitemap filtering, priority ordering and
    candidate limits, then normalize accepted records into
    evidence items.
    """

    accepted_records = (
        _filter_sitemap_records(
            records,
            source,
        )
    )

    return [
        _build_sitemap_evidence_item(
            record,
            source,
        )
        for record
        in accepted_records
    ]


def _fetch_sitemap_urlset_records(
    sitemap_url,
):
    """
    Fetch one child URL-set sitemap and return its raw records.
    """

    xml = fetch_source_document(
        sitemap_url
    )

    if xml is None:
        return None

    parsed = _extract_sitemap_urls(
        xml
    )

    if parsed["type"] != "urlset":
        return None

    return parsed["items"]


def discover_sitemap_source(
    source,
):
    """
    Discover normalized evidence from a sitemap.

    Supports either:

    - a direct URL-set sitemap
    - a sitemap index containing child sitemaps

    Optional source configuration can limit:

    - which child sitemaps are traversed
    - which page URLs are retained
    - how old sitemap modifications may be
    - how many sitemap candidates are returned

    Candidate limits are applied globally across selected
    child sitemaps rather than independently per child.
    """

    sitemap_url = source["url"]

    xml = fetch_source_document(
        sitemap_url
    )

    if xml is None:
        return None

    parsed = _extract_sitemap_urls(
        xml
    )

    if parsed["type"] == "urlset":
        return _records_to_sitemap_evidence(
            parsed["items"],
            source,
        )

    if parsed["type"] == "sitemapindex":
        all_records = []

        child_patterns = source.get(
            "sitemap_include_patterns",
            [],
        )

        for child_url in parsed["items"]:
            if child_patterns:
                if not any(
                    pattern.lower()
                    in child_url.lower()
                    for pattern
                    in child_patterns
                ):
                    continue

            child_records = (
                _fetch_sitemap_urlset_records(
                    child_url
                )
            )

            if child_records is None:
                continue

            all_records.extend(
                child_records
            )

        return _records_to_sitemap_evidence(
            all_records,
            source,
        )

    logger.warning(
        "Unsupported or invalid sitemap for source '%s': %s",
        source.get(
            "name",
            "Unknown source",
        ),
        sitemap_url,
    )

    return None


# ---------------------------------------------------------
# Generic source dispatcher
# ---------------------------------------------------------

def discover_source(source):
    """
    Discover normalized evidence from one configured source.

    Acquisition-method-specific logic belongs behind this
    boundary.
    """

    method = (
        source.get(
            "method",
            "rss",
        )
        .strip()
        .lower()
    )

    if method == "rss":
        return discover_rss_source(
            source
        )

    if method == "sitemap":
        return discover_sitemap_source(
            source
        )

    if method == "html":
        from services.html_discovery_service import (
            discover_html_source,
        )

        return discover_html_source(
            source
        )

    logger.warning(
        "Unsupported discovery method '%s' for source '%s'.",
        method,
        source.get(
            "name",
            "Unknown source",
        ),
    )

    return None

