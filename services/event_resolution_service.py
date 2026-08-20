from datetime import timedelta

from models.funding_round import FundingRound


EVENT_DATE_WINDOW_DAYS = 14
AMOUNT_TOLERANCE_RATIO = 0.02


def normalize_round_type(round_type):
    if not round_type:
        return None

    return (
        round_type
        .strip()
        .lower()
        .replace("-", " ")
    )


def normalize_currency(currency):
    if not currency:
        return None

    return currency.strip().upper()


def amounts_match(
    amount_a,
    amount_b,
):
    """
    Return True when two funding amounts are close enough to
    plausibly represent the same reported financing event.
    """

    if amount_a is None or amount_b is None:
        return False

    if amount_a <= 0 or amount_b <= 0:
        return False

    difference = abs(
        amount_a - amount_b
    )

    tolerance = max(
        amount_a,
        amount_b,
    ) * AMOUNT_TOLERANCE_RATIO

    return difference <= tolerance


def currencies_match(
    currency_a,
    currency_b,
):
    """
    Require both events to have the same known currency.

    We deliberately do not attempt FX conversion in event
    resolution v1 because that could create false merges.
    """

    normalized_a = normalize_currency(
        currency_a
    )

    normalized_b = normalize_currency(
        currency_b
    )

    if not normalized_a or not normalized_b:
        return False

    return normalized_a == normalized_b


def round_types_compatible(
    round_type_a,
    round_type_b,
):
    """
    Determine whether two raw funding-stage descriptions are
    compatible.

    Missing round type does not invalidate an otherwise strong
    match because many funding articles omit the stage.
    """

    normalized_a = normalize_round_type(
        round_type_a
    )

    normalized_b = normalize_round_type(
        round_type_b
    )

    if not normalized_a or not normalized_b:
        return True

    return normalized_a == normalized_b


def dates_compatible(
    date_a,
    date_b,
):
    """
    Funding reports within the configured time window may
    represent the same underlying event.

    Missing dates do not by themselves prevent a match.
    """

    if date_a is None or date_b is None:
        return True

    difference = abs(
        date_a - date_b
    )

    return difference <= timedelta(
        days=EVENT_DATE_WINDOW_DAYS
    )


def funding_event_matches(
    *,
    company_id_a,
    amount_a,
    currency_a,
    round_type_a,
    announced_at_a,
    company_id_b,
    amount_b,
    currency_b,
    round_type_b,
    announced_at_b,
):
    """
    Single source of truth for funding-event identity.

    Two records are considered a strong candidate for the same
    real-world financing event when they have:

    - the same canonical company
    - the same known currency
    - approximately the same amount
    - compatible round types
    - compatible announcement dates

    This function performs no database writes.
    """

    if company_id_a is None or company_id_b is None:
        return False

    if company_id_a != company_id_b:
        return False

    if not currencies_match(
        currency_a,
        currency_b,
    ):
        return False

    if not amounts_match(
        amount_a,
        amount_b,
    ):
        return False

    if not round_types_compatible(
        round_type_a,
        round_type_b,
    ):
        return False

    if not dates_compatible(
        announced_at_a,
        announced_at_b,
    ):
        return False

    return True


def funding_rounds_match(
    funding_round_a,
    funding_round_b,
):
    """
    Compare two persisted FundingRound records using the same
    matching rules as live ingestion.
    """

    if funding_round_a is None:
        return False

    if funding_round_b is None:
        return False

    if funding_round_a.id == funding_round_b.id:
        return False

    return funding_event_matches(
        company_id_a=funding_round_a.company_id,
        amount_a=funding_round_a.amount,
        currency_a=funding_round_a.currency,
        round_type_a=funding_round_a.round_type,
        announced_at_a=funding_round_a.announced_at,

        company_id_b=funding_round_b.company_id,
        amount_b=funding_round_b.amount,
        currency_b=funding_round_b.currency,
        round_type_b=funding_round_b.round_type,
        announced_at_b=funding_round_b.announced_at,
    )


def find_matching_funding_round(
    company,
    amount,
    currency,
    round_type,
    announced_at,
):
    """
    Find an existing canonical FundingRound that appears to
    represent the same real-world financing event.

    This is used during live ingestion.
    """

    if company is None:
        return None

    if company.id is None:
        return None

    if amount is None:
        return None

    if not currency:
        return None

    normalized_currency = normalize_currency(
        currency
    )

    candidate_rounds = FundingRound.query.filter_by(
        company_id=company.id,
        currency=normalized_currency,
    ).all()

    for candidate in candidate_rounds:
        if funding_event_matches(
            company_id_a=company.id,
            amount_a=amount,
            currency_a=currency,
            round_type_a=round_type,
            announced_at_a=announced_at,

            company_id_b=candidate.company_id,
            amount_b=candidate.amount,
            currency_b=candidate.currency,
            round_type_b=candidate.round_type,
            announced_at_b=candidate.announced_at,
        ):
            return candidate

    return None