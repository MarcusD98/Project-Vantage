from services.round_taxonomy_service import (
    canonicalize_round_type,
    normalize_round_type_text,
)


def test_normalizes_round_type():
    assert (
        normalize_round_type_text(
            " Series-A "
        )
        == "series a"
    )


def test_maps_seed():
    assert (
        canonicalize_round_type(
            "Seed round"
        )
        == "Seed"
    )


def test_maps_pre_seed():
    assert (
        canonicalize_round_type(
            "Pre-Seed"
        )
        == "Pre-Seed"
    )


def test_maps_pre_series_a():
    assert (
        canonicalize_round_type(
            "Pre-Series A"
        )
        == "Pre-Series A"
    )


def test_maps_series_a():
    assert (
        canonicalize_round_type(
            "Series A financing"
        )
        == "Series A"
    )


def test_maps_pre_series_b():
    assert (
        canonicalize_round_type(
            "Pre-Series B"
        )
        == "Pre-Series B"
    )


def test_maps_series_b():
    assert (
        canonicalize_round_type(
            "Series B"
        )
        == "Series B"
    )


def test_maps_later_series():
    assert (
        canonicalize_round_type(
            "Series F"
        )
        == "Series E+"
    )


def test_maps_growth():
    assert (
        canonicalize_round_type(
            "Growth equity"
        )
        == "Growth"
    )


def test_maps_venture_debt():
    assert (
        canonicalize_round_type(
            "Venture debt"
        )
        == "Debt"
    )


def test_maps_mixed_equity_and_debt():
    assert (
        canonicalize_round_type(
            "Equity and debt"
        )
        == "Mixed"
    )


def test_maps_safe_note():
    assert (
        canonicalize_round_type(
            "SAFE note"
        )
        == "SAFE"
    )


def test_maps_fidc_to_debt():
    assert (
        canonicalize_round_type(
            "FIDC"
        )
        == "Debt"
    )


def test_maps_strategic():
    assert (
        canonicalize_round_type(
            "Strategic investment"
        )
        == "Strategic"
    )


def test_unknown_round():
    assert (
        canonicalize_round_type(
            "Mystery financing"
        )
        == "Other"
    )


def test_missing_round():
    assert (
        canonicalize_round_type(None)
        is None
    )