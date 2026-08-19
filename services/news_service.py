import feedparser
import logging

from config import SOURCES, CACHE_DURATION_MINUTES
from models.article import db, Article

from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta


_cached_articles = None
_cache_time = None

CACHE_DURATION = timedelta(
    minutes=CACHE_DURATION_MINUTES
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# RSS fetching
# ---------------------------------------------------------

def fetch_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)

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


# ---------------------------------------------------------
# Source health
# ---------------------------------------------------------

def get_source_health():
    source_health = []

    for source in SOURCES:
        if not source.get("enabled", True):
            source_health.append(
                {
                    "name": source["name"],
                    "region": source["region"],
                    "status": "disabled",
                    "entries": 0,
                }
            )
            continue

        feed = feedparser.parse(
            source["url"]
        )

        if not feed.entries:
            source_health.append(
                {
                    "name": source["name"],
                    "region": source["region"],
                    "status": "failed",
                    "entries": 0,
                }
            )
            continue

        status = (
            "warning"
            if feed.bozo
            else "healthy"
        )

        source_health.append(
            {
                "name": source["name"],
                "region": source["region"],
                "status": status,
                "entries": len(feed.entries),
            }
        )

    return source_health


# ---------------------------------------------------------
# Article normalization helpers
# ---------------------------------------------------------

def clean_summary(summary):
    soup = BeautifulSoup(
        summary,
        "html.parser",
    )

    return soup.get_text(
        " ",
        strip=True,
    )


def normalize_articles(
    feed,
    source,
):
    normalized_articles = []

    for entry in feed.entries:
        url = entry.get(
            "link",
            "",
        )

        if not url:
            continue

        article = {
            "title": entry.get(
                "title",
                "Untitled article",
            ),
            "source": source,
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

        normalized_articles.append(
            article
        )

    return normalized_articles


def deduplicate_articles(articles):
    seen_urls = set()
    unique_articles = []

    for article in articles:
        if article["url"] in seen_urls:
            continue

        seen_urls.add(
            article["url"]
        )

        unique_articles.append(
            article
        )

    return unique_articles


def parse_article_date(article):
    try:
        return parsedate_to_datetime(
            article["published_at"]
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def sort_articles_by_date(articles):
    dated_articles = []

    for article in articles:
        date = parse_article_date(
            article
        )

        if date is None:
            continue

        article["parsed_date"] = date

        dated_articles.append(
            article
        )

    return sorted(
        dated_articles,
        key=lambda article: (
            article["parsed_date"]
        ),
        reverse=True,
    )


# ---------------------------------------------------------
# Relevance filtering
# ---------------------------------------------------------

def filter_vc_articles(articles):
    keywords = [
        "raises",
        "raised",
        "funding",
        "fundraise",
        "valuation",
        "venture",
        "vc",
        "investor",
        "investment",
        "series a",
        "series b",
        "series c",
        "series d",
        "series e",
        "ipo",
        "seed",
    ]

    filtered_articles = []

    for article in articles:
        title = article[
            "title"
        ].lower()

        if any(
            keyword in title
            for keyword in keywords
        ):
            filtered_articles.append(
                article
            )

    return filtered_articles


# ---------------------------------------------------------
# Categorization
# ---------------------------------------------------------

def categorize_article(article):
    title = article[
        "title"
    ].lower()

    fund_phrases = [
        "fund i",
        "fund ii",
        "fund iii",
        "fund iv",
        "fund v",
        "new fund",
        "second fund",
        "third fund",
        "venture fund",
        "vc fund",
    ]

    if any(
        phrase in title
        for phrase in fund_phrases
    ):
        return "Fund News"

    if (
        "fund" in title
        and any(
            action in title
            for action in [
                "raises",
                "raised",
                "closes",
                "closed",
                "launches",
                "launched",
            ]
        )
        and "backed by" not in title
    ):
        return "Fund News"

    if any(
        keyword in title
        for keyword in [
            "acquires",
            "acquired",
            "acquisition",
            "merger",
            "buys",
        ]
    ):
        return "M&A"

    if "ipo" in title:
        return "IPO"

    if any(
        keyword in title
        for keyword in [
            "series a",
            "series b",
            "series c",
            "series d",
            "series e",
            "seed",
            "raises",
            "raised",
            "funding",
            "fundraise",
            "valuation",
            "investment",
        ]
    ):
        return "Funding Round"

    return "Other"


def categorize_articles(articles):
    for article in articles:
        article["category"] = (
            categorize_article(
                article
            )
        )

    return articles


# ---------------------------------------------------------
# Persistence
# ---------------------------------------------------------

def save_articles_to_database(
    articles,
):
    saved_count = 0

    for article in articles:
        existing_article = (
            Article.query.filter_by(
                url=article["url"]
            ).first()
        )

        if existing_article:
            continue

        db_article = Article(
            title=article["title"],
            source=article["source"],
            url=article["url"],
            published_at=article[
                "parsed_date"
            ],
            summary=article["summary"],
            category=article["category"],
        )

        db.session.add(
            db_article
        )

        saved_count += 1

    db.session.commit()

    return saved_count


# ---------------------------------------------------------
# Core ingestion
# ---------------------------------------------------------

def ingest_news_sources():
    """
    Fetch enabled RSS sources, normalize and filter articles,
    classify them, and persist only new records.

    This function is intentionally independent of the
    homepage cache so it can be safely called by the
    Vantage ingestion pipeline.
    """

    all_articles = []

    sources_checked = 0
    sources_failed = 0

    for source in SOURCES:
        if not source.get(
            "enabled",
            True,
        ):
            continue

        sources_checked += 1

        feed = fetch_rss_feed(
            source["url"]
        )

        if feed is None:
            sources_failed += 1
            continue

        articles = normalize_articles(
            feed,
            source["name"],
        )

        all_articles.extend(
            articles
        )

    discovered_count = len(
        all_articles
    )

    unique_articles = (
        deduplicate_articles(
            all_articles
        )
    )

    sorted_articles = (
        sort_articles_by_date(
            unique_articles
        )
    )

    vc_articles = (
        filter_vc_articles(
            sorted_articles
        )
    )

    categorized_articles = (
        categorize_articles(
            vc_articles
        )
    )

    saved_count = (
        save_articles_to_database(
            categorized_articles
        )
    )

    return {
        "sources_checked":
            sources_checked,

        "sources_failed":
            sources_failed,

        "articles_discovered":
            discovered_count,

        "articles_relevant":
            len(categorized_articles),

        "articles_saved":
            saved_count,
    }


# ---------------------------------------------------------
# Web-app article feed
# ---------------------------------------------------------

def get_vc_articles():
    global _cached_articles
    global _cache_time

    now = datetime.now()

    if (
        _cached_articles is not None
        and _cache_time is not None
        and now - _cache_time
        < CACHE_DURATION
    ):
        return _cached_articles

    all_articles = []

    for source in SOURCES:
        if not source.get(
            "enabled",
            True,
        ):
            continue

        feed = fetch_rss_feed(
            source["url"]
        )

        if feed is None:
            continue

        articles = normalize_articles(
            feed,
            source["name"],
        )

        all_articles.extend(
            articles
        )

    unique_articles = (
        deduplicate_articles(
            all_articles
        )
    )

    sorted_articles = (
        sort_articles_by_date(
            unique_articles
        )
    )

    vc_articles = (
        filter_vc_articles(
            sorted_articles
        )
    )

    categorized_articles = (
        categorize_articles(
            vc_articles
        )
    )

    save_articles_to_database(
        categorized_articles
    )

    _cached_articles = (
        categorized_articles
    )

    _cache_time = now

    return categorized_articles