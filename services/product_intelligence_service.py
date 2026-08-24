from datetime import (
    datetime,
    timezone,
)

from services.investor_confidence_service import (
    get_investor_rankings,
)

from services.market_signal_service import (
    get_sector_momentum,
)


CONFIDENCE_PRIORITY = {
    "corpus_supported": 0,
    "observational": 1,
}


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


def select_investor_changes(
    rankings,
    limit=6,
):
    """
    Select the strongest user-facing investor activity changes.

    This function does not calculate a new signal.

    It promotes existing supported Vantage activity comparisons
    into a product-facing ordering:

        confidence
        → magnitude of observed change
        → current observed activity
        → investor name
    """

    limit = _positive_integer(
        limit,
        "limit",
    )

    changes = []

    for item in rankings:
        if (
            item.get(
                "trend_status"
            )
            != "supported"
        ):
            continue

        confidence = item.get(
            "trend_confidence"
        )

        if (
            confidence
            not in CONFIDENCE_PRIORITY
        ):
            continue

        delta = item.get(
            "investment_delta",
            0,
        )

        if delta == 0:
            continue

        changes.append(
            item
        )

    changes.sort(
        key=lambda item: (
            CONFIDENCE_PRIORITY[
                item[
                    "trend_confidence"
                ]
            ],
            -abs(
                item[
                    "investment_delta"
                ]
            ),
            -item[
                "current_investments"
            ],
            item[
                "investor"
            ]
            .name
            .casefold(),
        )
    )

    return changes[:limit]


def get_product_intelligence_summary(
    *,
    as_of=None,
    investor_window_days=90,
    market_window_days=180,
    investor_limit=6,
    ranking_pool=30,
    sector_limit=5,
):
    """
    Compose existing Vantage intelligence into a product-facing
    summary.

    No new behavioral or market signal is calculated here.
    """

    investor_window_days = (
        _positive_integer(
            investor_window_days,
            "investor_window_days",
        )
    )

    market_window_days = (
        _positive_integer(
            market_window_days,
            "market_window_days",
        )
    )

    investor_limit = (
        _positive_integer(
            investor_limit,
            "investor_limit",
        )
    )

    ranking_pool = (
        _positive_integer(
            ranking_pool,
            "ranking_pool",
        )
    )

    sector_limit = (
        _positive_integer(
            sector_limit,
            "sector_limit",
        )
    )

    normalized_as_of = (
        _normalize_as_of(
            as_of
        )
    )

    investor_rankings = (
        get_investor_rankings(
            window_days=(
                investor_window_days
            ),
            as_of=normalized_as_of,
            limit=ranking_pool,
        )
    )

    investor_changes = (
        select_investor_changes(
            investor_rankings,
            limit=investor_limit,
        )
    )

    sector_momentum = (
        get_sector_momentum(
            window_days=(
                market_window_days
            ),
            as_of=normalized_as_of,
            limit=sector_limit,
        )
    )

    return {
        "as_of":
            normalized_as_of,

        "investor_window_days":
            investor_window_days,

        "market_window_days":
            market_window_days,

        "investor_changes":
            investor_changes,

        "sector_momentum":
            sector_momentum,
    }
