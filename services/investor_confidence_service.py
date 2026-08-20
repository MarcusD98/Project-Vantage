from datetime import (
    datetime,
    timezone,
)

from services.investor_intelligence_service import (
    get_investor_profile as get_base_investor_profile,
    get_investor_rankings as get_base_investor_rankings,
)

from services.investor_temporal_coverage_service import (
    get_temporal_corpus_coverage,
)


def _normalize_as_of(as_of=None):
    if as_of is None:
        return (
            datetime.now(
                timezone.utc
            )
            .replace(
                tzinfo=None
            )
        )

    if as_of.tzinfo is not None:
        return (
            as_of.astimezone(
                timezone.utc
            )
            .replace(
                tzinfo=None
            )
        )

    return as_of


def _decorate_profile_with_confidence(
    profile,
):
    if profile is None:
        return None

    investor = profile[
        "investor"
    ]

    window = profile[
        "window"
    ]

    temporal = (
        get_temporal_corpus_coverage(
            investor_name=investor.name,
            current_start=(
                window[
                    "current_start"
                ]
            ),
            current_end=(
                window[
                    "current_end"
                ]
            ),
            previous_start=(
                window[
                    "previous_start"
                ]
            ),
            previous_end=(
                window[
                    "previous_end"
                ]
            ),
        )
    )

    profile[
        "coverage"
    ][
        "temporal_corpus"
    ] = temporal

    activity = profile[
        "signals"
    ][
        "activity"
    ]

    if (
        activity[
            "status"
        ]
        != "supported"
    ):
        confidence = (
            "insufficient"
        )

        confidence_reason = (
            activity.get(
                "reason"
            )
        )

    elif (
        temporal[
            "status"
        ]
        == "complete"
    ):
        confidence = (
            "corpus_supported"
        )

        confidence_reason = None

    else:
        confidence = (
            "observational"
        )

        confidence_reason = (
            temporal.get(
                "reason"
            )
            or (
                "Matched temporal corpus coverage is not "
                "complete."
            )
        )

    activity[
        "confidence"
    ] = confidence

    activity[
        "confidence_reason"
    ] = confidence_reason

    return profile


def get_investor_profile(
    identifier,
    window_days=90,
    as_of=None,
    recent_limit=8,
):
    """
    Return the existing Vantage investor profile decorated with
    temporal corpus confidence.

    The underlying analytical calculations are unchanged.
    """

    normalized_as_of = (
        _normalize_as_of(
            as_of
        )
    )

    profile = (
        get_base_investor_profile(
            identifier=identifier,
            window_days=window_days,
            as_of=normalized_as_of,
            recent_limit=recent_limit,
        )
    )

    return (
        _decorate_profile_with_confidence(
            profile
        )
    )


def get_investor_rankings(
    window_days=90,
    as_of=None,
    limit=20,
):
    """
    Return the existing investor ranking plus one transparent
    confidence label for each activity comparison.

    Confidence values:

        corpus_supported
            Enough observations, plus complete processing of
            discovered first-party Funding Round candidates in
            both comparison windows.

        observational
            Enough graph observations to calculate a trend, but
            matched first-party temporal corpus coverage is
            unavailable or incomplete.

        insufficient
            Not enough observations for the base comparison.
    """

    normalized_as_of = (
        _normalize_as_of(
            as_of
        )
    )

    rankings = (
        get_base_investor_rankings(
            window_days=window_days,
            as_of=normalized_as_of,
            limit=limit,
        )
    )

    for item in rankings:
        profile = (
            get_investor_profile(
                identifier=(
                    item[
                        "investor"
                    ].name
                ),
                window_days=window_days,
                as_of=normalized_as_of,
                recent_limit=1,
            )
        )

        activity = profile[
            "signals"
        ][
            "activity"
        ]

        temporal = profile[
            "coverage"
        ][
            "temporal_corpus"
        ]

        item[
            "trend_confidence"
        ] = activity[
            "confidence"
        ]

        item[
            "trend_confidence_reason"
        ] = activity[
            "confidence_reason"
        ]

        item[
            "temporal_corpus_status"
        ] = temporal[
            "status"
        ]

    return rankings