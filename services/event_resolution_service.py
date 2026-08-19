from datetime import timedelta

from models.funding_round import FundingRound


EVENT_DATE_WINDOW_DAYS = 14


def normalize_round_type(round_type):
    if not round_type:
        return None

    return (
        round_type
        .strip()
        .lower()
        .replace("-", " ")
    )


def amounts_match(
    amount_a,
    amount_b,
):
    if amount_a is None or amount_b is None:
        return False

    if amount_a == 0 or amount_b == 0:
        return False

    difference = abs(
        amount_a - amount_b
    )

    tolerance = max(
        amount_a,
        amount_b,
    ) * 0.02

    return difference <= tolerance


def round_types_compatible(
    round_type_a,
    round_type_b,
):
    normalized_a = normalize_round_type(
        round_type_a
    )

    normalized_b = normalize_round_type(
        round_type_b
    )

    # Missing round type should not prevent an otherwise
    # strong event match.
    if not normalized_a or not normalized_b:
        return True

    return normalized_a == normalized_b


def dates_compatible(
    date_a,
    date_b,
):
    if date_a is None or date_b is None:
        return True

    difference = abs(
        date_a - date_b
    )

    return difference <= timedelta(
        days=EVENT_DATE_WINDOW_DAYS
    )


def find_matching_funding_round(
    company,
    amount,
    currency,
    round_type,
    announced_at,
):
    """
    Find an existing funding event that appears to represent
    the same real-world company financing event.

    V1 deliberately requires:
    - same canonical company
    - same currency
    - approximately same amount
    - compatible round type
    - close announcement dates

    This is intentionally conservative.
    """

    if company is None:
        return None

    if amount is None:
        return None

    if not currency:
        return None

    candidate_rounds = FundingRound.query.filter_by(
        company_id=company.id,
        currency=currency,
    ).all()

    for candidate in candidate_rounds:
        if not amounts_match(
            candidate.amount,
            amount,
        ):
            continue

        if not round_types_compatible(
            candidate.round_type,
            round_type,
        ):
            continue

        if not dates_compatible(
            candidate.announced_at,
            announced_at,
        ):
            continue

        return candidate

    return None