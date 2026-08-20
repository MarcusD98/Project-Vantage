import pytest

from services import (
    fleet_service,
)

from services.fleet_service import (
    run_source_fleet,
    select_source_fleet,
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


def test_fleet_does_not_process_by_default(
    monkeypatch,
):
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