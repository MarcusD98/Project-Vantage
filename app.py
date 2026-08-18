import logging

from flask import Flask, render_template, request

from config import SOURCES
from models.article import db, Article
from services.news_service import (
    get_vc_articles,
)

logging.basicConfig(level=logging.INFO)

# Create the Flask application
app = Flask(__name__)

# After Flask app starts, connects to SQLite and creates tables if they don't exist

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vc_news.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Define the homepage route.
# When a user visits "/", Flask runs the home() function.
@app.route("/")
def home():

    # Refresh the database from RSS feeds
    get_vc_articles()

    # Read optional search, source and category filters from the URL query parameters
    search_query = request.args.get("q", "").lower()
    source_filter = request.args.get("source", "")
    category_filter = request.args.get("category", "")

    # Start a database query
    query = Article.query

    if search_query:
        query = query.filter(
            Article.title.ilike(f"%{search_query}%")
        )
    if source_filter:
        query = query.filter_by(
            source=source_filter
        )

    if category_filter:
        query = query.filter_by(
            category=category_filter
        )

    articles = query.order_by(
        Article.published_at.desc()
    ).all()

    # Render index.html and pass the article/filter data into the template
    return render_template(
        "index.html",
        articles=articles,
        search_query=search_query,
        source_filter=source_filter,
        sources=SOURCES,
        category_filter=category_filter,
    )

# Run the Flask development server when this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)