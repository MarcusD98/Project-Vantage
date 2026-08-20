from datetime import (
    datetime,
    timezone,
)

from models.article import db

from models.source_run import (
    SourceRun,
)


VALID_SOURCE_RUN_STATUSES = {
    "running",
    "success",
    "warning",
    "partial",
    "failed",
}


def _utcnow():
    """
    Return a naive UTC datetime.

    Existing Vantage SQLite models primarily use naive
    datetimes, so SourceRun follows the same persistence
    convention while treating values as UTC.
    """

    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )
    )


def _integer_value(
    result,
    key,
):
    if not result:
        return 0

    value = result.get(
        key,
        0,
    )

    if value is None:
        return 0

    return int(
        value
    )


def start_source_run(
    source,
    mode,
    process_enabled=False,
):
    """
    Persist the beginning of one source operation.

    The row is committed immediately.

    If the application later terminates unexpectedly, the
    surviving 'running' row becomes useful evidence that an
    operation did not finish cleanly.
    """

    if source is None:
        raise ValueError(
            "Source configuration is required."
        )

    source_key = (
        source.get(
            "key"
        )
    )

    source_name = (
        source.get(
            "name"
        )
    )

    if not source_key:
        raise ValueError(
            "Source configuration missing key."
        )

    if not source_name:
        raise ValueError(
            "Source configuration missing name."
        )

    source_run = SourceRun(
        source_key=source_key,
        source_name=source_name,
        source_type=source.get(
            "type"
        ),
        mode=mode,
        process_enabled=bool(
            process_enabled
        ),
        status="running",
        started_at=_utcnow(),
    )

    try:
        db.session.add(
            source_run
        )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return source_run


def finish_source_run(
    source_run,
    status,
    discovery=None,
    processing=None,
    error=None,
):
    """
    Finalize one persisted source operation.

    Discovery and intelligence statistics are copied onto the
    operational record so source-network history can later be
    analyzed without reconstructing CLI output.
    """

    normalized_status = (
        str(status)
        .strip()
        .lower()
    )

    if (
        normalized_status
        not in VALID_SOURCE_RUN_STATUSES
    ):
        raise ValueError(
            "Unsupported SourceRun status: "
            f"{status}"
        )

    if source_run is None:
        raise ValueError(
            "SourceRun is required."
        )

    persisted_run = (
        db.session.get(
            SourceRun,
            source_run.id,
        )
    )

    if persisted_run is None:
        raise ValueError(
            "SourceRun no longer exists."
        )

    # -----------------------------------------------------
    # Discovery
    # -----------------------------------------------------

    persisted_run.articles_discovered = (
        _integer_value(
            discovery,
            "articles_discovered",
        )
    )

    persisted_run.articles_relevant = (
        _integer_value(
            discovery,
            "articles_relevant",
        )
    )

    persisted_run.articles_saved = (
        _integer_value(
            discovery,
            "articles_saved",
        )
    )

    persisted_run.dates_populated = (
        _integer_value(
            discovery,
            "dates_populated",
        )
    )

    if discovery is not None:
        persisted_run.remaining_undated = (
            discovery.get(
                "remaining_undated"
            )
        )

    # -----------------------------------------------------
    # Intelligence
    # -----------------------------------------------------

    persisted_run.articles_selected = (
        _integer_value(
            processing,
            "articles_selected",
        )
    )

    persisted_run.stale_articles_skipped = (
        _integer_value(
            processing,
            "stale_articles_skipped",
        )
    )

    persisted_run.compound_articles_skipped = (
        _integer_value(
            processing,
            "compound_articles_skipped",
        )
    )

    persisted_run.content_retrieved = (
        _integer_value(
            processing,
            "content_retrieved",
        )
    )

    persisted_run.content_failed = (
        _integer_value(
            processing,
            "content_failed",
        )
    )

    persisted_run.funding_processed = (
        _integer_value(
            processing,
            "funding_processed",
        )
    )

    persisted_run.funding_rounds = (
        _integer_value(
            processing,
            "funding_rounds",
        )
    )

    persisted_run.fund_news_processed = (
        _integer_value(
            processing,
            "fund_news_processed",
        )
    )

    persisted_run.fund_closes = (
        _integer_value(
            processing,
            "fund_closes",
        )
    )

    persisted_run.processing_failed = (
        _integer_value(
            processing,
            "processing_failed",
        )
    )

    # -----------------------------------------------------
    # Final state
    # -----------------------------------------------------

    persisted_run.status = (
        normalized_status
    )

    persisted_run.finished_at = (
        _utcnow()
    )

    persisted_run.error = (
        str(error)
        if error is not None
        else None
    )

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return persisted_run


def get_recent_source_runs(
    limit=20,
    source_name=None,
    status=None,
):
    """
    Return recent source operations newest-first.
    """

    try:
        limit = int(
            limit
        )

    except (
        TypeError,
        ValueError,
    ):
        limit = 20

    if limit <= 0:
        return []

    query = (
        SourceRun.query
    )

    if source_name:
        query = query.filter(
            SourceRun.source_name
            == source_name
        )

    if status:
        normalized_status = (
            str(status)
            .strip()
            .lower()
        )

        if (
            normalized_status
            not in VALID_SOURCE_RUN_STATUSES
        ):
            raise ValueError(
                "Unsupported SourceRun status: "
                f"{status}"
            )

        query = query.filter(
            SourceRun.status
            == normalized_status
        )

    return (
        query
        .order_by(
            SourceRun.started_at.desc(),
            SourceRun.id.desc(),
        )
        .limit(
            limit
        )
        .all()
    )