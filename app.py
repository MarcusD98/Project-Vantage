
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
        "IPO",        
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

# Displaying articles

def display_articles(articles):
    for article in articles:
        print("-" * 50)
        print(f"Title: {article['title']} ")
        print(f"Source: {article['source']} ")
        print(f"URL: {article['url']} ")
        print(f"Published at: {article['published_at']} ")

# Fetching the RSS feeds

techcrunch_fetch_feed = fetch_rss_feed("https://techcrunch.com/feed")
sifted_fetch_feed = fetch_rss_feed("https://sifted.eu/feed")

# Calling in normalization of articles function for each site

techcrunch_articles = normalize_articles(
    techcrunch_fetch_feed,
    "TechCrunch"
)
sifted_articles = normalize_articles(
    sifted_fetch_feed,
    "Sifted"
)

# Calling displaying of articles

all_articles = techcrunch_articles + sifted_articles
sorted_articles = sort_articles_by_date(all_articles)
vc_articles = filter_vc_articles(sorted_articles)

display_articles(vc_articles)


