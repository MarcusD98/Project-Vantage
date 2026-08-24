import logging
import click

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
)

from flask_migrate import Migrate

from config import (
    SOURCES,
    get_database_url,
)

from models.article import db, Article
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound
from models.entity_alias import EntityAlias
from models.entity_resolution_review import (
    EntityResolutionReview,
)
from models.fund import Fund
from models.fund_close import FundClose
from models.extraction_record import ExtractionRecord

from services.news_service import (
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

from services.data_cleanup_service import (
    reconcile_funding_round_pair,
    reconcile_historical_funding_rounds,
)

from services.source_measurement_service import (
    format_source_measurement_report,
    get_source_measurements,
)

from services.corpus_cli import (
    register_corpus_commands,
)

from services.investor_confidence_service import (
    get_investor_profile as get_investor_intelligence_profile,
)

from services.investor_ui_service import (
    INVESTOR_WINDOW_OPTIONS,
    normalize_investor_window,
)

from services.product_intelligence_service import (
    get_product_intelligence_summary,
)


logging.basicConfig(
    level=logging.INFO
)


# ---------------------------------------------------------
# Application setup
# ---------------------------------------------------------

app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = get_database_url()

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False

db.init_app(app)

migrate = Migrate(
    app,
    db,
)


# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

@app.route("/")
def home():
    search_query = (
        request.args.get(
            "q",
            "",
        )
        .lower()
    )

    source_filter = (
        request.args.get(
            "source",
            "",
        )
    )

    category_filter = (
        request.args.get(
            "category",
            "",
        )
    )

    query = Article.query

    if search_query:
        query = query.filter(
            Article.title.ilike(
                f"%{search_query}%"
            )
        )

    if source_filter:
        query = query.filter_by(
            source=source_filter
        )

    if category_filter:
        query = query.filter_by(
            category=category_filter
        )

    articles = (
        query
        .order_by(
            Article.published_at.desc()
        )
        .all()
    )

    return render_template(
        "index.html",
        articles=articles,
        search_query=search_query,
        source_filter=source_filter,
        sources=SOURCES,
        category_filter=category_filter,
    )


# ---------------------------------------------------------
# Sources
# ---------------------------------------------------------

@app.route("/sources")
def sources():
    source_health = (
        get_source_health()
    )

    for source in source_health:
        source[
            "stored_articles"
        ] = (
            Article.query
            .filter_by(
                source=source["name"]
            )
            .count()
        )

    return render_template(
        "sources.html",
        source_health=source_health,
    )


# ---------------------------------------------------------
# Funding
# ---------------------------------------------------------

@app.route("/funding")
def funding():
    funding_rounds = (
        FundingRound.query
        .order_by(
            FundingRound
            .announced_at
            .desc()
        )
        .all()
    )

    return render_template(
        "funding.html",
        funding_rounds=funding_rounds,
    )


# ---------------------------------------------------------
# Company
# ---------------------------------------------------------

@app.route(
    "/company/<int:company_id>"
)
def company_profile(company_id):
    company = (
        Company.query
        .get_or_404(
            company_id
        )
    )

    funding_rounds = (
        FundingRound.query
        .filter_by(
            company_id=company.id
        )
        .order_by(
            FundingRound
            .announced_at
            .desc()
        )
        .all()
    )

    return render_template(
        "company.html",
        company=company,
        funding_rounds=funding_rounds,
    )


# ---------------------------------------------------------
# Investor
# ---------------------------------------------------------

@app.route(
    "/investor/<int:investor_id>"
)
def investor_profile(investor_id):
    investor = (
        Investor.query
        .get_or_404(
            investor_id
        )
    )

    window_days = (
        normalize_investor_window(
            request.args.get(
                "window"
            )
        )
    )

    intelligence_profile = (
        get_investor_intelligence_profile(
            identifier=investor.name,
            window_days=window_days,
            recent_limit=8,
        )
    )

    funding_rounds = (
        FundingRound.query
        .filter(
            FundingRound.investors.any(
                id=investor.id
            )
        )
        .order_by(
            FundingRound
            .announced_at
            .desc()
        )
        .all()
    )

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
        intelligence_profile=(
            intelligence_profile
        ),
        window_days=window_days,
        window_options=(
            INVESTOR_WINDOW_OPTIONS
        ),
    )


# ---------------------------------------------------------
# Data quality
# ---------------------------------------------------------

@app.route("/data-quality")
def data_quality():
    summary = (
        get_data_quality_summary()
    )

    return render_template(
        "data_quality.html",
        summary=summary,
    )


@app.route(
    "/data-quality/review/"
    "<int:review_id>/approve",
    methods=["POST"],
)
def approve_entity_review(
    review_id,
):
    approve_resolution_review(
        review_id
    )

    return redirect(
        url_for(
            "data_quality"
        )
    )


@app.route(
    "/data-quality/review/"
    "<int:review_id>/reject",
    methods=["POST"],
)
def reject_entity_review(
    review_id,
):
    reject_resolution_review(
        review_id
    )

    return redirect(
        url_for(
            "data_quality"
        )
    )


# ---------------------------------------------------------
# Intelligence
# ---------------------------------------------------------

