import feedparser
import logging

from config import SOURCES, CACHE_DURATION_MINUTES
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
    formatted_articles = format_article_dates(vc_articles)

    _cached_articles = formatted_articles
    _cache_time = now

    return formatted_articles