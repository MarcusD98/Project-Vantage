from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from models.investor import Investor

from services.entity_resolution_service import (
    resolve_entity_name,
)


COVERAGE_HIGH_THRESHOLD = 0.80
COVERAGE_MEDIUM_THRESHOLD = 0.50

MIN_DIMENSION_SIGNAL_OBSERVATIONS = 3
MIN_DIMENSION_SIGNAL_COVERAGE = 0.60

MIN_ACTIVITY_COMPARISON_OBSERVATIONS = 4
MIN_ACTIVITY_PREVIOUS_OBSERVATIONS = 1

LEADING_DIMENSION_SHARE = 0.40


def _normalize_datetime(value):
    """
    Normalize datetimes to naive UTC for comparison with the
    existing Vantage SQLite datetime convention.
    """

    if value is None:
        return None

    if value.tzinfo is not None:
        return (
            value.astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

    return value


def _normalize_as_of(as_of=None):
    if as_of is None:
        return (
            datetime.now(timezone.utc)
            .replace(tzinfo=None)
        )

    return _normalize_datetime(as_of)


def _positive_integer(value, name):
    try:
        value = int(value)

    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{name} must be an integer."
        ) from exc

    if value <= 0:
        raise ValueError(
            f"{name} must be greater than zero."
        )

    return value


