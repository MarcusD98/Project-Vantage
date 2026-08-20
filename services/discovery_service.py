import logging

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


# ---------------------------------------------------------
# RSS discovery
# ---------------------------------------------------------

def fetch_rss_feed(feed_url):
    """
    Fetch and parse an RSS feed.

    Returns the parsed feed when usable, otherwise None.
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
    Discover evidence items from one RSS-configured source.

    The returned dictionaries use the normalized discovery
    shape expected by the rest of the Vantage ingestion layer.
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
                "source": source["name"],
                "source_type": source.get(
                    "type",
                    "publication",
                ),
                "discovery_method": "rss",
                "url": url,
                "published_at": entry.get(
                    "published",
                    "",
                ),
                "summary": clean_summary(
                    entry.get(
                        "summary",
                        "",
                    )
                ),
            }
        )

    return items


# ---------------------------------------------------------
# Generic source dispatcher
# ---------------------------------------------------------

def discover_source(source):
    """
    Discover normalized evidence from one configured source.

    Source-specific acquisition logic belongs behind this
    boundary.

    Source Network V2 initially supports RSS only through the
    generic interface. Sitemap and HTML adapters will be added
    next without requiring the caller to change.
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