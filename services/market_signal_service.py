from services.market_comparison_service import (
    compare_market_activity,
)


MIN_COMPARABLE_INVESTORS = 3
MIN_SECTOR_COMBINED_EVENTS = 4
MIN_SECTOR_PREVIOUS_EVENTS = 1
MIN_SECTOR_COVERAGE = 0.60


# Catch-all taxonomy values remain valid measurements because
# they describe the observed corpus, but they are not meaningful
# enough to promote as market-intelligence signals.
NON_SIGNAL_DIMENSION_VALUES = {
    "other",
    "unknown",
    "unclassified",
}


def _positive_integer(
    value,
    name,
):
    try:
        value = int(value)

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            f"{name} must be an integer."
        ) from exc

    if value <= 0:
        raise ValueError(
            f"{name} must be greater than zero."
        )

    return value


def _direction(delta):
    if delta > 0:
        return "up"

    if delta < 0:
        return "down"

    return "flat"


def _is_signal_dimension_value(
    value,
):
    if value is None:
        return False

    return (
        str(value)
        .strip()
        .casefold()
        not in NON_SIGNAL_DIMENSION_VALUES
    )


def _comparison_confidence(
    comparison,
):
    comparable_count = (
        comparison[
            "cohort"
        ][
            "comparable_investor_count"
        ]
    )

    sector_coverage = (
        comparison[
            "coverage"
        ][
            "combined"
        ][
            "ratio"
        ]
    )

    if comparable_count == 0:
        return {
            "label":
                "insufficient",

            "reason": (
                "No investors have complete comparable "
                "first-party corpus coverage across both "
                "analysis windows."
            ),
        }

    if (
        comparable_count
        < MIN_COMPARABLE_INVESTORS
    ):
        return {
            "label":
                "observational",

            "reason": (
                "Comparable cohort contains fewer than "
                f"{MIN_COMPARABLE_INVESTORS} investors."
            ),
        }

    if (
        sector_coverage
        < MIN_SECTOR_COVERAGE
    ):
        return {
            "label":
                "observational",

            "reason": (
                "Known sector coverage across the comparable "
                "cohort is below "
                f"{MIN_SECTOR_COVERAGE:.0%}."
            ),
        }

    return {
        "label":
            "corpus_supported",

        "reason":
            None,
    }


def _qualify_sector_measurement(
    row,
    confidence,
):
    current_count = (
        row[
            "current_event_count"
        ]
    )

    previous_count = (
        row[
            "previous_event_count"
        ]
    )

    combined_count = (
        current_count
        + previous_count
    )

    if (
        combined_count
        < MIN_SECTOR_COMBINED_EVENTS
    ):
        status = (
            "insufficient"
        )

        reason = (
            "Need at least "
            f"{MIN_SECTOR_COMBINED_EVENTS} "
            "observed sector events across the "
            "two comparison windows."
        )

    elif (
        previous_count
        < MIN_SECTOR_PREVIOUS_EVENTS
    ):
        status = (
            "insufficient"
        )

        reason = (
            "Need at least "
            f"{MIN_SECTOR_PREVIOUS_EVENTS} "
            "observed sector event in the previous "
            "window before calculating momentum."
        )

    else:
        status = (
            "supported"
        )

        reason = None

    result = dict(
        row
    )

    result[
        "status"
    ] = status

    result[
        "direction"
    ] = (
        _direction(
            row[
                "delta"
            ]
        )
    )

    result[
        "confidence"
    ] = (
        confidence[
            "label"
        ]
        if status
        == "supported"
        else "insufficient"
    )

    result[
        "confidence_reason"
    ] = (
        confidence[
            "reason"
        ]
        if status
        == "supported"
        else reason
    )

    result[
        "signal_eligible"
    ] = (
        _is_signal_dimension_value(
            row[
                "value"
            ]
        )
    )

    return result


def _signal_sort_key(item):
    direction_rank = {
        "up": 0,
        "down": 1,
        "flat": 2,
    }

    return (
        direction_rank[
            item[
                "direction"
            ]
        ],
        -abs(
            item[
                "delta"
            ]
        ),
        -item[
            "current_event_count"
        ],
        item[
            "value"
        ].casefold(),
    )


def get_sector_momentum(
    *,
    window_days=180,
    as_of=None,
    investor_names=None,
    limit=10,
):
    """
    Build deterministic sector-momentum signals from canonical
    funding events inside a temporally comparable investor cohort.

    The underlying measurement comes from canonical events.
    No LLM determines whether a sector is rising or falling.

    Catch-all taxonomy values such as Other remain visible in
    measurements but are deliberately excluded from promoted
    market signals.
    """

    limit = (
        _positive_integer(
            limit,
            "limit",
        )
    )

    comparison = (
        compare_market_activity(
            dimension="sector",
            window_days=window_days,
            as_of=as_of,
            investor_names=(
                investor_names
            ),
        )
    )

    confidence = (
        _comparison_confidence(
            comparison
        )
    )

    measurements = [
        _qualify_sector_measurement(
            row,
            confidence,
        )
        for row
        in comparison[
            "comparison"
        ]
    ]

    signals = [
        item
        for item
        in measurements
        if (
            item[
                "status"
            ]
            == "supported"
            and item[
                "direction"
            ]
            != "flat"
            and item[
                "signal_eligible"
            ]
        )
    ]

    signals.sort(
        key=_signal_sort_key
    )

    return {
        "signal_type":
            "sector_momentum",

        "as_of":
            comparison[
                "as_of"
            ],

        "window":
            comparison[
                "window"
            ],

        "cohort":
            comparison[
                "cohort"
            ],

        "coverage":
            comparison[
                "coverage"
            ],

        "confidence":
            confidence,

        "current_round_count":
            comparison[
                "current_round_count"
            ],

        "previous_round_count":
            comparison[
                "previous_round_count"
            ],

        "signals":
            signals[
                :limit
            ],

        "measurements":
            measurements,
    }