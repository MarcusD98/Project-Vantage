from collections import (
    Counter,
    defaultdict,
)

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from models.investor import (
    Investor,
)


def _normalize_datetime(
    value,
):
    """
    Normalize datetimes to naive UTC for comparison with the
    existing Vantage SQLite datetime convention.
    """

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


def _normalize_as_of(
    as_of=None,
):
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
        value = int(
            value
        )

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


def _find_investor(
    identifier,
):
    if identifier is None:
        return None

    normalized = (
        str(identifier)
        .strip()
        .casefold()
    )

    if not normalized:
        return None

    for investor in (
        Investor.query.all()
    ):
        if (
            investor.name
            .strip()
            .casefold()
            == normalized
        ):
            return investor

    return None


def _rounds_for_investor(
    investor,
):
    """
    Return unique canonical funding rounds associated with an
    investor.

    Lead rounds are included defensively even though Vantage
    currently also stores lead investors in the general
    participating-investor relationship.
    """

    rounds = {}

    for funding_round in (
        investor.funding_rounds
    ):
        key = (
            funding_round.id
            if funding_round.id
            is not None
            else id(
                funding_round
            )
        )

        rounds[key] = (
            funding_round
        )

    for funding_round in (
        investor.led_funding_rounds
    ):
        key = (
            funding_round.id
            if funding_round.id
            is not None
            else id(
                funding_round
            )
        )

        rounds[key] = (
            funding_round
        )

    return list(
        rounds.values()
    )


def _lead_round_ids(
    investor,
):
    return {
        (
            funding_round.id
            if funding_round.id
            is not None
            else id(
                funding_round
            )
        )
        for funding_round
        in investor.led_funding_rounds
    }


def _round_key(
    funding_round,
):
    return (
        funding_round.id
        if funding_round.id
        is not None
        else id(
            funding_round
        )
    )


def _round_date(
    funding_round,
):
    return _normalize_datetime(
        funding_round.announced_at
    )


def _analysis_rounds(
    rounds,
    as_of,
):
    """
    Keep undated historical observations and dated rounds up to
    the analysis date.

    Future-dated records are excluded.
    """

    result = []

    for funding_round in rounds:
        announced_at = (
            _round_date(
                funding_round
            )
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
        announced_at = (
            _round_date(
                funding_round
            )
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


def _round_volume_by_currency(
    rounds,
):
    """
    Sum the full financing-round amounts in which the investor
    participated.

    This is NOT an estimate of investor capital deployed.
    """

    totals = defaultdict(
        lambda: {
            "amount": 0.0,
            "round_count": 0,
        }
    )

    for funding_round in rounds:
        if (
            funding_round.amount
            is None
        ):
            continue

        currency = (
            funding_round.currency
            or ""
        ).strip().upper()

        if not currency:
            continue

        totals[
            currency
        ][
            "amount"
        ] += float(
            funding_round.amount
        )

        totals[
            currency
        ][
            "round_count"
        ] += 1

    return [
        {
            "currency":
                currency,

            "amount":
                values[
                    "amount"
                ],

            "round_count":
                values[
                    "round_count"
                ],
        }
        for currency, values
        in sorted(
            totals.items()
        )
    ]


def _activity_summary(
    rounds,
    lead_ids,
):
    company_keys = set()

    lead_count = 0

    for funding_round in rounds:
        if (
            _round_key(
                funding_round
            )
            in lead_ids
        ):
            lead_count += 1

        company = (
            funding_round.company
        )

        if company is None:
            continue

        company_key = (
            company.id
            if company.id
            is not None
            else company.name
        )

        company_keys.add(
            company_key
        )

    return {
        "investment_count":
            len(
                rounds
            ),

        "lead_count":
            lead_count,

        "company_count":
            len(
                company_keys
            ),

        "round_volume_by_currency":
            _round_volume_by_currency(
                rounds
            ),
    }


def _counter_items(
    values,
    label_key,
):
    counts = Counter(
        values
    )

    ordered = sorted(
        counts.items(),
        key=lambda item: (
            -item[1],
            item[0].casefold(),
        ),
    )

    return [
        {
            label_key:
                label,

            "count":
                count,
        }
        for label, count
        in ordered
    ]


def _stage_exposure(
    rounds,
):
    stages = []

    for funding_round in rounds:
        stage = (
            funding_round.canonical_round_type
            or funding_round.round_type
            or "Unknown"
        )

        stages.append(
            stage
        )

    return _counter_items(
        stages,
        "stage",
    )


def _sector_exposure(
    rounds,
):
    sectors = []

    for funding_round in rounds:
        company = (
            funding_round.company
        )

        sector = None

        if company is not None:
            sector = (
                company.canonical_sector
                or company.sector
            )

        sectors.append(
            sector
            or "Unknown"
        )

    return _counter_items(
        sectors,
        "sector",
    )


def _geography_exposure(
    rounds,
):
    locations = []

    for funding_round in rounds:
        company = (
            funding_round.company
        )

        location = None

        if company is not None:
            location = (
                company.country
                or company.headquarters
            )

        locations.append(
            location
            or "Unknown"
        )

    return _counter_items(
        locations,
        "location",
    )


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
            if article.id
            is not None
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
        dated[
            :limit
        ]
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
                        funding_round
                        .canonical_round_type
                        or funding_round
                        .round_type
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

    dated_count = sum(
        1
        for funding_round
        in rounds
        if (
            _round_date(
                funding_round
            )
            is not None
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

        "coverage": {
            "observed_rounds":
                len(
                    rounds
                ),

            "dated_rounds":
                dated_count,

            "undated_rounds":
                (
                    len(
                        rounds
                    )
                    - dated_count
                ),
        },

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
    Build one evidence-backed investor activity profile from
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

    return rankings[
        :limit
    ]