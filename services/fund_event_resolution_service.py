from models.fund_close import FundClose

from services.event_resolution_service import (
    amounts_match,
    currencies_match,
    dates_compatible,
)


def normalize_close_type(close_type):
    if not close_type:
        return None

    return (
        close_type
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def close_types_compatible(
    close_type_a,
    close_type_b,
):
    """
    Determine whether two fund-close descriptions are
    compatible.

    Missing or unknown close type should not block an
    otherwise strong match because many fund announcements
    do not clearly distinguish first, interim, or final close.
    """

    normalized_a = normalize_close_type(
        close_type_a
    )

    normalized_b = normalize_close_type(
        close_type_b
    )

    if not normalized_a or not normalized_b:
        return True

    if normalized_a == "unknown":
        return True

    if normalized_b == "unknown":
        return True

    return normalized_a == normalized_b


def fund_close_events_match(
    *,
    fund_id_a,
    amount_a,
    currency_a,
    close_type_a,
    announced_at_a,
    fund_id_b,
    amount_b,
    currency_b,
    close_type_b,
    announced_at_b,
):
    """
    Return True when two fund-close records are strong
    candidates for the same real-world fund-close event.

    Conservative v1 matching requires:

    - the same canonical Fund
    - the same known currency
    - approximately the same amount
    - compatible close types
    - compatible announcement dates

    This function performs no database writes.
    """

    if fund_id_a is None or fund_id_b is None:
        return False

    if fund_id_a != fund_id_b:
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

    if not close_types_compatible(
        close_type_a,
        close_type_b,
    ):
        return False

    if not dates_compatible(
        announced_at_a,
        announced_at_b,
    ):
        return False

    return True


def fund_closes_match(
    fund_close_a,
    fund_close_b,
):
    """
    Compare two persisted FundClose records using the
    canonical fund-close matching rules.
    """

    if fund_close_a is None:
        return False

    if fund_close_b is None:
        return False

    if fund_close_a.id == fund_close_b.id:
        return False

    return fund_close_events_match(
        fund_id_a=fund_close_a.fund_id,
        amount_a=fund_close_a.amount,
        currency_a=fund_close_a.currency,
        close_type_a=fund_close_a.close_type,
        announced_at_a=fund_close_a.announced_at,

        fund_id_b=fund_close_b.fund_id,
        amount_b=fund_close_b.amount,
        currency_b=fund_close_b.currency,
        close_type_b=fund_close_b.close_type,
        announced_at_b=fund_close_b.announced_at,
    )


def find_matching_fund_close(
    fund,
    amount,
    currency,
    close_type,
    announced_at,
):
    """
    Find an existing canonical FundClose that appears to
    represent the same real-world event.

    Matching is intentionally conservative.

    Missing amount or currency currently prevents automatic
    cross-source matching. We should only relax that rule
    later if real Source Network V2 evidence demonstrates a
    clear need.
    """

    if fund is None:
        return None

    if fund.id is None:
        return None

    if amount is None:
        return None

    if not currency:
        return None

    normalized_currency = (
        currency
        .strip()
        .upper()
    )

    candidate_closes = (
        FundClose.query.filter_by(
            fund_id=fund.id,
            currency=normalized_currency,
        ).all()
    )

    for candidate in candidate_closes:
        if fund_close_events_match(
            fund_id_a=fund.id,
            amount_a=amount,
            currency_a=currency,
            close_type_a=close_type,
            announced_at_a=announced_at,

            fund_id_b=candidate.fund_id,
            amount_b=candidate.amount,
            currency_b=candidate.currency,
            close_type_b=candidate.close_type,
            announced_at_b=candidate.announced_at,
        ):
            return candidate

    return None