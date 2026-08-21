from types import (
    SimpleNamespace,
)

import pytest

from services import (
    fleet_service,
)

from services.fleet_service import (
    run_source_fleet,
    select_source_fleet,
)


def _patch_run_persistence(
    monkeypatch,
):
    counter = {
        "value": 0,
    }

    def fake_start(
        source,
        mode,
        process_enabled,
    ):
        counter[
            "value"
        ] += 1

        return SimpleNamespace(
            id=counter[
                "value"
            ]
        )

    def fake_finish(
        source_run,
        status,
        discovery=None,
        processing=None,
        error=None,
    ):
        return source_run

    monkeypatch.setattr(
        fleet_service,
        "start_source_run",
        fake_start,
    )

    monkeypatch.setattr(
        fleet_service,
        "finish_source_run",
        fake_finish,
    )


def test_select_incremental_investor_fleet():
    fleet = (
        select_source_fleet(
            mode="incremental",
            source_type="investor",
        )
    )

    names = {
        source["name"]
        for source in fleet
    }

    assert names == {
        "Accel",
        "Index Ventures",
        "Sequoia Capital",
        "Andreessen Horowitz",
        "General Catalyst",
        "Bessemer Venture Partners",
        "Greylock",
        "NEA",
        "Balderton Capital",
        "Insight Partners",
        "Lightspeed Venture Partners",
        "Menlo Ventures",
        "Felicis",
        "Creandum",
        "Dawn Capital",
        "Redpoint Ventures",
        "GV",
        "Northzone",
        "DCVC",
    }


def test_select_historical_fleet():
    fleet = (
        select_source_fleet(
            mode="historical"
        )
    )

    names = [
        source["name"]
        for source in fleet
    ]

    assert names == [
        "TechCrunch",
        "Accel",
        "Index Ventures",
        "Sequoia Capital",
        "Bessemer Venture Partners",
        "Greylock",
        "Lightspeed Venture Partners",
        "Menlo Ventures",
        "Felicis",
        "Creandum",
        "Dawn Capital",
        "Redpoint Ventures",
        "GV",
        "Northzone",
        "DCVC",
    ]

def test_select_source_by_name():
    fleet = (
        select_source_fleet(
            mode="incremental",
            source_names=[
                "Accel",
            ],
        )
    )

    assert len(
        fleet
    ) == 1

    assert (
        fleet[0]["name"]
        == "Accel"
    )


def test_select_source_by_key():
    fleet = (
        select_source_fleet(
            mode="incremental",
            source_names=[
                "sequoia-capital",
            ],
        )
    )

    assert len(
        fleet
    ) == 1

    assert (
        fleet[0]["name"]
        == "Sequoia Capital"
    )


def test_unavailable_source_raises():
    with pytest.raises(
        ValueError
    ):
        select_source_fleet(
            mode="historical",
            source_names=[
                "Sifted",
            ],
        )


def test_fleet_continues_after_source_failure(
    monkeypatch,
):
    _patch_run_persistence(
        monkeypatch
    )

    fleet = [
        {
            "key": "one",
            "name": "One",
            "type": "publication",
        },
        {
            "key": "two",
            "name": "Two",
            "type": "publication",
        },
    ]

    monkeypatch.setattr(
        fleet_service,
        "select_source_fleet",
        lambda **kwargs: fleet,
    )

    def fake_sync(
        source,
        mode,
        enrichment_limit,
    ):
        if (
            source["name"]
            == "One"
        ):
            raise RuntimeError(
                "Source failed"
            )

        return {
            "source":
                source["name"],

            "articles_discovered":
                5,

            "articles_relevant":
                3,

            "articles_saved":
                2,

            "dates_populated":
                0,
        }

    monkeypatch.setattr(
        fleet_service,
        "run_source_sync",
        fake_sync,
    )

    result = (
        run_source_fleet()
    )

    assert (
        result["totals"][
            "sources_selected"
        ]
        == 2
    )

    assert (
        result["totals"][
            "sources_failed"
        ]
        == 1
    )

    assert (
        result["totals"][
            "sources_succeeded"
        ]
        == 1
    )

    assert (
        result["totals"][
            "articles_saved"
        ]
        == 2
    )

    assert (
        result["results"][0][
            "status"
        ]
        == "failed"
    )

    assert (
        result["results"][1][
            "status"
        ]
        == "success"
    )


