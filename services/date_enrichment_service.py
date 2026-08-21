from models.article import (
    Article,
    db,
)

from source_registry import (
    get_source,
)

from services.article_service import (
    populate_missing_article_dates,
)


def _percentage(
    numerator,
    denominator,
):
    """
    Return a percentage rounded to one decimal place.
    """

    if not denominator:
        return 0.0

    return round(
        (
            numerator
            / denominator
        )
        * 100,
        1,
    )


def _count_undated_articles(
    source_name,
):
    """
    Count persisted evidence for one source whose publication
    date is still unknown.
    """

    return (
        Article.query
        .filter(
            Article.source
            == source_name,

            Article.published_at
            .is_(
                None
            ),
        )
        .count()
    )


def run_date_enrichment(
    *,
    source_name,
    limit=20,
):
    """
    Attempt publication-date recovery for persisted evidence
    belonging to one configured Vantage source.

    This operation performs no discovery, LLM extraction, or
    canonical knowledge mutation.

    Lifecycle:

        existing undated evidence
            ↓
        fetch source page
            ↓
        generic structured date extraction
            ↓
        Article.published_at
            ↓
        commit

    Existing publication dates are never overwritten.

    Returns operator-facing measurements describing:

    - undated evidence before the run
    - number of pages selected for enrichment
    - dates recovered
    - undated evidence remaining
    - recovery rate for the attempted batch
    """

    if not source_name:
        raise ValueError(
            "source_name is required."
        )

    source = get_source(
        source_name
    )

    if source is None:
        raise ValueError(
            f"Unknown source: {source_name}"
        )

    canonical_source_name = (
        source[
            "name"
        ]
    )

    if limit is None:
        raise ValueError(
            "limit is required."
        )

    if not isinstance(
        limit,
        int,
    ):
        raise TypeError(
            "limit must be an integer."
        )

    if limit < 0:
        raise ValueError(
            "limit cannot be negative."
        )

    undated_before = (
        _count_undated_articles(
            canonical_source_name
        )
    )

    attempted = min(
        undated_before,
        limit,
    )

    if attempted == 0:
        return {
            "source":
                canonical_source_name,

            "source_key":
                source[
                    "key"
                ],

            "limit":
                limit,

            "undated_before":
                undated_before,

            "attempted":
                0,

            "dates_recovered":
                0,

            "remaining_undated":
                undated_before,

            "recovery_rate":
                0.0,
        }

    try:
        dates_recovered = (
            populate_missing_article_dates(
                source=canonical_source_name,
                limit=limit,
            )
        )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    remaining_undated = (
        _count_undated_articles(
            canonical_source_name
        )
    )

    return {
        "source":
            canonical_source_name,

        "source_key":
            source[
                "key"
            ],

        "limit":
            limit,

        "undated_before":
            undated_before,

        "attempted":
            attempted,

        "dates_recovered":
            dates_recovered,

        "remaining_undated":
            remaining_undated,

        "recovery_rate":
            _percentage(
                dates_recovered,
                attempted,
            ),
    }