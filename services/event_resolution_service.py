from datetime import timedelta

from models.funding_round import FundingRound


EVENT_DATE_WINDOW_DAYS = 14

# Sparse events have weaker identity signals, so use a much
# tighter temporal window before treating two evidence records
# as the same real-world event.
SPARSE_EVENT_DATE_WINDOW_DAYS = 3

AMOUNT_TOLERANCE_RATIO = 0.02


def normalize_round_type(
    round_type,
):
    if not round_type:
        return None

    return (
        round_type
        .strip()
        .lower()
        .replace(
            "-",
            " ",
        )
    )


def normalize_currency(
    currency,
):
    if not currency:
        return None

    return (
        currency
        .strip()
        .upper()
    )


def amounts_match(
    amount_a,
    amount_b,
):
    """
    Return True when two funding amounts are close enough to
    plausibly represent the same reported financing event.
    """

    if (
        amount_a is None
        or amount_b is None
    ):
        return False

    if (
        amount_a <= 0
        or amount_b <= 0
    ):
        return False

    difference = abs(
        amount_a
        - amount_b
    )

    tolerance = max(
        amount_a,
        amount_b,
    ) * AMOUNT_TOLERANCE_RATIO

    return (
        difference
        <= tolerance
    )


def currencies_match(
    currency_a,
    currency_b,
):
    """
    Require both events to have the same known currency.

    We deliberately do not attempt FX conversion in event
    resolution because that could create false merges.
    """

    normalized_a = (
        normalize_currency(
            currency_a
        )
    )

    normalized_b = (
        normalize_currency(
            currency_b
        )
    )

    if (
        not normalized_a
        or not normalized_b
    ):
        return False

    return (
        normalized_a
        == normalized_b
    )


def round_types_compatible(
    round_type_a,
    round_type_b,
):
    """
    Determine whether two raw funding-stage descriptions are
    compatible.

    Missing round type does not invalidate an otherwise strong
    match when amount and currency already provide strong event
    identity.
    """

    normalized_a = (
        normalize_round_type(
            round_type_a
        )
    )

    normalized_b = (
        normalize_round_type(
            round_type_b
        )
    )

    if (
        not normalized_a
        or not normalized_b
    ):
        return True

    return (
        normalized_a
        == normalized_b
    )


def dates_compatible(
    date_a,
    date_b,
    window_days=EVENT_DATE_WINDOW_DAYS,
):
    """
    Return True when two evidence dates fall within the supplied
    event-resolution window.

    For strongly identified events, missing dates remain
    compatible.

    Sparse matching separately requires both dates to exist.
    """

    if (
        date_a is None
        or date_b is None
    ):
        return True

    difference = abs(
        date_a
        - date_b
    )

    return (
        difference
        <= timedelta(
            days=window_days
        )
    )


def _known_amounts_do_not_conflict(
    amount_a,
    amount_b,
):
    """
    Missing amount is neutral.

    When both amounts are known, they must satisfy the normal
    funding amount tolerance.
    """

    if (
        amount_a is None
        or amount_b is None
    ):
        return True

    return amounts_match(
        amount_a,
        amount_b,
    )


def _known_currencies_do_not_conflict(
    currency_a,
    currency_b,
):
    """
    Missing currency is neutral.

    When both currencies are known, they must agree.
    """

    normalized_a = (
        normalize_currency(
            currency_a
        )
    )

    normalized_b = (
        normalize_currency(
            currency_b
        )
    )

    if (
        normalized_a is None
        or normalized_b is None
    ):
        return True

    return (
        normalized_a
        == normalized_b
    )


def _sparse_funding_event_matches(
    *,
    amount_a,
    currency_a,
    round_type_a,
    announced_at_a,
    amount_b,
    currency_b,
    round_type_b,
    announced_at_b,
):
    """
    Conservatively resolve funding events when amount and/or
    currency are unavailable.

    Sparse matching deliberately requires stronger remaining
    signals:

    - both publication/announcement dates must be known
    - dates must be within three days
    - both round types must be known
    - normalized round types must match exactly
    - any known amounts must not conflict
    - any known currencies must not conflict

    If those signals are not available, Vantage prefers separate
    canonical events over an unsafe automatic merge.
    """

    if (
        announced_at_a is None
        or announced_at_b is None
    ):
        return False

    if not dates_compatible(
        announced_at_a,
        announced_at_b,
        window_days=(
            SPARSE_EVENT_DATE_WINDOW_DAYS
        ),
    ):
        return False

    normalized_round_a = (
        normalize_round_type(
            round_type_a
        )
    )

    normalized_round_b = (
        normalize_round_type(
            round_type_b
        )
    )

    if (
        not normalized_round_a
        or not normalized_round_b
    ):
        return False

    if (
        normalized_round_a
        != normalized_round_b
    ):
        return False

    if not _known_amounts_do_not_conflict(
        amount_a,
        amount_b,
    ):
        return False

    if not _known_currencies_do_not_conflict(
        currency_a,
        currency_b,
    ):
        return False

    return True


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

    Strong match:

        same canonical company
        + known matching currency
        + approximately matching amount
        + compatible round type
        + dates within the normal event window

    Sparse match:

        same canonical company
        + missing amount and/or currency
        + same known round type
        + both dates known and within a tighter window
        + no conflict among any known amount/currency values

    This function performs no database writes.
    """

    if (
        company_id_a is None
        or company_id_b is None
    ):
        return False

    if (
        company_id_a
        != company_id_b
    ):
        return False

    strong_identity_available = (
        amount_a is not None
        and amount_b is not None
        and normalize_currency(
            currency_a
        )
        is not None
        and normalize_currency(
            currency_b
        )
        is not None
    )

    if strong_identity_available:
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

    return (
        _sparse_funding_event_matches(
            amount_a=amount_a,
            currency_a=currency_a,
            round_type_a=round_type_a,
            announced_at_a=announced_at_a,

            amount_b=amount_b,
            currency_b=currency_b,
            round_type_b=round_type_b,
            announced_at_b=announced_at_b,
        )
    )


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

    if (
        funding_round_a.id
        == funding_round_b.id
    ):
        return False

    return funding_event_matches(
        company_id_a=(
            funding_round_a.company_id
        ),
        amount_a=(
            funding_round_a.amount
        ),
        currency_a=(
            funding_round_a.currency
        ),
        round_type_a=(
            funding_round_a.round_type
        ),
        announced_at_a=(
            funding_round_a.announced_at
        ),

        company_id_b=(
            funding_round_b.company_id
        ),
        amount_b=(
            funding_round_b.amount
        ),
        currency_b=(
            funding_round_b.currency
        ),
        round_type_b=(
            funding_round_b.round_type
        ),
        announced_at_b=(
            funding_round_b.announced_at
        ),
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

    Candidate selection intentionally starts with canonical
    company identity.

    Event-level strong or sparse matching then determines
    whether an existing round can safely be reused.
    """

    if company is None:
        return None

    if company.id is None:
        return None

    candidate_rounds = (
        FundingRound.query
        .filter_by(
            company_id=company.id,
        )
        .all()
    )

    for candidate in candidate_rounds:
        if funding_event_matches(
            company_id_a=company.id,
            amount_a=amount,
            currency_a=currency,
            round_type_a=round_type,
            announced_at_a=announced_at,

            company_id_b=(
                candidate.company_id
            ),
            amount_b=(
                candidate.amount
            ),
            currency_b=(
                candidate.currency
            ),
            round_type_b=(
                candidate.round_type
            ),
            announced_at_b=(
                candidate.announced_at
            ),
        ):
            return candidate

    return None