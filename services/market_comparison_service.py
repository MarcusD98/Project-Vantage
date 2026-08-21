from collections import defaultdict
from datetime import datetime, timedelta, timezone

from models.funding_round import FundingRound
from services.entity_resolution_service import resolve_entity_name
from services.investor_temporal_coverage_service import (
    get_temporal_corpus_coverage,
)
from source_registry import SOURCE_REGISTRY


SUPPORTED_MARKET_DIMENSIONS = {
    "sector",
}


def _normalize_datetime(value):
    if value is None:
        return None

    if value.tzinfo is not None:
        return (
            value.astimezone(
                timezone.utc
            )
            .replace(
                tzinfo=None
            )
        )

    return value


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

    return _normalize_datetime(
        as_of
    )


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


def _clean_dimension_value(value):
    if value is None:
        return None

    value = str(
        value
    ).strip()

    if (
        not value
        or value.casefold()
        in {
            "unknown",
            "none",
            "n/a",
            "na",
        }
    ):
        return None

    return value


def _sector_value(
    funding_round,
):
    company = (
        funding_round.company
    )

    if company is None:
        return None

    return _clean_dimension_value(
        company.canonical_sector
        or company.sector
    )


def _window_bounds(
    as_of,
    window_days,
):
    current_start = (
        as_of
        - timedelta(
            days=window_days
        )
    )

    previous_start = (
        current_start
        - timedelta(
            days=window_days
        )
    )

    return {
        "days":
            window_days,

        "current_start":
            current_start,

        "current_end":
            as_of,

        "previous_start":
            previous_start,

        "previous_end":
            current_start,
    }


def _default_investor_names():
    return [
        source[
            "name"
        ]
        for source
        in SOURCE_REGISTRY
        if (
            source.get(
                "enabled",
                False,
            )
            and source.get(
                "type"
            )
            == "investor"
        )
    ]


