from itertools import combinations

from models.funding_round import (
    FundingRound,
)

from services.event_resolution_service import (
    normalize_currency,
    normalize_round_type,
)


CROSS_CURRENCY_WINDOW_DAYS = 3
MIN_INVESTOR_OVERLAP = 2


def _stage(funding_round):
    return normalize_round_type(
        funding_round.canonical_round_type
        or funding_round.round_type
    )


def _investor_names(
    funding_round,
):
    return {
        investor.name
        for investor
        in funding_round.investors
        if investor.name
    }


def _lead_names(
    funding_round,
):
    return {
        investor.name
        for investor
        in funding_round.lead_investors
        if investor.name
    }


def cross_currency_duplicate_candidate(
    funding_round_a,
    funding_round_b,
):
    """
    Return diagnostic evidence when two canonical rounds may
    represent the same real-world financing reported in
    different currencies.

    This function is deliberately read-only.

    It does not:
    - perform FX conversion
    - merge events
    - mutate canonical data

    Candidate requirements:
    - same canonical company
    - both dates known and within three days
    - same known financing stage
    - both currencies known and different
    - shared lead investor OR at least two shared investors
    """

    if (
        funding_round_a is None
        or funding_round_b is None
    ):
        return None

    if (
        funding_round_a.id is not None
        and funding_round_b.id is not None
        and funding_round_a.id
        == funding_round_b.id
    ):
        return None

    if (
        funding_round_a.company_id is None
        or funding_round_b.company_id is None
        or funding_round_a.company_id
        != funding_round_b.company_id
    ):
        return None

    if (
        funding_round_a.announced_at is None
        or funding_round_b.announced_at is None
    ):
        return None

    days_apart = abs(
        (
            funding_round_a.announced_at
            - funding_round_b.announced_at
        ).total_seconds()
    ) / 86400

    if (
        days_apart
        > CROSS_CURRENCY_WINDOW_DAYS
    ):
        return None

    stage_a = _stage(
        funding_round_a
    )

    stage_b = _stage(
        funding_round_b
    )

    if (
        not stage_a
        or not stage_b
        or stage_a != stage_b
    ):
        return None

    currency_a = normalize_currency(
        funding_round_a.currency
    )

    currency_b = normalize_currency(
        funding_round_b.currency
    )

    if (
        not currency_a
        or not currency_b
        or currency_a == currency_b
    ):
        return None

    investor_overlap = (
        _investor_names(
            funding_round_a
        )
        & _investor_names(
            funding_round_b
        )
    )

    lead_overlap = (
        _lead_names(
            funding_round_a
        )
        & _lead_names(
            funding_round_b
        )
    )

    if (
        not lead_overlap
        and len(
            investor_overlap
        )
        < MIN_INVESTOR_OVERLAP
    ):
        return None

    return {
        "round_a_id":
            funding_round_a.id,

        "round_b_id":
            funding_round_b.id,

        "company_id":
            funding_round_a.company_id,

        "company_name":
            (
                funding_round_a.company.name
                if funding_round_a.company
                is not None
                else None
            ),

        "days_apart":
            days_apart,

        "stage":
            stage_a,

        "currency_a":
            currency_a,

        "currency_b":
            currency_b,

        "amount_a":
            funding_round_a.amount,

        "amount_b":
            funding_round_b.amount,

        "investor_overlap":
            sorted(
                investor_overlap,
                key=str.casefold,
            ),

        "lead_overlap":
            sorted(
                lead_overlap,
                key=str.casefold,
            ),
    }


def get_cross_currency_duplicate_candidates():
    """
    Scan the canonical funding graph for conservative
    cross-currency duplicate candidates.

    Read-only diagnostic operation.
    """

    rounds = (
        FundingRound.query.all()
    )

    by_company = {}

    for funding_round in rounds:
        by_company.setdefault(
            funding_round.company_id,
            [],
        ).append(
            funding_round
        )

    candidates = []

    for company_rounds in (
        by_company.values()
    ):
        for first, second in combinations(
            company_rounds,
            2,
        ):
            candidate = (
                cross_currency_duplicate_candidate(
                    first,
                    second,
                )
            )

            if candidate is not None:
                candidates.append(
                    candidate
                )

    candidates.sort(
        key=lambda item: (
            (
                item[
                    "company_name"
                ]
                or ""
            ).casefold(),
            item[
                "round_a_id"
            ]
            or 0,
            item[
                "round_b_id"
            ]
            or 0,
        )
    )

    return candidates
