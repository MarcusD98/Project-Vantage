from flask import Flask, render_template, request

from services.news_service import (
    get_vc_articles,
)

# Create the Flask application
app = Flask(__name__)

# Define the homepage route.
# When a user visits "/", Flask runs the home() function.
@app.route("/")
def home():

    # Get the processed VC articles from the news service

    articles = get_vc_articles()

    # Read optional search and source filters from the URL query parameters
    search_query = request.args.get("q", "").lower()
    source_filter = request.args.get("source", "")

    # If the user entered a search term, keep only matching article titles
    if search_query:
        articles = [
            article
            for article in articles
            if search_query in article["title"].lower()
        ]

    # If the user selected a source, keep only articles from that source
    if source_filter:
        articles = [
            article
            for article in articles
            if article["source"] == source_filter
        ]

    # Render index.html and pass the article/filter data into the template
    return render_template(
        "index.html",
        articles=articles,
        search_query=search_query,
        source_filter=source_filter,
    )

# Run the Flask development server when this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)