def _normalize_requested_names(
    investor_names,
):
    if investor_names is None:
        return (
            _default_investor_names()
        )

    if isinstance(
        investor_names,
        str,
    ):
        investor_names = [
            investor_names
        ]

    cleaned = []
    seen = set()

    for value in investor_names:
        if value is None:
            continue

        name = str(
            value
        ).strip()

        if not name:
            continue

        key = (
            name.casefold()
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        cleaned.append(
            name
        )

    if not cleaned:
        raise ValueError(
            "investor_names must contain "
            "at least one investor."
        )

    return cleaned


def _resolve_investor(
    identifier,
):
    resolution = (
        resolve_entity_name(
            identifier,
            "investor",
        )
    )

    if (
        resolution[
            "status"
        ]
        not in {
            "alias",
            "exact",
        }
    ):
        return None

    return resolution[
        "entity"
    ]


def _build_comparable_cohort(
    *,
    investor_names,
    window,
):
    requested = (
        _normalize_requested_names(
            investor_names
        )
    )

    resolved = {}
    coverage_rows = []
    unresolved = []

    for identifier in requested:
        investor = (
            _resolve_investor(
                identifier
            )
        )

        if investor is None:
            unresolved.append(
                identifier
            )
            continue

        if investor.id in resolved:
            continue

        temporal = (
            get_temporal_corpus_coverage(
                investor_name=identifier,
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

        coverage = {
            "investor_id":
                investor.id,

            "investor_name":
                investor.name,

            "requested_identifier":
                identifier,

            "source_name":
                temporal.get(
                    "source_name"
                ),

            "temporal_status":
                temporal[
                    "status"
                ],

            "temporal_reason":
                temporal.get(
                    "reason"
                ),

            "comparable":
                (
                    temporal[
                        "status"
                    ]
                    == "complete"
                ),
        }

        resolved[
            investor.id
        ] = {
            "investor":
                investor,

            "coverage":
                coverage,
        }

        coverage_rows.append(
            coverage
        )

    comparable_ids = {
        investor_id
        for investor_id, item
        in resolved.items()
        if item[
            "coverage"
        ][
            "comparable"
        ]
    }

    comparable_names = sorted(
        [
            item[
                "investor"
            ].name
            for investor_id, item
            in resolved.items()
            if investor_id
            in comparable_ids
        ],
        key=str.casefold,
    )

    resolved_count = len(
        resolved
    )

    comparable_count = len(
        comparable_ids
    )

    return {
        "requested_investors":
            requested,

        "resolved_investor_count":
            resolved_count,

        "comparable_investor_count":
            comparable_count,

        "comparable_ratio":
            (
                comparable_count
                / resolved_count
                if resolved_count
                else 0.0
            ),

        "comparable_investor_ids":
            comparable_ids,

        "comparable_investor_names":
            comparable_names,

        "coverage_by_investor":
            sorted(
                coverage_rows,
                key=lambda item: (
                    item[
                        "investor_name"
                    ].casefold()
                ),
            ),

        "unresolved_investors":
            sorted(
                unresolved,
                key=str.casefold,
            ),
    }


def _round_investor_ids(
    funding_round,
):
    investor_ids = {
        investor.id
        for investor
        in funding_round.investors
        if investor.id
        is not None
    }

    investor_ids.update(
        investor.id
        for investor
        in funding_round.lead_investors
        if investor.id
        is not None
    )

    return investor_ids


def _rounds_between(
    *,
    start,
    end,
    include_end,
):
    query = (
        FundingRound.query
        .filter(
            FundingRound.announced_at
            >= start
        )
    )

    if include_end:
        query = query.filter(
            FundingRound.announced_at
            <= end
        )

    else:
        query = query.filter(
            FundingRound.announced_at
            < end
        )

    return query.all()


def _cohort_rounds(
    rounds,
    comparable_ids,
):
    if not comparable_ids:
        return []

    return [
        funding_round
        for funding_round
        in rounds
        if (
            _round_investor_ids(
                funding_round
            )
            & comparable_ids
        )
    ]


def _dimension_coverage(
    rounds,
    extractor,
):
    total = len(
        rounds
    )

    known = sum(
        1
        for funding_round
        in rounds
        if extractor(
            funding_round
        )
        is not None
    )

    ratio = (
        known / total
        if total
        else 0.0
    )

    return {
        "known":
            known,

        "total":
            total,

        "missing":
            max(
                total - known,
                0,
            ),

        "ratio":
            ratio,

        "percent":
            ratio * 100,
    }


def _sector_aggregation(
    rounds,
    comparable_ids,
):
    buckets = defaultdict(
        lambda: {
            "event_ids":
                set(),

            "company_ids":
                set(),

            "investor_ids":
                set(),

            "investor_names":
                set(),

            "lead_event_ids":
                set(),
        }
    )

    for funding_round in rounds:
        sector = (
            _sector_value(
                funding_round
            )
        )

        if sector is None:
            continue

        bucket = (
            buckets[
                sector
            ]
        )

        if funding_round.id is not None:
            bucket[
                "event_ids"
            ].add(
                funding_round.id
            )

        company = (
            funding_round.company
        )

        if (
            company is not None
            and company.id
            is not None
        ):
            bucket[
                "company_ids"
            ].add(
                company.id
            )

        for investor in (
            funding_round.investors
        ):
            if (
                investor.id
                not in comparable_ids
            ):
                continue

            bucket[
                "investor_ids"
            ].add(
                investor.id
            )

            bucket[
                "investor_names"
            ].add(
                investor.name
            )

        lead_in_cohort = False

        for investor in (
            funding_round.lead_investors
        ):
            if (
                investor.id
                not in comparable_ids
            ):
                continue

            bucket[
                "investor_ids"
            ].add(
                investor.id
            )

            bucket[
                "investor_names"
            ].add(
                investor.name
            )

            lead_in_cohort = True

        if (
            lead_in_cohort
            and funding_round.id
            is not None
        ):
            bucket[
                "lead_event_ids"
            ].add(
                funding_round.id
            )

    return {
        sector: {
            "event_count":
                len(
                    values[
                        "event_ids"
                    ]
                ),

            "company_count":
                len(
                    values[
                        "company_ids"
                    ]
                ),

            "investor_count":
                len(
                    values[
                        "investor_ids"
                    ]
                ),

            "investor_names":
                sorted(
                    values[
                        "investor_names"
                    ],
                    key=str.casefold,
                ),

            "lead_event_count":
                len(
                    values[
                        "lead_event_ids"
                    ]
                ),

            "event_ids":
                sorted(
                    values[
                        "event_ids"
                    ]
                ),
        }
        for sector, values
        in buckets.items()
    }


def _empty_aggregate():
    return {
        "event_count": 0,
        "company_count": 0,
        "investor_count": 0,
        "investor_names": [],
        "lead_event_count": 0,
        "event_ids": [],
    }


def _comparison_rows(
    current,
    previous,
):
    sectors = sorted(
        (
            set(
                current
            )
            | set(
                previous
            )
        ),
        key=str.casefold,
    )

    rows = []

    for sector in sectors:
        current_values = (
            current.get(
                sector,
                _empty_aggregate(),
            )
        )

        previous_values = (
            previous.get(
                sector,
                _empty_aggregate(),
            )
        )

        current_count = (
            current_values[
                "event_count"
            ]
        )

        previous_count = (
            previous_values[
                "event_count"
            ]
        )

        delta = (
            current_count
            - previous_count
        )

        rows.append(
            {
                "dimension":
                    "sector",

                "value":
                    sector,

                "current_event_count":
                    current_count,

                "previous_event_count":
                    previous_count,

                "delta":
                    delta,

                "change_pct":
                    (
                        delta
                        / previous_count
                        * 100
                        if previous_count
                        else None
                    ),

                "current_company_count":
                    current_values[
                        "company_count"
                    ],

                "previous_company_count":
                    previous_values[
                        "company_count"
                    ],

                "current_investor_count":
                    current_values[
                        "investor_count"
                    ],

                "previous_investor_count":
                    previous_values[
                        "investor_count"
                    ],

                "current_lead_event_count":
                    current_values[
                        "lead_event_count"
                    ],

                "previous_lead_event_count":
                    previous_values[
                        "lead_event_count"
                    ],

                "contributing_investors":
                    sorted(
                        (
                            set(
                                current_values[
                                    "investor_names"
                                ]
                            )
                            | set(
                                previous_values[
                                    "investor_names"
                                ]
                            )
                        ),
                        key=str.casefold,
                    ),

                "current_event_ids":
                    current_values[
                        "event_ids"
                    ],

                "previous_event_ids":
                    previous_values[
                        "event_ids"
                    ],
            }
        )

    return rows


def compare_market_activity(
    *,
    dimension="sector",
    window_days=180,
    as_of=None,
    investor_names=None,
):
    """
    Compare canonical funding activity across two equal windows.

    Only investors whose discovered first-party corpus is complete
    across both windows are included in the comparable cohort.

    V1 supports the sector dimension.

    Signal interpretation is deliberately left to
    market_signal_service.
    """

    if (
        dimension
        not in SUPPORTED_MARKET_DIMENSIONS
    ):
        raise ValueError(
            "Unsupported market comparison dimension: "
            f"{dimension}"
        )

    window_days = (
        _positive_integer(
            window_days,
            "window_days",
        )
    )

    as_of = (
        _normalize_as_of(
            as_of
        )
    )

    window = (
        _window_bounds(
            as_of,
            window_days,
        )
    )

    cohort = (
        _build_comparable_cohort(
            investor_names=(
                investor_names
            ),
            window=window,
        )
    )

    comparable_ids = (
        cohort[
            "comparable_investor_ids"
        ]
    )

    current_rounds = (
        _cohort_rounds(
            _rounds_between(
                start=(
                    window[
                        "current_start"
                    ]
                ),
                end=(
                    window[
                        "current_end"
                    ]
                ),
                include_end=True,
            ),
            comparable_ids,
        )
    )

    previous_rounds = (
        _cohort_rounds(
            _rounds_between(
                start=(
                    window[
                        "previous_start"
                    ]
                ),
                end=(
                    window[
                        "previous_end"
                    ]
                ),
                include_end=False,
            ),
            comparable_ids,
        )
    )

    current_coverage = (
        _dimension_coverage(
            current_rounds,
            _sector_value,
        )
    )

    previous_coverage = (
        _dimension_coverage(
            previous_rounds,
            _sector_value,
        )
    )

    combined_coverage = (
        _dimension_coverage(
            (
                current_rounds
                + previous_rounds
            ),
            _sector_value,
        )
    )

    current = (
        _sector_aggregation(
            current_rounds,
            comparable_ids,
        )
    )

    previous = (
        _sector_aggregation(
            previous_rounds,
            comparable_ids,
        )
    )

    public_cohort = {
        key: value
        for key, value
        in cohort.items()
        if key
        != "comparable_investor_ids"
    }

    return {
        "dimension":
            dimension,

        "as_of":
            as_of,

        "window":
            window,

        "cohort":
            public_cohort,

        "coverage": {
            "current":
                current_coverage,

            "previous":
                previous_coverage,

            "combined":
                combined_coverage,
        },

        "current_round_count":
            len(
                current_rounds
            ),

        "previous_round_count":
            len(
                previous_rounds
            ),

        "comparison":
            _comparison_rows(
                current,
                previous,
            ),
    }