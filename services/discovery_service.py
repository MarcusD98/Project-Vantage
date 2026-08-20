import logging

from email.utils import parsedate_to_datetime

import feedparser

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


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

    Invalid or missing dates return None rather than causing
    the evidence item to be discarded.
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

    Dates are normalized here so downstream services do not
    need to understand RSS-specific date formats.
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
                "published_at": parse_rss_date(
                    entry.get(
                        "published",
                        "",
                    )
                ),
                "summary": clean_summary(
                    entry.get(
                        "summary",
                        "",
                    )
                ),
                "source": source["name"],
                "source_type": source.get(
                    "type",
                    "publication",
                ),
                "discovery_method": "rss",
            }
        )

    return items


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

    logger.warning(
        "Unsupported discovery method '%s' for source '%s'.",
        method,
        source.get(
            "name",
            "Unknown source",
        ),
    )

    return None