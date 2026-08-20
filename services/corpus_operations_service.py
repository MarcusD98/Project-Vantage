from datetime import (
    datetime,
    timezone,
)

from config import SOURCES

from models.article import (
    db,
    Article,
)

from services.article_service import (
    populate_missing_article_dates,
)

from services.backfill_service import (
    run_source_backfill,
)

from services.intelligence_pipeline import (
    _prepare_candidate_article,
    _process_funding_article,
    _process_fund_news_article,
)


def _get_live_source(
    source_name,
):
    """
    Return one configured live source by name.
    """

    for source in SOURCES:
        if (
            source.get("name")
            == source_name
        ):
            return source

    return None


def _validate_source(
    source_name,
):
    """
    Ensure a requested source exists in the main source registry.
    """

    source = _get_live_source(
        source_name
    )

    if source is None:
        raise ValueError(
            f"Unknown source: "
            f"{source_name}"
        )

    return source


def run_backfill_operation(
    source_name,
    enrichment_limit=1000,
):
    """
    Run historical evidence recovery for one configured source.

    Lifecycle:

        historical discovery
        → relevance filtering
        → categorization
        → persistence
        → page/date/content enrichment

    This operation deliberately performs no LLM extraction and
    creates no canonical funding or fund-close events.

    Database changes are committed when the operation succeeds.
    """

    _validate_source(
        source_name
    )

    try:
        backfill_stats = (
            run_source_backfill(
                source_name
            )
        )

        dates_populated = (
            populate_missing_article_dates(
                source=source_name,
                limit=enrichment_limit,
            )
        )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    remaining_undated = (
        Article.query
        .filter_by(
            source=source_name,
            published_at=None,
        )
        .count()
    )

    return {
        **backfill_stats,

        "dates_populated":
            dates_populated,

        "remaining_undated":
            remaining_undated,
    }


def _select_stored_articles(
    source_name,
    category,
    limit,
    stats,
    now,
):
    """
    Select existing unprocessed evidence for one source.

    No source discovery occurs here.

    Existing intelligence preparation rules are reused so
    publication-age policy and content enrichment remain
    consistent with the normal intelligence pipeline.

    A zero or negative limit selects no articles.
    """

    if limit <= 0:
        return []

    candidates = (
        Article.query
        .filter(
            Article.source
            == source_name,

            Article.category
            == category,

            Article.llm_processed_at
            .is_(None),
        )
        .order_by(
            Article.published_at.desc()
        )
        .all()
    )

    selected = []

    for article in candidates:
        if not _prepare_candidate_article(
            article,
            stats,
            now=now,
        ):
            continue

        selected.append(
            article
        )

        if len(selected) >= limit:
            break

    return selected


def run_stored_intelligence(
    source_name,
    funding_limit=10,
    fund_news_limit=10,
):
    """
    Process already-persisted evidence for one source.

    Unlike run_intelligence_pipeline(), this function performs
    no discovery and does not refresh live sources.

    Lifecycle:

        stored evidence
        → source filter
        → candidate preparation
        → LLM extraction
        → entity/event resolution
        → persistence
    """

    _validate_source(
        source_name
    )

    stats = {
        "source":
            source_name,

        "articles_selected":
            0,

        "stale_articles_skipped":
            0,

        "content_retrieved":
            0,

        "content_failed":
            0,

        "funding_processed":
            0,

        "funding_rounds":
            0,

        "fund_news_processed":
            0,

        "fund_closes":
            0,

        "processing_failed":
            0,
    }

    now = datetime.now(
        timezone.utc
    )

    try:
        funding_articles = (
            _select_stored_articles(
                source_name=source_name,
                category="Funding Round",
                limit=funding_limit,
                stats=stats,
                now=now,
            )
        )

        fund_news_articles = (
            _select_stored_articles(
                source_name=source_name,
                category="Fund News",
                limit=fund_news_limit,
                stats=stats,
                now=now,
            )
        )

        # Preserve metadata/content recovered while preparing
        # candidates before LLM processing begins.
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    stats[
        "articles_selected"
    ] = (
        len(funding_articles)
        + len(fund_news_articles)
    )

    for article in funding_articles:
        _process_funding_article(
            article,
            stats,
        )

    for article in fund_news_articles:
        _process_fund_news_article(
            article,
            stats,
        )

    return stats