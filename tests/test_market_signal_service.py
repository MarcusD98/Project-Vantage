from datetime import datetime

from services.market_signal_service import (
    get_sector_momentum,
)


def _comparison(
    *,
    comparable_investors=3,
    coverage_ratio=1.0,
):
    return {
        "as_of":
            datetime(
                2026,
                6,
                30,
            ),

        "window": {
            "days":
                180,

            "current_start":
                datetime(
                    2026,
                    1,
                    1,
                ),

            "current_end":
                datetime(
                    2026,
                    6,
                    30,
                ),

            "previous_start":
                datetime(
                    2025,
                    7,
                    5,
                ),

            "previous_end":
                datetime(
                    2026,
                    1,
                    1,
                ),
        },

        "cohort": {
            "comparable_investor_count":
                comparable_investors,

            "comparable_investor_names":
                [
                    (
                        f"Investor "
                        f"{index}"
                    )
                    for index
                    in range(
                        comparable_investors
                    )
                ],
        },

        "coverage": {
            "current": {
                "ratio":
                    coverage_ratio,
            },

            "previous": {
                "ratio":
                    coverage_ratio,
            },

            "combined": {
                "ratio":
                    coverage_ratio,
            },
        },

        "current_round_count":
            16,

        "previous_round_count":
            15,

        "comparison": [
            {
                "dimension":
                    "sector",

                "value":
                    "AI Infrastructure",

                "current_event_count":
                    6,

                "previous_event_count":
                    3,

                "delta":
                    3,

                "change_pct":
                    100.0,

                "current_company_count":
                    6,

                "previous_company_count":
                    3,

                "current_investor_count":
                    3,

                "previous_investor_count":
                    2,

                "current_lead_event_count":
                    2,

                "previous_lead_event_count":
                    1,

                "contributing_investors": [
                    "Investor 0",
                    "Investor 1",
                    "Investor 2",
                ],

                "current_event_ids": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                ],

                "previous_event_ids": [
                    7,
                    8,
                    9,
                ],
            },

            {
                "dimension":
                    "sector",

                "value":
                    "Other",

                "current_event_count":
                    8,

                "previous_event_count":
                    10,

                "delta":
                    -2,

                "change_pct":
                    -20.0,

                "current_company_count":
                    8,

                "previous_company_count":
                    10,

                "current_investor_count":
                    3,

                "previous_investor_count":
                    3,

                "current_lead_event_count":
                    2,

                "previous_lead_event_count":
                    3,

                "contributing_investors": [
                    "Investor 0",
                    "Investor 1",
                    "Investor 2",
                ],

                "current_event_ids": [
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                ],

                "previous_event_ids": [
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                ],
            },

            {
                "dimension":
                    "sector",

                "value":
                    "Robotics",

                "current_event_count":
                    1,

                "previous_event_count":
                    0,

                "delta":
                    1,

                "change_pct":
                    None,

                "current_company_count":
                    1,

                "previous_company_count":
                    0,

                "current_investor_count":
                    1,

                "previous_investor_count":
                    0,

                "current_lead_event_count":
                    0,

                "previous_lead_event_count":
                    0,

                "contributing_investors": [
                    "Investor 0"
                ],

                "current_event_ids": [
                    10
                ],

                "previous_event_ids":
                    [],
            },
        ],
    }


def test_sector_momentum_returns_supported_signal(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "services.market_signal_service."
            "compare_market_activity"
        ),
        lambda **kwargs: (
            _comparison()
        ),
    )

    result = (
        get_sector_momentum(
            window_days=180,
        )
    )

    assert (
        result[
            "confidence"
        ][
            "label"
        ]
        == "corpus_supported"
    )

    assert (
        len(
            result[
                "signals"
            ]
        )
        == 1
    )

    signal = (
        result[
            "signals"
        ][0]
    )

    assert (
        signal[
            "value"
        ]
        == "AI Infrastructure"
    )

    assert (
        signal[
            "direction"
        ]
        == "up"
    )

    assert (
        signal[
            "delta"
        ]
        == 3
    )

    assert (
        signal[
            "change_pct"
        ]
        == 100.0
    )

    assert (
        signal[
            "confidence"
        ]
        == "corpus_supported"
    )

    assert (
        signal[
            "signal_eligible"
        ]
        is True
    )


def test_catch_all_sector_remains_measurement_but_not_signal(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "services.market_signal_service."
            "compare_market_activity"
        ),
        lambda **kwargs: (
            _comparison()
        ),
    )

    result = (
        get_sector_momentum()
    )

    other = next(
        item
        for item
        in result[
            "measurements"
        ]
        if item[
            "value"
        ]
        == "Other"
    )

    assert (
        other[
            "status"
        ]
        == "supported"
    )

    assert (
        other[
            "confidence"
        ]
        == "corpus_supported"
    )

    assert (
        other[
            "direction"
        ]
        == "down"
    )

    assert (
        other[
            "signal_eligible"
        ]
        is False
    )

    assert all(
        item[
            "value"
        ]
        != "Other"
        for item
        in result[
            "signals"
        ]
    )


def test_small_comparable_cohort_is_observational(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "services.market_signal_service."
            "compare_market_activity"
        ),
        lambda **kwargs: (
            _comparison(
                comparable_investors=2
            )
        ),
    )

    result = (
        get_sector_momentum()
    )

    assert (
        result[
            "confidence"
        ][
            "label"
        ]
        == "observational"
    )

    assert (
        result[
            "signals"
        ][0][
            "confidence"
        ]
        == "observational"
    )


def test_new_low_volume_sector_is_not_promoted_to_signal(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "services.market_signal_service."
            "compare_market_activity"
        ),
        lambda **kwargs: (
            _comparison()
        ),
    )

    result = (
        get_sector_momentum()
    )

    robotics = next(
        item
        for item
        in result[
            "measurements"
        ]
        if item[
            "value"
        ]
        == "Robotics"
    )

    assert (
        robotics[
            "status"
        ]
        == "insufficient"
    )

    assert (
        robotics[
            "confidence"
        ]
        == "insufficient"
    )

    assert all(
        item[
            "value"
        ]
        != "Robotics"
        for item
        in result[
            "signals"
        ]
    )


def test_low_sector_coverage_downgrades_confidence(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "services.market_signal_service."
            "compare_market_activity"
        ),
        lambda **kwargs: (
            _comparison(
                coverage_ratio=0.50
            )
        ),
    )

    result = (
        get_sector_momentum()
    )

    assert (
        result[
            "confidence"
        ][
            "label"
        ]
        == "observational"
    )