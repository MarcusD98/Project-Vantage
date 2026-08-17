import feedparser
from email.utils import parsedate_to_datetime

# Defining the RSS feed fetch

def fetch_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    
    print(feed.feed.title)
    print(len(feed.entries))

    return feed

# Defining the normalize article function

def normalize_articles(feed, source):
    normalized_articles = []

    for entry in feed.entries:
        article = {
            "title": entry["title"],
            "source": source,
            "url": entry["link"],
            "published_at": entry["published"]
        }

        normalized_articles.append(article)

    return normalized_articles

# Sorting articles by date

def sort_articles_by_date(articles):
    return sorted(
        articles,
        key=lambda article: parsedate_to_datetime(article["published_at"]),
        reverse=True
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
