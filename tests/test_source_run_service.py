import pytest

from models.article import db

from models.source_run import (
    SourceRun,
)

from services.source_run_service import (
    finish_source_run,
    get_recent_source_runs,
    start_source_run,
)


def _source():
    return {
        "key":
            "test-source",

        "name":
            "Test Source",

        "type":
            "investor",
    }


def test_start_source_run_persists_running_record(
    app,
):
    source_run = (
        start_source_run(
            source=_source(),
            mode="incremental",
            process_enabled=False,
        )
    )

    persisted = (
        db.session.get(
            SourceRun,
            source_run.id,
        )
    )

    assert persisted is not None

    assert (
        persisted.source_key
        == "test-source"
    )

    assert (
        persisted.status
        == "running"
    )

    assert (
        persisted.finished_at
        is None
    )


def test_finish_source_run_persists_discovery_stats(
    app,
):
    source_run = (
        start_source_run(
            source=_source(),
            mode="incremental",
        )
    )

    finished = (
        finish_source_run(
            source_run=source_run,
            status="success",
            discovery={
                "articles_discovered":
                    20,

                "articles_relevant":
                    12,

                "articles_saved":
                    4,

                "dates_populated":
                    0,

                "remaining_undated":
                    None,
            },
        )
    )

    assert (
        finished.status
        == "success"
    )

    assert (
        finished.articles_discovered
        == 20
    )

    assert (
        finished.articles_relevant
        == 12
    )

    assert (
        finished.articles_saved
        == 4
    )

    assert (
        finished.finished_at
        is not None
    )


def test_finish_source_run_persists_processing_stats(
    app,
):
    source_run = (
        start_source_run(
            source=_source(),
            mode="incremental",
            process_enabled=True,
        )
    )

    finished = (
        finish_source_run(
            source_run=source_run,
            status="warning",
            discovery={
                "articles_discovered":
                    10,

                "articles_relevant":
                    8,

                "articles_saved":
                    2,

                "dates_populated":
                    0,
            },
            processing={
                "articles_selected":
                    5,

                "stale_articles_skipped":
                    1,

                "compound_articles_skipped":
                    1,

                "content_retrieved":
                    3,

                "content_failed":
                    0,

                "funding_processed":
                    4,

                "funding_rounds":
                    3,

                "fund_news_processed":
                    1,

                "fund_closes":
                    1,

                "processing_failed":
                    1,
            },
        )
    )

    assert (
        finished.status
        == "warning"
    )

    assert (
        finished.articles_selected
        == 5
    )

    assert (
        finished.funding_processed
        == 4
    )

    assert (
        finished.funding_rounds
        == 3
    )

    assert (
        finished.fund_closes
        == 1
    )

    assert (
        finished.processing_failed
        == 1
    )


def test_failed_source_run_preserves_error(
    app,
):
    source_run = (
        start_source_run(
            source=_source(),
            mode="historical",
        )
    )

    finished = (
        finish_source_run(
            source_run=source_run,
            status="failed",
            error=(
                "Discovery failed"
            ),
        )
    )

    assert (
        finished.status
        == "failed"
    )

    assert (
        finished.error
        == "Discovery failed"
    )


def test_recent_source_runs_can_filter_by_status(
    app,
):
    first = (
        start_source_run(
            source=_source(),
            mode="incremental",
        )
    )

    finish_source_run(
        source_run=first,
        status="success",
    )

    second = (
        start_source_run(
            source=_source(),
            mode="incremental",
        )
    )

    finish_source_run(
        source_run=second,
        status="failed",
        error="Failure",
    )

    failed_runs = (
        get_recent_source_runs(
            status="failed",
        )
    )

    assert len(
        failed_runs
    ) == 1

    assert (
        failed_runs[0].id
        == second.id
    )


def test_invalid_source_run_status_raises(
    app,
):
    source_run = (
        start_source_run(
            source=_source(),
            mode="incremental",
        )
    )

    with pytest.raises(
        ValueError
    ):
        finish_source_run(
            source_run=source_run,
            status="banana",
        )