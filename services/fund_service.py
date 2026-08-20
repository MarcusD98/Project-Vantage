from models.article import db
from models.investor import Investor
from models.fund import Fund
from models.fund_close import FundClose

from services.entity_resolution_service import (
    resolve_entity_name,
)

from services.entity_review_service import (
    record_entity_resolution_review,
)

from services.fund_event_resolution_service import (
    find_matching_fund_close,
)


def save_fund_close_extraction(
    article,
    extraction,
):
    """
    Persist a structured fund-close extraction into the
    current database session.

    Responsibilities:
    - resolve the investor / fund manager
    - resolve or create the Fund
    - resolve the canonical FundClose event
    - attach supporting evidence
    - enrich Fund and FundClose metadata

    Transaction ownership belongs to the caller.

    This function deliberately does not commit.
    """

    if not extraction.is_fund_close:
        return None

    if not extraction.event_evidence:
        return None

    if not extraction.investor_name:
        return None

    # ---------------------------------------------------------
    # Resolve fund manager / investor
    # ---------------------------------------------------------

    investor_resolution = resolve_entity_name(
        extraction.investor_name,
        "investor",
    )

    if investor_resolution["status"] == "invalid":
        return None

    record_entity_resolution_review(
        article=article,
        resolution=investor_resolution,
        entity_type="investor",
    )

    investor_name = (
        investor_resolution["canonical_name"]
        or investor_resolution["normalized_name"]
    )

    investor = investor_resolution["entity"]

    if investor is None:
        investor = Investor.query.filter_by(
            name=investor_name
        ).first()

    if investor is None:
        investor = Investor(
            name=investor_name
        )

        db.session.add(
            investor
        )

        db.session.flush()

    # ---------------------------------------------------------
    # Resolve Fund
    # ---------------------------------------------------------

    if not extraction.fund_name:
        return None

    fund = Fund.query.filter_by(
        name=extraction.fund_name,
        investor_id=investor.id,
    ).first()

    if fund is None:
        fund = Fund(
            name=extraction.fund_name,
            investor=investor,
            strategy=extraction.strategy,
            geography=extraction.geography,
            vintage_year=extraction.vintage_year,
        )

        db.session.add(
            fund
        )

        # Required because event resolution needs fund.id.
        db.session.flush()

    else:
        if extraction.strategy:
            fund.strategy = (
                extraction.strategy
            )

        if extraction.geography:
            fund.geography = (
                extraction.geography
            )

        if extraction.vintage_year:
            fund.vintage_year = (
                extraction.vintage_year
            )

    # ---------------------------------------------------------
    # Resolve canonical real-world FundClose event
    # ---------------------------------------------------------

    fund_close = find_matching_fund_close(
        fund=fund,
        amount=extraction.amount,
        currency=extraction.currency,
        close_type=extraction.close_type,
        announced_at=article.published_at,
    )

    # Compatibility / idempotency fallback:
    # preserve the existing behaviour for an article that has
    # already created a FundClose.
    if fund_close is None:
        fund_close = FundClose.query.filter_by(
            article_id=article.id
        ).first()

    # ---------------------------------------------------------
    # Create new canonical FundClose
    # ---------------------------------------------------------

    if fund_close is None:
        fund_close = FundClose(
            fund=fund,
            article=article,
            amount=extraction.amount,
            currency=extraction.currency,
            close_type=extraction.close_type,
            announced_at=article.published_at,
            event_evidence=extraction.event_evidence,
        )

        db.session.add(
            fund_close
        )

        db.session.flush()

    # ---------------------------------------------------------
    # Enrich existing canonical FundClose
    # ---------------------------------------------------------

    else:
        fund_close.fund = fund

        if extraction.event_evidence:
            fund_close.event_evidence = (
                extraction.event_evidence
            )

        if extraction.amount is not None:
            fund_close.amount = (
                extraction.amount
            )

        if extraction.currency:
            fund_close.currency = (
                extraction.currency
                .strip()
                .upper()
            )

        if extraction.close_type:
            fund_close.close_type = (
                extraction.close_type
            )

        # Preserve the earliest known announcement date.
        if article.published_at:
            if (
                fund_close.announced_at is None
                or article.published_at
                < fund_close.announced_at
            ):
                fund_close.announced_at = (
                    article.published_at
                )

        # Retain backwards-compatible primary article.
        if fund_close.article is None:
            fund_close.article = article

    # ---------------------------------------------------------
    # Supporting source evidence
    # ---------------------------------------------------------

    if article not in fund_close.articles:
        fund_close.articles.append(
            article
        )

    db.session.flush()

    return fund_close