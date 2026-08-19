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


def save_fund_close_extraction(
    article,
    extraction,
):
    if not extraction.is_fund_close:
        return None

    if not extraction.event_evidence:
        return None

    if not extraction.investor_name:
        return None

    # Resolve the fund manager / investor entity
    investor_resolution = resolve_entity_name(
        extraction.investor_name,
        "investor",
    )

    if investor_resolution["status"] == "invalid":
        return None

    # Persist uncertain matches for human review
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

        db.session.add(investor)
        db.session.flush()

    # We require a usable fund name before creating a Fund record
    if not extraction.fund_name:
        return None

    # Find the fund under this specific investor
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

        db.session.add(fund)
        db.session.flush()

    else:
        # Enrich existing fund metadata when better information exists
        if extraction.strategy:
            fund.strategy = extraction.strategy

        if extraction.geography:
            fund.geography = extraction.geography

        if extraction.vintage_year:
            fund.vintage_year = extraction.vintage_year

    # Avoid duplicate close events for the same article
    existing_close = FundClose.query.filter_by(
        article_id=article.id
    ).first()

    if existing_close is not None:
        existing_close.fund = fund
        existing_close.amount = extraction.amount
        existing_close.currency = extraction.currency
        existing_close.close_type = extraction.close_type
        existing_close.announced_at = article.published_at
        existing_close.event_evidence = extraction.event_evidence

        db.session.commit()

        return existing_close

    fund_close = FundClose(
        fund=fund,
        article=article,
        amount=extraction.amount,
        currency=extraction.currency,
        close_type=extraction.close_type,
        announced_at=article.published_at,
        event_evidence=extraction.event_evidence,
    )

    db.session.add(fund_close)
    db.session.commit()

    return fund_close