def test_zero_yield_discovery_is_warning(
    monkeypatch,
):
    _patch_run_persistence(
        monkeypatch
    )

    fleet = [
        {
            "key": "empty",
            "name": "Empty Source",
            "type": "investor",
        },
    ]

    monkeypatch.setattr(
        fleet_service,
        "select_source_fleet",
        lambda **kwargs: fleet,
    )

    monkeypatch.setattr(
        fleet_service,
        "run_source_sync",
        lambda **kwargs: {
            "source":
                "Empty Source",

            "articles_discovered":
                0,

            "articles_relevant":
                0,

            "articles_saved":
                0,

            "dates_populated":
                0,
        },
    )

    result = (
        run_source_fleet(
            process=False
        )
    )

    assert (
        result["results"][0][
            "status"
        ]
        == "warning"
    )

    assert (
        result["totals"][
            "sources_warning"
        ]
        == 1
    )

    assert (
        result["totals"][
            "sources_succeeded"
        ]
        == 0
    )

    assert (
        result["totals"][
            "sources_failed"
        ]
        == 0
    )


def test_zero_new_saves_can_still_succeed(
    monkeypatch,
):
    _patch_run_persistence(
        monkeypatch
    )

    fleet = [
        {
            "key": "known",
            "name": "Known Source",
            "type": "investor",
        },
    ]

    monkeypatch.setattr(
        fleet_service,
        "select_source_fleet",
        lambda **kwargs: fleet,
    )

    monkeypatch.setattr(
        fleet_service,
        "run_source_sync",
        lambda **kwargs: {
            "source":
                "Known Source",

            "articles_discovered":
                25,

            "articles_relevant":
                25,

            "articles_saved":
                0,

            "dates_populated":
                0,
        },
    )

    result = (
        run_source_fleet(
            process=False
        )
    )

    assert (
        result["results"][0][
            "status"
        ]
        == "success"
    )

    assert (
        result["totals"][
            "sources_succeeded"
        ]
        == 1
    )

    assert (
        result["totals"][
            "sources_warning"
        ]
        == 0
    )


def test_fleet_does_not_process_by_default(
    monkeypatch,
):
    _patch_run_persistence(
        monkeypatch
    )

    fleet = [
        {
            "key": "one",
            "name": "One",
            "type": "publication",
        },
    ]

    monkeypatch.setattr(
        fleet_service,
        "select_source_fleet",
        lambda **kwargs: fleet,
    )

    monkeypatch.setattr(
        fleet_service,
        "run_source_sync",
        lambda **kwargs: {
            "source": "One",
            "articles_discovered": 5,
            "articles_relevant": 3,
            "articles_saved": 1,
            "dates_populated": 0,
        },
    )

    def should_not_run(
        **kwargs,
    ):
        raise AssertionError(
            "Processing should not run."
        )

    monkeypatch.setattr(
        fleet_service,
        "run_stored_intelligence",
        should_not_run,
    )

    result = (
        run_source_fleet(
            process=False
        )
    )

    assert (
        result["totals"][
            "sources_succeeded"
        ]
        == 1
    )

    assert (
        result["totals"][
            "funding_processed"
        ]
        == 0
    )