def _clean_dimension_value(value):
    """
    Normalize analytical dimension values.

    Missing / placeholder values should not count as known
    coverage.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    if value.casefold() in {
        "unknown",
        "none",
        "n/a",
        "na",
    }:
        return None

    return value


def _find_investor(identifier):
    """
    Resolve an investor using the canonical entity layer.

    This means investor intelligence automatically respects
    durable aliases such as:

        Index -> Index Ventures
    """

    if identifier is None:
        return None

    identifier = str(identifier).strip()

    if not identifier:
        return None

    resolution = resolve_entity_name(
        identifier,
        "investor",
    )

    if resolution["status"] in {
        "alias",
        "exact",
    }:
        return resolution["entity"]

    return None


def _round_key(funding_round):
    return (
        funding_round.id
        if funding_round.id is not None
        else id(funding_round)
    )


def _round_date(funding_round):
    return _normalize_datetime(
        funding_round.announced_at
    )


def _stage_value(funding_round):
    return _clean_dimension_value(
        funding_round.canonical_round_type
        or funding_round.round_type
    )


def _sector_value(funding_round):
    company = funding_round.company

    if company is None:
        return None

    return _clean_dimension_value(
        company.canonical_sector
        or company.sector
    )


def _geography_value(funding_round):
    """
    Country is the canonical geography dimension for V1.

    We deliberately do not fall back to free-form headquarters
    because that would mix countries, cities and arbitrary
    location strings in the same analytical dimension.
    """

    company = funding_round.company

    if company is None:
        return None

    return _clean_dimension_value(
        company.country
    )


def _rounds_for_investor(investor):
    """
    Return unique canonical funding rounds associated with an
    investor.

    Lead rounds are included defensively even though Vantage
    also stores lead investors in the general investor
    relationship.
    """

    rounds = {}

    for funding_round in investor.funding_rounds:
        rounds[
            _round_key(funding_round)
        ] = funding_round

    for funding_round in investor.led_funding_rounds:
        rounds[
            _round_key(funding_round)
        ] = funding_round

    return list(
        rounds.values()
    )


def _lead_round_ids(investor):
    return {
        _round_key(funding_round)
        for funding_round
        in investor.led_funding_rounds
    }


def _analysis_rounds(rounds, as_of):
    """
    Preserve undated historical observations and dated rounds
    up to the analysis date.

    Future-dated records are excluded.
    """

    result = []

    for funding_round in rounds:
        announced_at = _round_date(
            funding_round
        )

        if (
            announced_at is not None
            and announced_at > as_of
        ):
            continue

        result.append(
            funding_round
        )

    return result


def _rounds_between(
    rounds,
    start,
    end,
    include_end=False,
):
    selected = []

    for funding_round in rounds:
        announced_at = _round_date(
            funding_round
        )

        if announced_at is None:
            continue

        if announced_at < start:
            continue

        if include_end:
            if announced_at > end:
                continue

        else:
            if announced_at >= end:
                continue

        selected.append(
            funding_round
        )

    return selected


def _round_volume_by_currency(rounds):
    """
    Sum complete financing-round values in which the investor
    participated.

    This is NOT investor capital deployed.
    """

    totals = defaultdict(
        lambda: {
            "amount": 0.0,
            "round_count": 0,
        }
    )

    for funding_round in rounds:
        if funding_round.amount is None:
            continue

        currency = (
            funding_round.currency
            or ""
        ).strip().upper()

        if not currency:
            continue

        totals[currency][
            "amount"
        ] += float(
            funding_round.amount
        )

        totals[currency][
            "round_count"
        ] += 1

    return [
        {
            "currency": currency,
            "amount": values["amount"],
            "round_count": values[
                "round_count"
            ],
        }
        for currency, values
        in sorted(totals.items())
    ]


def _activity_summary(
    rounds,
    lead_ids,
):
    company_keys = set()
    lead_count = 0

    for funding_round in rounds:
        if (
            _round_key(funding_round)
            in lead_ids
        ):
            lead_count += 1

        company = funding_round.company

        if company is None:
            continue

        company_key = (
            company.id
            if company.id is not None
            else company.name
        )

        company_keys.add(
            company_key
        )

    return {
        "investment_count":
            len(rounds),

        "lead_count":
            lead_count,

        "company_count":
            len(company_keys),

        "round_volume_by_currency":
            _round_volume_by_currency(
                rounds
            ),
    }


def _counter_items(
    values,
    label_key,
):
    counts = Counter(values)

    ordered = sorted(
        counts.items(),
        key=lambda item: (
            -item[1],
            item[0].casefold(),
        ),
    )

    return [
        {
            label_key: label,
            "count": count,
        }
        for label, count
        in ordered
    ]


def _stage_exposure(rounds):
    values = []

    for funding_round in rounds:
        value = _stage_value(
            funding_round
        )

        values.append(
            value or "Unknown"
        )

    return _counter_items(
        values,
        "stage",
    )


def _sector_exposure(rounds):
    values = []

    for funding_round in rounds:
        value = _sector_value(
            funding_round
        )

        values.append(
            value or "Unknown"
        )

    return _counter_items(
        values,
        "sector",
    )


def _geography_exposure(rounds):
    values = []

    for funding_round in rounds:
        value = _geography_value(
            funding_round
        )

        values.append(
            value or "Unknown"
        )

    return _counter_items(
        values,
        "location",
    )


def _coverage_label(
    known,
    total,
):
    if total <= 0:
        return "insufficient"

    ratio = known / total

    if ratio >= COVERAGE_HIGH_THRESHOLD:
        return "high"

    if ratio >= COVERAGE_MEDIUM_THRESHOLD:
        return "medium"

    if known > 0:
        return "low"

    return "insufficient"


def _coverage_metric(
    known,
    total,
):
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

        "label":
            _coverage_label(
                known,
                total,
            ),
    }


def _build_dimension_coverage(
    rounds,
    extractor,
):
    known = sum(
        1
        for funding_round
        in rounds
        if extractor(
            funding_round
        )
        is not None
    )

    return _coverage_metric(
        known=known,
        total=len(rounds),
    )


def _build_comparison_history(
    current_rounds,
    previous_rounds,
):
    current_count = len(
        current_rounds
    )

    previous_count = len(
        previous_rounds
    )

    combined = (
        current_count
        + previous_count
    )

    sufficient = (
        previous_count
        >= MIN_ACTIVITY_PREVIOUS_OBSERVATIONS
        and combined
        >= MIN_ACTIVITY_COMPARISON_OBSERVATIONS
    )

    return {
        "current_observations":
            current_count,

        "previous_observations":
            previous_count,

        "combined_observations":
            combined,

        "status":
            (
                "sufficient"
                if sufficient
                else "insufficient"
            ),
    }


def _build_coverage(
    rounds,
    current_rounds,
    previous_rounds,
):
    total = len(rounds)

    dated_count = sum(
        1
        for funding_round
        in rounds
        if _round_date(
            funding_round
        )
        is not None
    )

    return {
        # Backwards-compatible fields.
        "observed_rounds":
            total,

        "dated_rounds":
            dated_count,

        "undated_rounds":
            total - dated_count,

        # Dimension-level coverage.
        "date":
            _coverage_metric(
                known=dated_count,
                total=total,
            ),

        "stage":
            _build_dimension_coverage(
                rounds,
                _stage_value,
            ),

        "sector":
            _build_dimension_coverage(
                rounds,
                _sector_value,
            ),

        "geography":
            _build_dimension_coverage(
                rounds,
                _geography_value,
            ),

        "comparison_history":
            _build_comparison_history(
                current_rounds,
                previous_rounds,
            ),
    }


def _build_activity_signal(
    current,
    previous,
    comparison_history,
):
    if (
        comparison_history["status"]
        != "sufficient"
    ):
        return {
            "status":
                "insufficient",

            "direction":
                None,

            "current":
                current[
                    "investment_count"
                ],

            "previous":
                previous[
                    "investment_count"
                ],

            "delta":
                (
                    current[
                        "investment_count"
                    ]
                    - previous[
                        "investment_count"
                    ]
                ),

            "change_pct":
                None,

            "reason": (
                "Need at least "
                f"{MIN_ACTIVITY_COMPARISON_OBSERVATIONS} "
                "observed rounds across the two "
                "comparison windows, including at least "
                f"{MIN_ACTIVITY_PREVIOUS_OBSERVATIONS} "
                "in the previous window."
            ),
        }

    current_count = (
        current[
            "investment_count"
        ]
    )

    previous_count = (
        previous[
            "investment_count"
        ]
    )

    delta = (
        current_count
        - previous_count
    )

    if delta > 0:
        direction = "up"

    elif delta < 0:
        direction = "down"

    else:
        direction = "flat"

    change_pct = (
        delta
        / previous_count
        * 100
    )

    return {
        "status":
            "supported",

        "direction":
            direction,

        "current":
            current_count,

        "previous":
            previous_count,

        "delta":
            delta,

        "change_pct":
            change_pct,

        "reason":
            None,
    }


def _build_dimension_signal(
    rounds,
    extractor,
    coverage,
):
    if (
        coverage["known"]
        < MIN_DIMENSION_SIGNAL_OBSERVATIONS
    ):
        return {
            "status":
                "insufficient",

            "pattern":
                None,

            "leaders":
                [],

            "leader_count":
                0,

            "known_count":
                coverage["known"],

            "share":
                None,

            "reason": (
                "Need at least "
                f"{MIN_DIMENSION_SIGNAL_OBSERVATIONS} "
                "known observations."
            ),
        }

    if (
        coverage["ratio"]
        < MIN_DIMENSION_SIGNAL_COVERAGE
    ):
        return {
            "status":
                "insufficient",

            "pattern":
                None,

            "leaders":
                [],

            "leader_count":
                0,

            "known_count":
                coverage["known"],

            "share":
                None,

            "reason": (
                "Known-field coverage is below "
                f"{MIN_DIMENSION_SIGNAL_COVERAGE:.0%}."
            ),
        }

    values = [
        extractor(
            funding_round
        )
        for funding_round
        in rounds
    ]

    values = [
        value
        for value
        in values
        if value is not None
    ]

    counts = Counter(
        values
    )

    if not counts:
        return {
            "status":
                "insufficient",

            "pattern":
                None,

            "leaders":
                [],

            "leader_count":
                0,

            "known_count":
                0,

            "share":
                None,

            "reason":
                "No known observations.",
        }

    leader_count = max(
        counts.values()
    )

    leaders = sorted(
        [
            label
            for label, count
            in counts.items()
            if count == leader_count
        ],
        key=str.casefold,
    )

    share = (
        leader_count
        / len(values)
    )

    pattern = (
        "leading"
        if share
        >= LEADING_DIMENSION_SHARE
        else "mixed"
    )

    return {
        "status":
            "supported",

        "pattern":
            pattern,

        "leaders":
            leaders,

        "leader_count":
            leader_count,

        "known_count":
            len(values),

        "share":
            share,

        "reason":
            None,
    }


def _build_signals(
    rounds,
    current,
    previous,
    coverage,
):
    return {
        "activity":
            _build_activity_signal(
                current=current,
                previous=previous,
                comparison_history=(
                    coverage[
                        "comparison_history"
                    ]
                ),
            ),

        "stage":
            _build_dimension_signal(
                rounds=rounds,
                extractor=_stage_value,
                coverage=coverage[
                    "stage"
                ],
            ),

        "sector":
            _build_dimension_signal(
                rounds=rounds,
                extractor=_sector_value,
                coverage=coverage[
                    "sector"
                ],
            ),

        "geography":
            _build_dimension_signal(
                rounds=rounds,
                extractor=_geography_value,
                coverage=coverage[
                    "geography"
                ],
            ),
    }


def _co_investors(
    investor,
    rounds,
):
    counts = Counter()

    for funding_round in rounds:
        for other in (
            funding_round.investors
        ):
            if (
                other.id
                == investor.id
            ):
                continue

            counts[
                other.name
            ] += 1

    ordered = sorted(
        counts.items(),
        key=lambda item: (
            -item[1],
            item[0].casefold(),
        ),
    )

    return [
        {
            "investor":
                name,

            "shared_rounds":
                count,
        }
        for name, count
        in ordered
    ]


def _evidence_sources(
    funding_round,
):
    articles = []

    if funding_round.article is not None:
        articles.append(
            funding_round.article
        )

    articles.extend(
        funding_round.articles
    )

    seen = set()
    sources = set()

    for article in articles:
        key = (
            article.id
            if article.id is not None
            else article.url
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        if article.source:
            sources.add(
                article.source
            )

    return sorted(
        sources,
        key=str.casefold,
    )


def _recent_investments(
    rounds,
    lead_ids,
    as_of,
    limit,
):
    dated = [
        funding_round
        for funding_round
        in rounds
        if (
            _round_date(
                funding_round
            )
            is not None
            and _round_date(
                funding_round
            )
            <= as_of
        )
    ]

    dated.sort(
        key=lambda funding_round:
            _round_date(
                funding_round
            ),
        reverse=True,
    )

    result = []

    for funding_round in (
        dated[:limit]
    ):
        company = (
            funding_round.company
        )

        sources = (
            _evidence_sources(
                funding_round
            )
        )

        result.append(
            {
                "funding_round_id":
                    funding_round.id,

                "company":
                    (
                        company.name
                        if company
                        is not None
                        else "Unknown"
                    ),

                "announced_at":
                    _round_date(
                        funding_round
                    ),

                "stage":
                    (
                        _stage_value(
                            funding_round
                        )
                        or "Unknown"
                    ),

                "amount":
                    funding_round.amount,

                "currency":
                    funding_round.currency,

                "is_lead":
                    (
                        _round_key(
                            funding_round
                        )
                        in lead_ids
                    ),

                "evidence_count":
                    len(
                        sources
                    ),

                "evidence_sources":
                    sources,
            }
        )

    return result


def _build_profile(
    investor,
    window_days,
    as_of,
    recent_limit,
):
    rounds = (
        _rounds_for_investor(
            investor
        )
    )

    rounds = (
        _analysis_rounds(
            rounds,
            as_of,
        )
    )

    lead_ids = (
        _lead_round_ids(
            investor
        )
    )

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

    current_rounds = (
        _rounds_between(
            rounds,
            start=current_start,
            end=as_of,
            include_end=True,
        )
    )

    previous_rounds = (
        _rounds_between(
            rounds,
            start=previous_start,
            end=current_start,
            include_end=False,
        )
    )

    current = (
        _activity_summary(
            current_rounds,
            lead_ids,
        )
    )

    previous = (
        _activity_summary(
            previous_rounds,
            lead_ids,
        )
    )

    all_time = (
        _activity_summary(
            rounds,
            lead_ids,
        )
    )

    investment_delta = (
        current[
            "investment_count"
        ]
        - previous[
            "investment_count"
        ]
    )

    lead_delta = (
        current[
            "lead_count"
        ]
        - previous[
            "lead_count"
        ]
    )

    if investment_delta > 0:
        direction = "up"

    elif investment_delta < 0:
        direction = "down"

    else:
        direction = "flat"

    if (
        previous[
            "investment_count"
        ]
        > 0
    ):
        investment_change_pct = (
            investment_delta
            / previous[
                "investment_count"
            ]
            * 100
        )

    else:
        investment_change_pct = None

    coverage = (
        _build_coverage(
            rounds=rounds,
            current_rounds=current_rounds,
            previous_rounds=(
                previous_rounds
            ),
        )
    )

    signals = (
        _build_signals(
            rounds=rounds,
            current=current,
            previous=previous,
            coverage=coverage,
        )
    )

    return {
        "investor":
            investor,

        "as_of":
            as_of,

        "window": {
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
        },

        "coverage":
            coverage,

        "signals":
            signals,

        "all_time":
            all_time,

        "current_window":
            current,

        "previous_window":
            previous,

        "change": {
            "investment_delta":
                investment_delta,

            "lead_delta":
                lead_delta,

            "investment_change_pct":
                investment_change_pct,

            "direction":
                direction,
        },

        "stage_exposure": {
            "all_time":
                _stage_exposure(
                    rounds
                ),

            "current_window":
                _stage_exposure(
                    current_rounds
                ),
        },

        "sector_exposure": {
            "all_time":
                _sector_exposure(
                    rounds
                ),

            "current_window":
                _sector_exposure(
                    current_rounds
                ),
        },

        "geography_exposure": {
            "all_time":
                _geography_exposure(
                    rounds
                ),

            "current_window":
                _geography_exposure(
                    current_rounds
                ),
        },

        "co_investors":
            _co_investors(
                investor,
                rounds,
            ),

        "recent_investments":
            _recent_investments(
                rounds,
                lead_ids,
                as_of,
                recent_limit,
            ),
    }


def get_investor_profile(
    identifier,
    window_days=90,
    as_of=None,
    recent_limit=8,
):
    """
    Build an evidence-backed investor activity profile from
    canonical Vantage funding events.
    """

    window_days = (
        _positive_integer(
            window_days,
            "window_days",
        )
    )

    recent_limit = (
        _positive_integer(
            recent_limit,
            "recent_limit",
        )
    )

    as_of = (
        _normalize_as_of(
            as_of
        )
    )

    investor = (
        _find_investor(
            identifier
        )
    )

    if investor is None:
        return None

    return _build_profile(
        investor=investor,
        window_days=window_days,
        as_of=as_of,
        recent_limit=recent_limit,
    )


def get_investor_rankings(
    window_days=90,
    as_of=None,
    limit=20,
):
    """
    Rank observed investors by current-window investment
    activity.

    Rankings are evidence-corpus observations, not claims of
    complete market activity.
    """

    window_days = (
        _positive_integer(
            window_days,
            "window_days",
        )
    )

    limit = (
        _positive_integer(
            limit,
            "limit",
        )
    )

    as_of = (
        _normalize_as_of(
            as_of
        )
    )

    rankings = []

    for investor in (
        Investor.query.all()
    ):
        profile = (
            _build_profile(
                investor=investor,
                window_days=window_days,
                as_of=as_of,
                recent_limit=1,
            )
        )

        if (
            profile[
                "all_time"
            ][
                "investment_count"
            ]
            == 0
        ):
            continue

        rankings.append(
            {
                "investor":
                    investor,

                "current_investments":
                    profile[
                        "current_window"
                    ][
                        "investment_count"
                    ],

                "previous_investments":
                    profile[
                        "previous_window"
                    ][
                        "investment_count"
                    ],

                "investment_delta":
                    profile[
                        "change"
                    ][
                        "investment_delta"
                    ],

                "current_leads":
                    profile[
                        "current_window"
                    ][
                        "lead_count"
                    ],

                "all_time_investments":
                    profile[
                        "all_time"
                    ][
                        "investment_count"
                    ],

                "trend_status":
                    profile[
                        "signals"
                    ][
                        "activity"
                    ][
                        "status"
                    ],
            }
        )

    rankings.sort(
        key=lambda item: (
            -item[
                "current_investments"
            ],
            -item[
                "current_leads"
            ],
            -item[
                "previous_investments"
            ],
            -item[
                "all_time_investments"
            ],
            item[
                "investor"
            ]
            .name
            .casefold(),
        )
    )

    return rankings[:limit]