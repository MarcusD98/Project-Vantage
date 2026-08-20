from backfill_config import (
    BACKFILL_SOURCES,
)

from models.article import db

from services.discovery_service import (
    discover_source,
)

from services.news_service import (
    categorize_articles,
    filter_vc_articles,
    save_articles_to_database,
)


def _get_backfill_source(
    source_name,
):
    """
    Return one configured backfill source by name.
    """

    for source in BACKFILL_SOURCES:
        if (
            source.get("name")
            == source_name
        ):
            return source

    return None


def run_source_backfill(
    source_name,
):
    """
    Discover and persist historical evidence for one
    configured backfill source.

    Backfill deliberately reuses the normal Vantage evidence
    pipeline:

        discovery
        → relevance
        → categorization
        → URL deduplication
        → Article persistence

    Existing URLs are ignored by the normal persistence layer.

    Transaction ownership belongs to the caller.
    """

    source = _get_backfill_source(
        source_name
    )

    if source is None:
        raise ValueError(
            f"Unknown backfill source: "
            f"{source_name}"
        )

    if not source.get(
        "enabled",
        True,
    ):
        return {
            "source":
                source_name,

            "articles_discovered":
                0,

            "articles_relevant":
                0,

            "articles_saved":
                0,
        }

    discovered = (
        discover_source(
            source
        )
    )

    if discovered is None:
        return {
            "source":
                source_name,

            "articles_discovered":
                0,

            "articles_relevant":
                0,

            "articles_saved":
                0,
        }

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

    db.session.flush()

    return {
        "source":
            source_name,

        "articles_discovered":
            len(discovered),

        "articles_relevant":
            len(categorized),

        "articles_saved":
            saved_count,
    }


def get_backfill_source_names():
    """
    Return enabled configured backfill source names.
    """

    return [
        source["name"]
        for source in BACKFILL_SOURCES
        if source.get(
            "enabled",
            True,
        )
    ]