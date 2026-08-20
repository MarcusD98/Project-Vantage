import logging
from datetime import datetime

from models.article import db, Article

from services.article_service import (
    populate_article_content,
)
from services.llm_extractor import (
    extract_funding_with_llm,
    extract_fund_close_with_llm,
)
from services.entity_service import (
    save_funding_extraction,
)
from services.fund_service import (
    save_fund_close_extraction,
)

from services.news_service import (
    ingest_news_sources,
)


logger = logging.getLogger(__name__)

def run_intelligence_pipeline(
    funding_limit=10,
    fund_news_limit=10,
):
    """
    Run the end-to-end Vantage ingestion and intelligence
    lifecycle.

    1. Refresh public news sources.
    2. Persist newly discovered relevant articles.
    3. Process unprocessed company-funding articles.
    4. Process unprocessed VC fund-news articles.
    5. Return a consolidated pipeline report.
    """

    try:
        ingestion_stats = (
            ingest_news_sources()
        )

        db.session.commit()

    except Exception:
        db.session.rollback()

        logger.exception(
            "News ingestion failed."
        )

        raise

    stats = {
        "sources_checked":
            ingestion_stats[
                "sources_checked"
            ],

        "sources_failed":
            ingestion_stats[
                "sources_failed"
            ],

        "articles_discovered":
            ingestion_stats[
                "articles_discovered"
            ],

        "articles_relevant":
            ingestion_stats[
                "articles_relevant"
            ],

        "articles_saved":
            ingestion_stats[
                "articles_saved"
            ],

        "articles_selected": 0,
        "content_retrieved": 0,
        "content_failed": 0,
        "funding_processed": 0,
        "funding_rounds": 0,
        "fund_news_processed": 0,
        "fund_closes": 0,
        "processing_failed": 0,
    }

    funding_articles = (
        Article.query.filter(
            Article.category
            == "Funding Round",
            Article.llm_processed_at
            .is_(None),
        )
        .order_by(
            Article.published_at.desc()
        )
        .limit(
            funding_limit
        )
        .all()
    )

    fund_news_articles = (
        Article.query.filter(
            Article.category
            == "Fund News",
            Article.llm_processed_at
            .is_(None),
        )
        .order_by(
            Article.published_at.desc()
        )
        .limit(
            fund_news_limit
        )
        .all()
    )

    stats["articles_selected"] = (
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


def _process_funding_article(
    article,
    stats,
):
    try:
        if not _ensure_article_content(
            article,
            stats,
        ):
            return

        extraction = extract_funding_with_llm(
            article
        )

        if extraction is None:
            stats["processing_failed"] += 1
            return

        # The LLM successfully processed the article.
        article.llm_processed_at = datetime.now()
        article.llm_is_funding_round = (
            extraction.is_funding_round
        )

        funding_round = save_funding_extraction(
            article,
            extraction,
        )

        db.session.commit()

        stats["funding_processed"] += 1

        if funding_round is not None:
            stats["funding_rounds"] += 1

    except Exception:
        db.session.rollback()

        logger.exception(
            "Funding intelligence processing failed "
            "for article %s: %s",
            article.id,
            article.title,
        )

        stats["processing_failed"] += 1


def _process_fund_news_article(
    article,
    stats,
):
    try:
        if not _ensure_article_content(
            article,
            stats,
        ):
            return

        extraction = extract_fund_close_with_llm(
            article
        )

        if extraction is None:
            stats["processing_failed"] += 1
            return

        # The article has successfully passed through the
        # intelligence layer, even if it is ultimately not
        # classified as a valid fund-close event.
        article.llm_processed_at = datetime.now()

        fund_close = save_fund_close_extraction(
            article,
            extraction,
        )

        db.session.commit()

        stats["fund_news_processed"] += 1

        if fund_close is not None:
            stats["fund_closes"] += 1

    except Exception:
        db.session.rollback()

        logger.exception(
            "Fund intelligence processing failed "
            "for article %s: %s",
            article.id,
            article.title,
        )

        stats["processing_failed"] += 1


def _ensure_article_content(
    article,
    stats,
):
    """
    Ensure an article has usable full-text content before
    intelligence extraction.
    """

    if article.content:
        return True

    content = populate_article_content(
        article
    )

    if content:
        stats["content_retrieved"] += 1
        return True

    stats["content_failed"] += 1

    logger.warning(
        "Could not retrieve content for article %s: %s",
        article.id,
        article.title,
    )

    return False