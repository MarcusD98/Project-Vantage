from models.article import db
from models.funding_round import FundingRound

from services.event_resolution_service import (
    funding_rounds_match,
)


def select_canonical_round(
    funding_round_a,
    funding_round_b,
):
    """
    Deterministically choose which FundingRound should survive
    when two records represent the same real-world event.

    Selection rules:

    1. Prefer the earlier known announcement date.
    2. If dates are equal or unavailable, prefer the lower ID.

    This function performs no database writes.
    """

    if funding_round_a is None:
        return funding_round_b

    if funding_round_b is None:
        return funding_round_a

    date_a = funding_round_a.announced_at
    date_b = funding_round_b.announced_at

    if date_a and date_b:
        if date_a < date_b:
            return funding_round_a

        if date_b < date_a:
            return funding_round_b

    elif date_a:
        return funding_round_a

    elif date_b:
        return funding_round_b

    if (
        funding_round_a.id is not None
        and funding_round_b.id is not None
    ):
        if funding_round_a.id <= funding_round_b.id:
            return funding_round_a

        return funding_round_b

    return funding_round_a


def merge_funding_rounds(
    source_round,
    target_round,
    *,
    require_match=True,
):
    """
    Merge source_round into target_round.

    The target survives.
    The source is deleted.

    Preserves:
    - supporting articles
    - participating investors
    - lead investors
    - useful event metadata
    - earliest announcement date
    - a primary article

    Transaction ownership belongs to the caller.

    When require_match=True, the shared funding-event matching
    engine must confirm that the two records represent the same
    event before any mutation occurs.
    """

    if source_round is None:
        return None

    if target_round is None:
        return None

    if source_round is target_round:
        return target_round

    if (
        source_round.id is not None
        and target_round.id is not None
        and source_round.id == target_round.id
    ):
        return target_round

    if require_match:
        if not funding_rounds_match(
            source_round,
            target_round,
        ):
            return None

    # ---------------------------------------------------------
    # Preserve supporting articles
    # ---------------------------------------------------------

    for article in list(
        source_round.articles
    ):
        if article not in target_round.articles:
            target_round.articles.append(
                article
            )

    if (
        source_round.article is not None
        and source_round.article
        not in target_round.articles
    ):
        target_round.articles.append(
            source_round.article
        )

    # ---------------------------------------------------------
    # Preserve participating investors
    # ---------------------------------------------------------

    for investor in list(
        source_round.investors
    ):
        if investor not in target_round.investors:
            target_round.investors.append(
                investor
            )

    # ---------------------------------------------------------
    # Preserve lead investors
    # ---------------------------------------------------------

    for investor in list(
        source_round.lead_investors
    ):
        if investor not in target_round.lead_investors:
            target_round.lead_investors.append(
                investor
            )

        if investor not in target_round.investors:
            target_round.investors.append(
                investor
            )

    # ---------------------------------------------------------
    # Preserve useful metadata
    # ---------------------------------------------------------

    if (
        not target_round.event_evidence
        and source_round.event_evidence
    ):
        target_round.event_evidence = (
            source_round.event_evidence
        )

    if (
        target_round.amount is None
        and source_round.amount is not None
    ):
        target_round.amount = (
            source_round.amount
        )

    if (
        not target_round.currency
        and source_round.currency
    ):
        target_round.currency = (
            source_round.currency
        )

    if (
        not target_round.round_type
        and source_round.round_type
    ):
        target_round.round_type = (
            source_round.round_type
        )

    if (
        not target_round.canonical_round_type
        and source_round.canonical_round_type
    ):
        target_round.canonical_round_type = (
            source_round.canonical_round_type
        )

    # ---------------------------------------------------------
    # Preserve earliest known announcement date
    # ---------------------------------------------------------

    if source_round.announced_at:
        if (
            target_round.announced_at is None
            or source_round.announced_at
            < target_round.announced_at
        ):
            target_round.announced_at = (
                source_round.announced_at
            )

    # ---------------------------------------------------------
    # Preserve primary article
    # ---------------------------------------------------------

    if (
        target_round.article is None
        and source_round.article is not None
    ):
        target_round.article = (
            source_round.article
        )

    # Ensure target primary article also exists in the complete
    # supporting-evidence relationship.
    if (
        target_round.article is not None
        and target_round.article
        not in target_round.articles
    ):
        target_round.articles.append(
            target_round.article
        )

    # ---------------------------------------------------------
    # Remove relationships from source before deletion
    # ---------------------------------------------------------

    source_round.articles.clear()
    source_round.investors.clear()
    source_round.lead_investors.clear()

    db.session.delete(
        source_round
    )

    db.session.flush()

    return target_round


def reconcile_funding_round_pair(
    funding_round_a,
    funding_round_b,
):
    """
    Reconcile two FundingRound records when the shared matching
    engine confirms that they represent the same real-world
    financing event.

    The surviving record is selected deterministically.

    Transaction ownership belongs to the caller.
    """

    if not funding_rounds_match(
        funding_round_a,
        funding_round_b,
    ):
        return None

    target_round = select_canonical_round(
        funding_round_a,
        funding_round_b,
    )

    if target_round is funding_round_a:
        source_round = funding_round_b
    else:
        source_round = funding_round_a

    return merge_funding_rounds(
        source_round=source_round,
        target_round=target_round,
        require_match=True,
    )