import pytest

from services.backfill_service import (
    _get_backfill_source,
    get_backfill_source_names,
    run_source_backfill,
)


def test_get_configured_backfill_source():
    source = _get_backfill_source(
        "TechCrunch"
    )

    assert source is not None

    assert (
        source["method"]
        == "html"
    )


def test_get_unknown_backfill_source():
    source = _get_backfill_source(
        "Not Real"
    )

    assert source is None


def test_get_backfill_source_names():
    names = (
        get_backfill_source_names()
    )

    assert "TechCrunch" in names


def test_unknown_backfill_source_raises():
    with pytest.raises(
        ValueError
    ):
        run_source_backfill(
            "Not Real"
        )