@app.route("/intelligence")
def intelligence():
    summary = (
        get_intelligence_summary()
    )

    product_intelligence = (
        get_product_intelligence_summary()
    )

    return render_template(
        "intelligence.html",
        summary=summary,
        product=product_intelligence,
    )


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

@app.cli.group()
def vantage():
    """
    Project Vantage management commands.
    """
    pass


register_corpus_commands(
    vantage
)


# ---------------------------------------------------------
# CLI: intelligence ingestion
# ---------------------------------------------------------

@vantage.command("ingest")
@click.option(
    "--funding-limit",
    default=10,
    type=int,
    show_default=True,
    help=(
        "Maximum Funding Round "
        "articles to process."
    ),
)
@click.option(
    "--fund-news-limit",
    default=10,
    type=int,
    show_default=True,
    help=(
        "Maximum Fund News "
        "articles to process."
    ),
)
def ingest_command(
    funding_limit,
    fund_news_limit,
):
    """
    Run the Vantage structured-intelligence pipeline.
    """

    click.echo("")
    click.echo(
        "Vantage Intelligence Pipeline"
    )
    click.echo(
        "-----------------------------"
    )

    result = (
        run_intelligence_pipeline(
            funding_limit=funding_limit,
            fund_news_limit=(
                fund_news_limit
            ),
        )
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
        f"Stale articles skipped:  "
        f"{result['stale_articles_skipped']}"
    )

    click.echo(
        f"Compound articles skipped:"
        f" {result['compound_articles_skipped']}"
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
    click.echo(
        "Pipeline complete."
    )


# ---------------------------------------------------------
# CLI: source measurement
# ---------------------------------------------------------

@vantage.command("sources")
def source_measurement_command():
    """
    Report persisted source contribution and operating state.
    """

    measurements = (
        get_source_measurements()
    )

    click.echo("")
    click.echo(
        "Vantage Source Measurement"
    )
    click.echo(
        "--------------------------"
    )
    click.echo("")

    click.echo(
        format_source_measurement_report(
            measurements
        )
    )

    click.echo("")

    click.echo(
        "Proc % = processed eligible funding evidence "
        "/ eligible funding candidates"
    )

    click.echo(
        "Confirm % = confirmed funding evidence "
        "/ processed eligible funding evidence"
    )

    click.echo(
        "Event % = canonical funding events "
        "/ confirmed funding evidence"
    )

    click.echo(
        "Overlap % = multi-source funding events "
        "/ supported funding events"
    )

    click.echo("")


# ---------------------------------------------------------
# CLI: funding reconciliation
# ---------------------------------------------------------

@vantage.command("reconcile")
@click.option(
    "--apply",
    "apply_changes",
    is_flag=True,
    help=(
        "Apply high-confidence historical funding-event "
        "merges. Without this flag the command is read-only."
    ),
)
def reconcile_command(
    apply_changes,
):
    """
    Audit or reconcile historical funding-event duplicates.
    """

    click.echo("")
    click.echo(
        "Vantage Funding Event Reconciliation"
    )
    click.echo(
        "------------------------------------"
    )

    mode = (
        "APPLY"
        if apply_changes
        else "DRY RUN"
    )

    click.echo("")

    click.echo(
        f"Mode:                    "
        f"{mode}"
    )

    try:
        result = (
            reconcile_historical_funding_rounds(
                apply=apply_changes
            )
        )

        if apply_changes:
            db.session.commit()

    except Exception:
        db.session.rollback()

        logging.exception(
            "Historical funding reconciliation failed."
        )

        raise

    click.echo("")

    click.echo(
        f"Initial candidates:      "
        f"{result['initial_candidates']}"
    )

    if not apply_changes:
        click.echo("")
        click.echo(
            "Candidate funding events:"
        )

        if not result["candidates"]:
            click.echo(
                "  None."
            )

        for candidate in result[
            "candidates"
        ]:
            click.echo("")

            click.echo(
                f"  "
                f"{candidate['company_name']}"
            )

            click.echo(
                "    Round "
                f"{candidate['round_a_id']}: "
                f"{candidate['round_a_amount']} "
                f"{candidate['round_a_currency']} | "
                f"{candidate['round_a_type']} | "
                f"{candidate['round_a_announced_at']}"
            )

            click.echo(
                "    Round "
                f"{candidate['round_b_id']}: "
                f"{candidate['round_b_amount']} "
                f"{candidate['round_b_currency']} | "
                f"{candidate['round_b_type']} | "
                f"{candidate['round_b_announced_at']}"
            )

        click.echo("")

        click.echo(
            "No database changes were made."
        )

        click.echo(
            "Re-run with --apply to execute "
            "these high-confidence merges."
        )

        return

    click.echo(
        f"Funding rounds merged:  "
        f"{result['merged']}"
    )

    click.echo(
        f"Candidates remaining:   "
        f"{result['remaining_candidates']}"
    )

    if result["merges"]:
        click.echo("")
        click.echo(
            "Applied merges:"
        )

        for merge in result[
            "merges"
        ]:
            click.echo(
                "  "
                f"{merge['company_name']}: "
                f"removed round "
                f"{merge['removed_round_id']} "
                f"→ canonical round "
                f"{merge['surviving_round_id']}"
            )

    click.echo("")
    click.echo(
        "Reconciliation complete."
    )


# ---------------------------------------------------------
# Development server
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True
    )