



articles = [
    {
        "title": "Venture Studio goes bust after founder arrested for being too sexy",
        "source": "TechCrunch",
        "url": "www.techcrunch.com/article1",
        "published_at": "2026-08-17",
    }, 
    {
        "title": "Marcus raises $100 million at $550 million Series C",
        "source": "SpastikVC",
        "url": "www.spastikVC.com/article1",
        "published_at": "2026-08-15",
    },
    {
        "title": "Guy tries to learn Python, explodes",
        "source": "SillyToday",
        "url": "www.sillytoday.com/article1",
        "published_at": "2026-08-13",
    }
]

def display_articles():
    for article in articles:
        print(article["title"])
        print(article["source"])
        print(article["url"])
        print(article["published_at"])

display_articles()
