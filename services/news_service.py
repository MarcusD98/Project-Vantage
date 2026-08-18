import feedparser
from email.utils import parsedate_to_datetime

# Adding SOURCE dictionaries

SOURCES = [
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed",
    },
    {
        "name": "Sifted",
        "url": "https://sifted.eu/feed",
    },
]

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


# Defining date conversion / standardisation

def format_article_dates(articles):
    for article in articles:
        date = parsedate_to_datetime(article["published_at"])
        article["published_at"] = date.strftime("%d %b %Y · %H:%M")

    return articles

# Defining a Get Articles function

def get_vc_articles():
    all_articles = []

    for source in SOURCES:
        feed = fetch_rss_feed(source["url"])
        articles = normalize_articles(
            feed,
            source["name"]
        )

        all_articles.extend(articles)

    # Combine, sort, filter, and format the articles
    sorted_articles = sort_articles_by_date(all_articles)
    vc_articles = filter_vc_articles(sorted_articles)
    formatted_articles = format_article_dates(vc_articles)

    return formatted_articles