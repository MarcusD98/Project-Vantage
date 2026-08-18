from flask import Flask, render_template, request

from services.news_service import (
    fetch_rss_feed,
    normalize_articles,
    sort_articles_by_date,
    filter_vc_articles,
    format_article_dates,
)

# Create the Flask application
app = Flask(__name__)

# Define the homepage route.
# When a user visits "/", Flask runs the home() function.
@app.route("/")
def home():

    # Fetch RSS feeds from each news source
    techcrunch_fetch_feed = fetch_rss_feed(
        "https://techcrunch.com/feed"
    )

    sifted_fetch_feed = fetch_rss_feed(
        "https://sifted.eu/feed"
    )

    # Convert each source's RSS data into our standard article structure
    techcrunch_articles = normalize_articles(
        techcrunch_fetch_feed,
        "TechCrunch"
    )

    sifted_articles = normalize_articles(
        sifted_fetch_feed,
        "Sifted"
    )

    # Combine, sort, filter, and format the articles
    all_articles = techcrunch_articles + sifted_articles
    sorted_articles = sort_articles_by_date(all_articles)
    vc_articles = filter_vc_articles(sorted_articles)
    formatted_articles = format_article_dates(vc_articles)

    # Read optional search and source filters from the URL query parameters
    search_query = request.args.get("q", "").lower()
    source_filter = request.args.get("source", "")

    # If the user entered a search term, keep only matching article titles
    if search_query:
        formatted_articles = [
            article
            for article in formatted_articles
            if search_query in article["title"].lower()
        ]

    # If the user selected a source, keep only articles from that source
    if source_filter:
        formatted_articles = [
            article
            for article in formatted_articles
            if article["source"] == source_filter
        ]

    # Render index.html and pass the article/filter data into the template
    return render_template(
        "index.html",
        articles=formatted_articles,
        search_query=search_query,
        source_filter=source_filter,
    )


# Run the Flask development server when this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)