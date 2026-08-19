from datetime import datetime

from services.event_resolution_service import (
    amounts_match,
    dates_compatible,
    round_types_compatible,
)


def test_identical_amounts_match():
    assert amounts_match(
        40_000_000,
        40_000_000,
    )


def test_small_amount_difference_matches():
    assert amounts_match(
        40_000_000,
        40_500_000,
    )


def test_different_amounts_do_not_match():
    assert not amounts_match(
        40_000_000,
        50_000_000,
    )


def test_same_round_type_is_compatible():
    assert round_types_compatible(
        "Series B",
        "series b",
    )


def test_different_round_types_are_not_compatible():
    assert not round_types_compatible(
        "Series A",
        "Series B",
    )


def test_missing_round_type_is_compatible():
    assert round_types_compatible(
        None,
        "Series B",
    )


def test_close_dates_are_compatible():
    assert dates_compatible(
        datetime(2026, 8, 10),
        datetime(2026, 8, 18),
    )


def test_distant_dates_are_not_compatible():
    assert not dates_compatible(
        datetime(2026, 1, 1),
        datetime(2026, 8, 18),
    )