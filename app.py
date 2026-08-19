import logging
import click

from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate

from config import SOURCES

from models.article import db, Article
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound
from models.entity_alias import EntityAlias
from models.entity_resolution_review import EntityResolutionReview
from models.fund import Fund
from models.fund_close import FundClose

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

from services.intelligence_service import (
    get_intelligence_summary,
)

from services.intelligence_pipeline import (
    run_intelligence_pipeline,
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

    funds = sorted(
        investor.funds,
        key=lambda fund: (
            fund.vintage_year or 0,
            fund.id,
        ),
        reverse=True,
    )

    return render_template(
        "investor.html",
        investor=investor,
        funding_rounds=funding_rounds,
        funds=funds,
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

@app.route("/intelligence")
def intelligence():
    summary = get_intelligence_summary()

    return render_template(
        "intelligence.html",
        summary=summary,
    )

@app.cli.group()
def vantage():
    """Project Vantage management commands."""
    pass

@vantage.command("ingest")
@click.option(
    "--funding-limit",
    default=10,
    type=int,
    show_default=True,
    help="Maximum Funding Round articles to process.",
)
@click.option(
    "--fund-news-limit",
    default=10,
    type=int,
    show_default=True,
    help="Maximum Fund News articles to process.",
)
def ingest_command(
    funding_limit,
    fund_news_limit,
):
    """Run the Vantage structured-intelligence pipeline."""

    click.echo("")
    click.echo("Vantage Intelligence Pipeline")
    click.echo("-----------------------------")

    # Run the actual end-to-end pipeline first.
    result = run_intelligence_pipeline(
        funding_limit=funding_limit,
        fund_news_limit=fund_news_limit,
    )

    # ---------------------------------------------------------
    # Source ingestion
    # ---------------------------------------------------------

    click.echo("")

    click.echo(
        f"Sources checked:         "
        f"{result['sources_checked']}"
    )

    click.echo(
        f"Source failures:         "
        f"{result['sources_failed']}"
    )

    click.echo("")

    click.echo(
        f"Articles discovered:     "
        f"{result['articles_discovered']}"
    )

    click.echo(
        f"Relevant articles:       "
        f"{result['articles_relevant']}"
    )

    click.echo(
        f"New articles saved:      "
        f"{result['articles_saved']}"
    )

    # ---------------------------------------------------------
    # Intelligence processing
    # ---------------------------------------------------------

    click.echo("")

    click.echo(
        f"Articles selected:       "
        f"{result['articles_selected']}"
    )

    click.echo(
        f"Content retrieved:       "
        f"{result['content_retrieved']}"
    )

    click.echo(
        f"Content failures:        "
        f"{result['content_failed']}"
    )

    click.echo("")

    click.echo(
        f"Funding processed:       "
        f"{result['funding_processed']}"
    )

    click.echo(
        f"Funding rounds saved:    "
        f"{result['funding_rounds']}"
    )

    click.echo("")

    click.echo(
        f"Fund news processed:     "
        f"{result['fund_news_processed']}"
    )

    click.echo(
        f"Fund closes saved:       "
        f"{result['fund_closes']}"
    )

    click.echo("")

    click.echo(
        f"Processing failures:     "
        f"{result['processing_failed']}"
    )

    click.echo("")
    click.echo("Pipeline complete.")

# Run the Flask development server when this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)