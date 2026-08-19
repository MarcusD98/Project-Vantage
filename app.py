import logging

from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate

from config import SOURCES

from models.article import db, Article
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound
from models.entity_alias import EntityAlias
from models.entity_resolution_review import EntityResolutionReview

from services.news_service import (
    get_vc_articles,
    get_source_health,
)

from services.data_quality_service import (
    get_data_quality_summary,
)

from services.entity_review_service import (
    approve_resolution_review,
    reject_resolution_review,
)

logging.basicConfig(level=logging.INFO)

# Create the Flask application
app = Flask(__name__)

# After Flask app starts, connects to SQLite and creates tables if they don't exist

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vc_news.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

# Define the homepage route.
# When a user visits "/", Flask runs the home() function.
@app.route("/")
def home():

    # Refresh article data when needed
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

@app.route("/sources")
def sources():
        source_health = get_source_health()

        for source in source_health:
             source["stored_articles"] = Article.query.filter_by(
                  source=source["name"]
             ).count()

        return render_template(
             "sources.html",
             source_health=source_health,
        )

@app.route("/funding")
def funding():
    funding_rounds = FundingRound.query.order_by(
        FundingRound.announced_at.desc()
    ).all()

    return render_template(
        "funding.html",
        funding_rounds=funding_rounds,
    )

@app.route("/company/<int:company_id>")
def company_profile(company_id):
    company = Company.query.get_or_404(company_id)

    funding_rounds = FundingRound.query.filter_by(
        company_id=company.id
    ).order_by(
        FundingRound.announced_at.desc()
    ).all()

    return render_template(
        "company.html",
        company=company,
        funding_rounds=funding_rounds,
    )

@app.route("/investor/<int:investor_id>")
def investor_profile(investor_id):
    investor = Investor.query.get_or_404(investor_id)

    funding_rounds = FundingRound.query.filter(
        FundingRound.investors.any(id=investor.id)
    ).order_by(
        FundingRound.announced_at.desc()
    ).all()

    return render_template(
        "investor.html",
        investor=investor,
        funding_rounds=funding_rounds,
    )

@app.route("/data-quality")
def data_quality():
    summary = get_data_quality_summary()

    return render_template(
        "data_quality.html",
        summary=summary,
    )

@app.route(
    "/data-quality/review/<int:review_id>/approve",
    methods=["POST"],
)
def approve_entity_review(review_id):
    approve_resolution_review(review_id)

    return redirect(
        url_for("data_quality")
    )

@app.route(
    "/data-quality/review/<int:review_id>/reject",
    methods=["POST"],
)
def reject_entity_review(review_id):
    reject_resolution_review(review_id)

    return redirect(
        url_for("data_quality")
    )

# Run the Flask development server when this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)