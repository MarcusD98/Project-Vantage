import logging

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from config import SOURCES

from models.article import (
    db,
    Article,
)

from services.article_service import (
    populate_article_content,
)

from services.compound_evidence_service import (
    is_compound_funding_evidence,
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


# ---------------------------------------------------------
# Source policy
# ---------------------------------------------------------

def _get_source_config(article):
    """
    Return the configured source definition for an Article.

    Articles whose source is no longer configured simply have
    no source-specific intelligence policy.
    """

    for source in SOURCES:
        if (
            source.get("name")
            == article.source
        ):
            return source

    return None


def _normalize_datetime(value):
    """
    Normalize a datetime to timezone-aware UTC for safe
    comparison.

    SQLite commonly returns timezone-naive values even when
    upstream evidence originally carried timezone information.
    """

    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc
        )

    return value.astimezone(
        timezone.utc
    )


def _article_is_within_publication_window(
    article,
    now=None,
):
    """
    Determine whether evidence is eligible for current
    intelligence processing.

    Sources may optionally define:

        max_published_age_days

    This check uses Article.published_at, which should represent
    the evidence document's actual publication date.

    Evidence with no source-specific rule remains eligible.

    Evidence whose publication date still cannot be determined
    also remains eligible rather than being silently discarded.
    """

    source = _get_source_config(
        article
    )

    if source is None:
        return True

    max_age_days = source.get(
        "max_published_age_days"
    )

    if max_age_days is None:
        return True

    published_at = (
        _normalize_datetime(
            article.published_at
        )
    )

    if published_at is None:
        return True

    if now is None:
        now = datetime.now(
            timezone.utc
        )
    else:
        now = _normalize_datetime(
            now
        )

    cutoff = (
        now
        - timedelta(
            days=max_age_days
        )
    )

    return (
        published_at
        >= cutoff
    )


def _source_requires_publication_date(
    article,
):
    """
    Return True when the article belongs to a source that uses
    a real-publication recency policy.
    """

    source = _get_source_config(
        article
    )

    if source is None:
        return False

    return (
        source.get(
            "max_published_age_days"
        )
        is not None
    )


# ---------------------------------------------------------
# Candidate preparation
# ---------------------------------------------------------

def _prepare_candidate_article(
    article,
    stats,
    now=None,
):
    """
    Prepare one evidence document before intelligence
    selection.

    Funding evidence that is clearly compound is preserved but
    excluded from Vantage's single-event funding extractor.

    For remaining sources with publication-age policies:

    1. Recover missing page metadata when necessary.
    2. Preserve any recovered publication date.
    3. Exclude genuinely stale evidence from current
       intelligence processing.

    Historical and compound evidence remains stored in Article
    and is not marked as LLM-processed.
    """

    if is_compound_funding_evidence(
        article
    ):
        stats.setdefault(
            "compound_articles_skipped",
            0,
        )

        stats[
            "compound_articles_skipped"
        ] += 1

        logger.info(
            "Skipping compound funding evidence "
            "article %s: %s",
            article.id,
            article.title,
        )

        return False

    requires_date = (
        _source_requires_publication_date(
            article
        )
    )

    should_fetch = (
        not article.content
        or (
            requires_date
            and article.published_at
            is None
        )
    )

    if should_fetch:
        had_content = bool(
            article.content
        )

        content = (
            populate_article_content(
                article
            )
        )

        if (
            not had_content
            and content
        ):
            stats[
                "content_retrieved"
            ] += 1

    if not _article_is_within_publication_window(
        article,
        now=now,
    ):
        stats[
            "stale_articles_skipped"
        ] += 1

        return False

    return True


def _select_articles_for_intelligence(
    category,
    limit,
    stats,
    now=None,
):
    """
    Select current, unprocessed evidence for one intelligence
    category.

    Candidate preparation occurs before the final batch limit,
    so stale or compound evidence does not consume processing
    capacity.
    """

    if limit <= 0:
        return []

    candidates = (
        Article.query
        .filter(
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


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------

def run_intelligence_pipeline(
    funding_limit=10,
    fund_news_limit=10,
):
    """
    Run the end-to-end Vantage ingestion and intelligence
    lifecycle.

    1. Refresh public evidence sources.
    2. Persist newly discovered relevant evidence.
    3. Exclude obvious compound funding evidence from the
       single-event extractor.
    4. Enrich page metadata where required.
    5. Apply source-specific publication recency policy.
    6. Process current company-funding evidence.
    7. Process current VC fund-news evidence.
    8. Return a consolidated pipeline report.
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

        "articles_selected":
            0,

        "stale_articles_skipped":
            0,

        "compound_articles_skipped":
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
            _select_articles_for_intelligence(
                category="Funding Round",
                limit=funding_limit,
                stats=stats,
                now=now,
            )
        )

        fund_news_articles = (
            _select_articles_for_intelligence(
                category="Fund News",
                limit=fund_news_limit,
                stats=stats,
                now=now,
            )
        )

        db.session.commit()

    except Exception:
        db.session.rollback()

        logger.exception(
            "Intelligence candidate preparation failed."
        )

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


# ---------------------------------------------------------
# Funding processing
# ---------------------------------------------------------

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

        extraction = (
            extract_funding_with_llm(
                article
            )
        )

        if extraction is None:
            stats[
                "processing_failed"
            ] += 1

            return

        article.llm_processed_at = (
            datetime.now()
        )

        article.llm_is_funding_round = (
            extraction.is_funding_round
        )

        funding_round = (
            save_funding_extraction(
                article,
                extraction,
            )
        )

        db.session.commit()

        stats[
            "funding_processed"
        ] += 1

        if funding_round is not None:
            stats[
                "funding_rounds"
            ] += 1

    except Exception:
        db.session.rollback()

        logger.exception(
            "Funding intelligence processing failed "
            "for article %s: %s",
            article.id,
            article.title,
        )

        stats[
            "processing_failed"
        ] += 1


# ---------------------------------------------------------
# Fund-news processing
# ---------------------------------------------------------

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

        extraction = (
            extract_fund_close_with_llm(
                article
            )
        )

        if extraction is None:
            stats[
                "processing_failed"
            ] += 1

            return

        article.llm_processed_at = (
            datetime.now()
        )

        fund_close = (
            save_fund_close_extraction(
                article,
                extraction,
            )
        )

        db.session.commit()

        stats[
            "fund_news_processed"
        ] += 1

        if fund_close is not None:
            stats[
                "fund_closes"
            ] += 1

    except Exception:
        db.session.rollback()

        logger.exception(
            "Fund intelligence processing failed "
            "for article %s: %s",
            article.id,
            article.title,
        )

        stats[
            "processing_failed"
        ] += 1


# ---------------------------------------------------------
# Content readiness
# ---------------------------------------------------------

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
        stats[
            "content_retrieved"
        ] += 1

        return True

    stats[
        "content_failed"
    ] += 1

    logger.warning(
        "Could not retrieve content for article %s: %s",
        article.id,
        article.title,
    )

    return False