import requests


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

raises = [
    {
        "company": "HumanEvolution",
        "founding_year": 2022,
        "series": "Series C",
        "amount_raised_usd": 20_000_000,
        "round_valuation_usd": 150_000_000,
    },
    {
        "company": "CubeChain",
        "founding_year": 2017,
        "series": "Series E",
        "amount_raised_usd": 250_000_000,
        "round_valuation_usd": 1_200_000_000,
    },
    {
        "company": "Straightening Forks",
        "founding_year": 2019,
        "series": "Series D",
        "amount_raised_usd": 120_000_000,
        "round_valuation_usd": 900_000_000,        
    }
]

def display_articles(articles):
    for article in articles:
        print("-" * 50)
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"URL: {article['url']}")
        print(f"Published at: {article['published_at']}")

def display_raises(raises):
    for funding_round in raises:
        print("-" * 50)
        print(f"Company: {funding_round['company']}")
        print(f"Founded: {funding_round['founding_year']}") 
        print(f"Series: {funding_round['series']}")
        amount = funding_round["amount_raised_usd"]
        print(f"Amount Raised (USD): ${amount:,}")
        valuation = funding_round["round_valuation_usd"]
        print(f"Valuation (USD): ${valuation:,}")

def display_large_raises(raises, minimum_amount):
    for funding_round in raises:
        if funding_round["amount_raised_usd"] > minimum_amount:
            print("-" * 50)
            print(funding_round["company"])

display_articles(articles)
display_raises(raises)
display_large_raises(raises, 200_000_000)

response = requests.get("https://jsonplaceholder.typicode.com/posts/1")

print(response.status_code)
print(response.json())


