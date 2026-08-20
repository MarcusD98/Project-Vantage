import logging

from datetime import datetime, timezone

from config import SOURCES

from models.article import db, Article

from services.discovery_service import (
    clean_summary,
    discover_source,
    fetch_rss_feed,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Source health
# ---------------------------------------------------------

def get_source_health():
    """
    Perform live diagnostic checks of configured sources.

    Source health remains RSS-oriented until additional
    discovery adapters are implemented.
    """

    source_health = []

    for source in SOURCES:
        if not source.get(
            "enabled",
            True,
        ):
            source_health.append(
                {
                    "name": source["name"],
                    "region": source["region"],
                    "status": "disabled",
                    "entries": 0,
                }
            )

            continue

        method = (
            source.get(
                "method",
                "rss",
            )
            .strip()
            .lower()
        )

        if method != "rss":
            source_health.append(
                {
                    "name": source["name"],
                    "region": source["region"],
                    "status": "unsupported",
                    "entries": 0,
                }
            )

            continue

        feed = fetch_rss_feed(
            source["url"]
        )

        if feed is None:
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
                "entries": len(
                    feed.entries
                ),
            }
        )

    return source_health


# ---------------------------------------------------------
# Deduplication
# ---------------------------------------------------------

def deduplicate_articles(articles):
    seen_urls = set()
    unique_articles = []

    for article in articles:
        url = article["url"]

        if url in seen_urls:
            continue

        seen_urls.add(
            url
        )

        unique_articles.append(
            article
        )

    return unique_articles


# ---------------------------------------------------------
# Date handling
# ---------------------------------------------------------

def _sortable_datetime(value):
    """
    Return a timezone-aware datetime suitable for sorting.

    Naive datetimes are treated as UTC.

    Missing dates sort behind dated evidence.
    """

    if value is None:
        return datetime.min.replace(
            tzinfo=timezone.utc
        )

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc
        )

    return value


def sort_articles_by_date(articles):
    """
    Sort evidence newest-first without dropping undated items.
    """

    return sorted(
        articles,
        key=lambda article: (
            _sortable_datetime(
                article.get(
                    "published_at"
                )
            )
        ),
        reverse=True,
    )


# ---------------------------------------------------------
# Relevance filtering
# ---------------------------------------------------------

def filter_vc_articles(articles):
    """
    Apply source-aware relevance filtering.

    Editorial publications require headline filtering because
    their content universe is broad.

    Investor first-party sources are already highly curated
    venture evidence, so they are retained with much higher
    recall and classified downstream.
    """

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
        source_type = (
            article.get(
                "source_type",
                "publication",
            )
            .strip()
            .lower()
        )

        if source_type == "investor":
            filtered_articles.append(
                article
            )

            continue

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
    """
    Route normalized evidence into a broad intelligence
    category.

    Categorization is intentionally a high-recall routing
    heuristic rather than a final statement of event truth.

    First-party investor sources can use investment-specific
    editorial language that general publications do not.
    """

    title = article[
        "title"
    ].lower()

    source_type = (
        article.get(
            "source_type",
            "publication",
        )
        .strip()
        .lower()
    )

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

    # First-party investors frequently announce new
    # investments using language such as:
    #
    #   "Partnering with Acme"
    #
    # This is a routing signal, not final event truth.
    # The funding extractor still decides whether the page
    # actually represents a financing event.
    if (
        source_type == "investor"
        and title.startswith(
            "partnering with "
        )
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


def recategorize_stored_articles(
    source=None,
):
    """
    Reapply the current categorization rules to evidence that
    is already stored.

    Useful when categorization logic improves after a source
    has already been ingested.

    Existing evidence is updated in place. Transaction
    ownership remains with the caller.

    Returns the number of Article rows whose category changed.
    """

    query = Article.query

    if source is not None:
        query = query.filter_by(
            source=source
        )

    changed = 0

    for article in query.all():
        category = categorize_article(
            {
                "title": article.title,
                "source_type": (
                    article.source_type
                    or "publication"
                ),
            }
        )

        if category == article.category:
            continue

        article.category = category
        changed += 1

    db.session.flush()

    return changed


# ---------------------------------------------------------
# Canonical source-processing pipeline
# ---------------------------------------------------------

def process_news_sources():
    """
    Discover and process all enabled Vantage sources.

    Acquisition-specific discovery happens behind
    discover_source().

    All discovered evidence should already conform to the
    normalized evidence contract.
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

        source_articles = (
            discover_source(
                source
            )
        )

        if source_articles is None:
            sources_failed += 1
            continue

        all_articles.extend(
            source_articles
        )

    articles_discovered = len(
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

    relevant_articles = (
        filter_vc_articles(
            sorted_articles
        )
    )

    categorized_articles = (
        categorize_articles(
            relevant_articles
        )
    )

    return {
        "sources_checked":
            sources_checked,

        "sources_failed":
            sources_failed,

        "articles_discovered":
            articles_discovered,

        "articles":
            categorized_articles,
    }


# ---------------------------------------------------------
# Persistence
# ---------------------------------------------------------

def save_articles_to_database(
    articles,
):
    """
    Persist previously unseen normalized evidence.

    Transaction ownership belongs to the caller.
    """

    saved_count = 0

    for article in articles:
        existing_article = (
            Article.query.filter_by(
                url=article["url"]
            ).first()
        )

        if existing_article is not None:
            continue

        db_article = Article(
            title=article["title"],
            source=article["source"],
            source_type=article.get(
                "source_type"
            ),
            discovery_method=article.get(
                "discovery_method"
            ),
            url=article["url"],
            published_at=article.get(
                "published_at"
            ),
            summary=article.get(
                "summary"
            ),
            category=article["category"],
        )

        db.session.add(
            db_article
        )

        saved_count += 1

    db.session.flush()

    return saved_count


# ---------------------------------------------------------
# Application ingestion entry point
# ---------------------------------------------------------

def ingest_news_sources():
    """
    Run the canonical Vantage discovery-processing flow and
    persist new relevant evidence.

    Transaction ownership belongs to the caller.
    """

    result = process_news_sources()

    articles = result[
        "articles"
    ]

    saved_count = (
        save_articles_to_database(
            articles
        )
    )

    return {
        "sources_checked":
            result[
                "sources_checked"
            ],

        "sources_failed":
            result[
                "sources_failed"
            ],

        "articles_discovered":
            result[
                "articles_discovered"
            ],

        "articles_relevant":
            len(articles),

        "articles_saved":
            saved_count,
    }