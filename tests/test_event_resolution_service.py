from datetime import datetime

from services.event_resolution_service import (
    amounts_match,
    currencies_match,
    dates_compatible,
    funding_event_matches,
    normalize_currency,
    normalize_round_type,
    round_types_compatible,
)


def test_normalizes_round_type():
    assert (
        normalize_round_type(
            "Series-B"
        )
        == "series b"
    )


def test_normalizes_currency():
    assert (
        normalize_currency(
            " usd "
        )
        == "USD"
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


def test_large_amount_difference_does_not_match():
    assert not amounts_match(
        40_000_000,
        50_000_000,
    )


def test_missing_amount_does_not_match():
    assert not amounts_match(
        None,
        40_000_000,
    )


def test_same_currency_matches():
    assert currencies_match(
        "USD",
        "usd",
    )


def test_different_currency_does_not_match():
    assert not currencies_match(
        "USD",
        "EUR",
    )


def test_missing_currency_does_not_match():
    assert not currencies_match(
        None,
        "USD",
    )


def test_same_round_type_is_compatible():
    assert round_types_compatible(
        "Series B",
        "series b",
    )


def test_hyphenated_round_type_is_compatible():
    assert round_types_compatible(
        "Series-B",
        "Series B",
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
        datetime(
            2026,
            8,
            10,
        ),
        datetime(
            2026,
            8,
            18,
        ),
    )


def test_distant_dates_are_not_compatible():
    assert not dates_compatible(
        datetime(
            2026,
            1,
            1,
        ),
        datetime(
            2026,
            8,
            18,
        ),
    )


def test_matching_funding_event():
    assert funding_event_matches(
        company_id_a=1,
        amount_a=20_000_000,
        currency_a="USD",
        round_type_a="Series A",
        announced_at_a=datetime(
            2026,
            8,
            10,
        ),

        company_id_b=1,
        amount_b=20_100_000,
        currency_b="USD",
        round_type_b="Series A",
        announced_at_b=datetime(
            2026,
            8,
            12,
        ),
    )


def test_different_company_is_not_same_event():
    assert not funding_event_matches(
        company_id_a=1,
        amount_a=20_000_000,
        currency_a="USD",
        round_type_a="Series A",
        announced_at_a=datetime(
            2026,
            8,
            10,
        ),

        company_id_b=2,
        amount_b=20_000_000,
        currency_b="USD",
        round_type_b="Series A",
        announced_at_b=datetime(
            2026,
            8,
            10,
        ),
    )


def test_different_currency_is_not_same_event():
    assert not funding_event_matches(
        company_id_a=1,
        amount_a=20_000_000,
        currency_a="USD",
        round_type_a="Series A",
        announced_at_a=datetime(
            2026,
            8,
            10,
        ),

        company_id_b=1,
        amount_b=20_000_000,
        currency_b="EUR",
        round_type_b="Series A",
        announced_at_b=datetime(
            2026,
            8,
            10,
        ),
    )


def test_different_round_is_not_same_event():
    assert not funding_event_matches(
        company_id_a=1,
        amount_a=20_000_000,
        currency_a="USD",
        round_type_a="Series A",
        announced_at_a=datetime(
            2026,
            8,
            10,
        ),

        company_id_b=1,
        amount_b=20_000_000,
        currency_b="USD",
        round_type_b="Series B",
        announced_at_b=datetime(
            2026,
            8,
            10,
        ),
    )


def test_distant_event_is_not_same_event():
    assert not funding_event_matches(
        company_id_a=1,
        amount_a=20_000_000,
        currency_a="USD",
        round_type_a="Series A",
        announced_at_a=datetime(
            2026,
            1,
            1,
        ),

        company_id_b=1,
        amount_b=20_000_000,
        currency_b="USD",
        round_type_b="Series A",
        announced_at_b=datetime(
            2026,
            8,
            10,
        ),
    )


def test_sparse_event_can_match_when_amount_is_missing():
    assert funding_event_matches(
        company_id_a=1,
        amount_a=None,
        currency_a="USD",
        round_type_a="Series A",
        announced_at_a=datetime(
            2026,
            8,
            10,
        ),

        company_id_b=1,
        amount_b=20_000_000,
        currency_b="USD",
        round_type_b="Series A",
        announced_at_b=datetime(
            2026,
            8,
            11,
        ),
    )


def test_sparse_event_can_match_when_currency_is_missing():
    assert funding_event_matches(
        company_id_a=1,
        amount_a=20_000_000,
        currency_a=None,
        round_type_a="Series A",
        announced_at_a=datetime(
            2026,
            8,
            10,
        ),

        company_id_b=1,
        amount_b=20_000_000,
        currency_b="USD",
        round_type_b="Series A",
        announced_at_b=datetime(
            2026,
            8,
            11,
        ),
    )


def test_sparse_event_requires_known_matching_round_type():
    assert not funding_event_matches(
        company_id_a=1,
        amount_a=None,
        currency_a=None,
        round_type_a=None,
        announced_at_a=datetime(
            2026,
            8,
            10,
        ),

        company_id_b=1,
        amount_b=None,
        currency_b=None,
        round_type_b=None,
        announced_at_b=datetime(
            2026,
            8,
            11,
        ),
    )


def test_sparse_event_uses_tight_date_window():
    assert not funding_event_matches(
        company_id_a=1,
        amount_a=None,
        currency_a=None,
        round_type_a="Series A",
        announced_at_a=datetime(
            2026,
            8,
            10,
        ),

        company_id_b=1,
        amount_b=None,
        currency_b=None,
        round_type_b="Series A",
        announced_at_b=datetime(
            2026,
            8,
            14,
        ),
    )