def test_fleet_aggregates_processing(
    monkeypatch,
):
    _patch_run_persistence(
        monkeypatch
    )

    fleet = [
        {
            "key": "one",
            "name": "One",
            "type": "investor",
        },
        {
            "key": "two",
            "name": "Two",
            "type": "investor",
        },
    ]

    monkeypatch.setattr(
        fleet_service,
        "select_source_fleet",
        lambda **kwargs: fleet,
    )

    monkeypatch.setattr(
        fleet_service,
        "run_source_sync",
        lambda source, **kwargs: {
            "source":
                source["name"],

            "articles_discovered":
                4,

            "articles_relevant":
                3,

            "articles_saved":
                2,

            "dates_populated":
                0,
        },
    )

    monkeypatch.setattr(
        fleet_service,
        "run_stored_intelligence",
        lambda **kwargs: {
            "articles_selected":
                2,

            "stale_articles_skipped":
                0,

            "compound_articles_skipped":
                0,

            "content_retrieved":
                0,

            "content_failed":
                0,

            "funding_processed":
                2,

            "funding_rounds":
                2,

            "fund_news_processed":
                0,

            "fund_closes":
                0,

            "processing_failed":
                0,
        },
    )

    result = (
        run_source_fleet(
            process=True
        )
    )

    totals = result[
        "totals"
    ]

    assert (
        totals[
            "sources_succeeded"
        ]
        == 2
    )

    assert (
        totals[
            "sources_warning"
        ]
        == 0
    )

    assert (
        totals[
            "articles_discovered"
        ]
        == 8
    )

    assert (
        totals[
            "articles_saved"
        ]
        == 4
    )

    assert (
        totals[
            "articles_selected"
        ]
        == 4
    )

    assert (
        totals[
            "funding_processed"
        ]
        == 4
    )

    assert (
        totals[
            "funding_rounds"
        ]
        == 4
    )


def test_processing_preserves_zero_yield_warning(
    monkeypatch,
):
    _patch_run_persistence(
        monkeypatch
    )

    fleet = [
        {
            "key": "empty",
            "name": "Empty Source",
            "type": "investor",
        },
    ]

    monkeypatch.setattr(
        fleet_service,
        "select_source_fleet",
        lambda **kwargs: fleet,
    )

    monkeypatch.setattr(
        fleet_service,
        "run_source_sync",
        lambda **kwargs: {
            "source":
                "Empty Source",

            "articles_discovered":
                0,

            "articles_relevant":
                0,

            "articles_saved":
                0,

            "dates_populated":
                0,
        },
    )

    monkeypatch.setattr(
        fleet_service,
        "run_stored_intelligence",
        lambda **kwargs: {
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
        },
    )

    result = (
        run_source_fleet(
            process=True
        )
    )

    assert (
        result["results"][0][
            "status"
        ]
        == "warning"
    )

    assert (
        result["totals"][
            "sources_warning"
        ]
        == 1
    )

    assert (
        result["totals"][
            "sources_succeeded"
        ]
        == 0
    )


def test_historical_fleet_uses_historical_processing(
    monkeypatch,
):
    _patch_run_persistence(
        monkeypatch
    )

    fleet = [
        {
            "key": "historical-one",
            "name": "Historical One",
            "type": "investor",
        },
    ]

    monkeypatch.setattr(
        fleet_service,
        "select_source_fleet",
        lambda **kwargs: fleet,
    )

    monkeypatch.setattr(
        fleet_service,
        "run_source_sync",
        lambda source, **kwargs: {
            "source":
                source["name"],

            "articles_discovered":
                3,

            "articles_relevant":
                2,

            "articles_saved":
                2,

            "dates_populated":
                2,
        },
    )

    captured = {}

    def fake_process(
        **kwargs,
    ):
        captured.update(
            kwargs
        )

        return {
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

    monkeypatch.setattr(
        fleet_service,
        "run_stored_intelligence",
        fake_process,
    )

    result = (
        run_source_fleet(
            mode="historical",
            process=True,
        )
    )

    assert (
        captured[
            "historical"
        ]
        is True
    )

    assert (
        result["totals"][
            "sources_succeeded"
        ]
        == 1
    )