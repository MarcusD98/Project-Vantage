from services.news_service import (
    fetch_rss_feed,
    normalize_articles,
    sort_articles_by_date,
    filter_vc_articles,
)

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


