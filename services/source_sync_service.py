from models.article import (
    db,
    Article,
)

from services.article_service import (
    populate_missing_article_dates,
)

from services.discovery_service import (
    discover_source,
)

from services.news_service import (
    categorize_articles,
    filter_vc_articles,
    save_articles_to_database,
)


def run_source_sync(
    source,
    mode="incremental",
    enrichment_limit=1000,
):
    """
    Discover and persist evidence for one configured source.

    This is the single-source operating primitive used by the
    fleet runner.

    Lifecycle:

        discovery
        → relevance
        → categorization
        → URL-deduplicated persistence

    Historical mode additionally performs page/date/content
    enrichment after discovery.

    The operation owns its database transaction so failure of
    one source cannot contaminate another source's run.
    """

    if source is None:
        raise ValueError(
            "Source configuration is required."
        )

    source_name = (
        source.get(
            "name"
        )
    )

    if not source_name:
        raise ValueError(
            "Source configuration missing name."
        )

    normalized_mode = (
        str(mode)
        .strip()
        .lower()
    )

    if normalized_mode not in {
        "incremental",
        "historical",
    }:
        raise ValueError(
            "Unsupported sync mode: "
            f"{mode}"
        )

    if not source.get(
        "enabled",
        True,
    ):
        return {
            "source":
                source_name,

            "source_key":
                source.get(
                    "key"
                ),

            "source_type":
                source.get(
                    "type"
                ),

            "mode":
                normalized_mode,

            "articles_discovered":
                0,

            "articles_relevant":
                0,

            "articles_saved":
                0,

            "dates_populated":
                0,

            "remaining_undated":
                0,
        }

    try:
        discovered = (
            discover_source(
                source
            )
        )

        if discovered is None:
            raise RuntimeError(
                "Discovery failed for "
                f"{source_name}."
            )

        relevant = (
            filter_vc_articles(
                discovered
            )
        )

        categorized = (
            categorize_articles(
                relevant
            )
        )

        saved_count = (
            save_articles_to_database(
                categorized
            )
        )

        dates_populated = 0
        remaining_undated = None

        if (
            normalized_mode
            == "historical"
        ):
            dates_populated = (
                populate_missing_article_dates(
                    source=source_name,
                    limit=enrichment_limit,
                )
            )

            remaining_undated = (
                Article.query
                .filter_by(
                    source=source_name,
                    published_at=None,
                )
                .count()
            )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return {
        "source":
            source_name,

        "source_key":
            source.get(
                "key"
            ),

        "source_type":
            source.get(
                "type"
            ),

        "mode":
            normalized_mode,

        "articles_discovered":
            len(
                discovered
            ),

        "articles_relevant":
            len(
                categorized
            ),

        "articles_saved":
            saved_count,

        "dates_populated":
            dates_populated,

        "remaining_undated":
            remaining_undated,
    }