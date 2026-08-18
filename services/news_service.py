import feedparser
import logging

from config import SOURCES, CACHE_DURATION_MINUTES
from models.article import db, Article

from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta

_cached_articles = None
_cache_time = None
CACHE_DURATION = timedelta(minutes=CACHE_DURATION_MINUTES)

logger = logging.getLogger(__name__)

# Defining the RSS feed fetch

def fetch_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)

    if feed.bozo:
        logger.warning("Problem parsing RSS feed: %s", feed_url)
        return None
    
    return feed

# Defining the summary-cleaning function

def clean_summary(summary):
    soup = BeautifulSoup(summary, "html.parser")
    clean_text = soup.get_text(" ", strip=True)

    return clean_text

# Defining the normalize article function

def normalize_articles(feed, source):
    normalized_articles = []

    for entry in feed.entries:
        article = {
            "title": entry.get("title", "Untitled article"),
            "source": source,
            "url": entry.get("link", ""),
            "published_at": entry.get("published", ""),
            "summary": clean_summary(
                entry.get("summary", "")
            ),
        }

        normalized_articles.append(article)

    return normalized_articles

# Deduplication of articles

def deduplicate_articles(articles):
    seen_urls = set()
    unique_articles = []

    for article in articles:
        if article["url"] not in seen_urls:
            seen_urls.add(article["url"])
            unique_articles.append(article)

    return unique_articles

# Helper function to safely parse an article's publication date

def parse_article_date(article):
    try:
        return parsedate_to_datetime(article["published_at"])
    except (TypeError, ValueError):
        return None

# Sorting articles by date

def sort_articles_by_date(articles):
    dated_articles = []

    for article in articles:
        date = parse_article_date(article)

        if date is not None:
            article["parsed_date"] = date
            dated_articles.append(article)

    return sorted(
        dated_articles,
        key=lambda article: article["parsed_date"],
        reverse=True,
    )

# Filter for VC relevance

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
        title = article["title"].lower()

        for keyword in keywords:
            if keyword in title:
                filtered_articles.append(article)
                break

    return filtered_articles

# Defining date conversion / standardisation

def format_article_dates(articles):
    for article in articles:
        date = article["parsed_date"]
        article["published_at"] = date.strftime("%d %b %Y · %H:%M")

    return articles

# Categorization of Articles into topics

def categorize_article(article):
    title = article["title"].lower()

    # Explicit fund-related phrases
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

    if any(phrase in title for phrase in fund_phrases):
        return "Fund News"

    # A firm raising, closing, or launching a fund
    if (
        "fund" in title
        and any(action in title for action in [
            "raises",
            "raised",
            "closes",
            "closed",
            "launches",
            "launched",
        ])
        and "backed by" not in title
    ):
        return "Fund News"

    if any(keyword in title for keyword in [
        "acquires",
        "acquired",
        "acquisition",
        "merger",
        "buys",
    ]):
        return "M&A"

    if "ipo" in title:
        return "IPO"

    if any(keyword in title for keyword in [
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
    ]):
        return "Funding Round"

    return "Other"

# Categorisation of articles

def categorize_articles(articles):
    for article in articles:
        article["category"] = categorize_article(article)

    return articles

# Save articles to database via SQLite Article

def save_articles_to_database(articles):
    saved_count = 0

    for article in articles:
        existing_article = Article.query.filter_by(
            url=article["url"]
        ).first()

        if existing_article:
            continue

        db_article = Article(
            title=article["title"],
            source=article["source"],
            url=article["url"],
            published_at=article["parsed_date"],
            summary=article["summary"],
            category=article["category"],
        )

        db.session.add(db_article)
        saved_count += 1

    db.session.commit()

    return saved_count

# Defining a Get Articles function --> Crucial function called into app.py, basically it is the orchestrator, bringing together all functions to this point

def get_vc_articles():
    global _cached_articles, _cache_time

    now = datetime.now()

    if (
        _cached_articles is not None
        and _cache_time is not None
        and now - _cache_time < CACHE_DURATION
    ):
        return _cached_articles
    
    all_articles = []

    for source in SOURCES:
        feed = fetch_rss_feed(source["url"])

        if feed is None:
            continue

        articles = normalize_articles(
            feed,
            source["name"]
        )

        all_articles.extend(articles)

    # Combine, sort, filter, and format the articles (TIP: read right-to-left)
    unique_articles = deduplicate_articles(all_articles)
    sorted_articles = sort_articles_by_date(unique_articles)
    vc_articles = filter_vc_articles(sorted_articles)
    categorized_articles = categorize_articles(vc_articles)

    save_articles_to_database(categorized_articles)

    formatted_articles = format_article_dates(categorized_articles)

    _cached_articles = formatted_articles
    _cache_time = now

    return formatted_articles








