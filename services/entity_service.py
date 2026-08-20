from models.article import db
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound

from services.entity_resolution_service import (
    resolve_entity_name,
)
from services.entity_review_service import (
    record_entity_resolution_review,
)
from services.event_resolution_service import (
    find_matching_funding_round,
)
from services.taxonomy_service import (
    canonicalize_sector,
)
from services.round_taxonomy_service import (
    canonicalize_round_type,
)


def save_funding_extraction(
    article,
    extraction,
):
    """
    Persist a structured company-funding extraction into the
    current database session.

    Responsibilities:
    - resolve the company
    - enrich company metadata
    - resolve the canonical funding event
    - attach supporting evidence
    - resolve participating investors
    - resolve lead investors

    Transaction ownership belongs to the caller.

    This function deliberately does not commit.
    """

    if not extraction.is_funding_round:
        return None

    if not extraction.event_evidence:
        return None

    if not extraction.company_name:
        return None

    # ---------------------------------------------------------
    # Resolve company
    # ---------------------------------------------------------

    company_resolution = resolve_entity_name(
        extraction.company_name,
        "company",
    )

    if company_resolution["status"] == "invalid":
        return None

    record_entity_resolution_review(
        article=article,
        resolution=company_resolution,
        entity_type="company",
    )

    company_name = (
        company_resolution["canonical_name"]
        or company_resolution["normalized_name"]
    )

    company = company_resolution["entity"]

    if company is None:
        company = Company.query.filter_by(
            name=company_name
        ).first()

    if company is None:
        company = Company(
            name=company_name
        )

        db.session.add(
            company
        )

        # Required because event resolution needs company.id.
        db.session.flush()

    # ---------------------------------------------------------
    # Enrich company metadata
    # ---------------------------------------------------------

    if extraction.sector:
        company.sector = extraction.sector

        company.canonical_sector = (
            canonicalize_sector(
                extraction.sector
            )
        )

    if extraction.company_city:
        company.city = (
            extraction.company_city
        )

    if extraction.company_country:
        company.country = (
            extraction.company_country
        )

    if extraction.founded_year:
        company.founded_year = (
            extraction.founded_year
        )

    # ---------------------------------------------------------
    # Resolve canonical real-world funding event
    # ---------------------------------------------------------

    funding_round = find_matching_funding_round(
        company=company,
        amount=extraction.amount,
        currency=extraction.currency,
        round_type=extraction.round_type,
        announced_at=article.published_at,
    )

    # Compatibility fallback for historical records created
    # before multi-source event resolution existed.
    if funding_round is None:
        funding_round = FundingRound.query.filter_by(
            article_id=article.id
        ).first()

    # ---------------------------------------------------------
    # Create new canonical event
    # ---------------------------------------------------------

    if funding_round is None:
        funding_round = FundingRound(
            company=company,
            event_evidence=extraction.event_evidence,
            amount=extraction.amount,
            currency=extraction.currency,
            round_type=extraction.round_type,
            canonical_round_type=(
                canonicalize_round_type(
                    extraction.round_type
                )
            ),
            announced_at=article.published_at,
            article=article,
        )

        db.session.add(
            funding_round
        )

        db.session.flush()

    # ---------------------------------------------------------
    # Enrich existing canonical event
    # ---------------------------------------------------------

    else:
        funding_round.company = company

        if extraction.event_evidence:
            funding_round.event_evidence = (
                extraction.event_evidence
            )

        if extraction.amount is not None:
            funding_round.amount = (
                extraction.amount
            )

        if extraction.currency:
            funding_round.currency = (
                extraction.currency
            )

        if extraction.round_type:
            funding_round.round_type = (
                extraction.round_type
            )

            funding_round.canonical_round_type = (
                canonicalize_round_type(
                    extraction.round_type
                )
            )

        # Preserve the earliest known announcement date.
        if article.published_at:
            if (
                funding_round.announced_at is None
                or article.published_at
                < funding_round.announced_at
            ):
                funding_round.announced_at = (
                    article.published_at
                )

        # Retain backwards-compatible primary article.
        if funding_round.article is None:
            funding_round.article = article

    # ---------------------------------------------------------
    # Supporting source evidence
    # ---------------------------------------------------------

    if article not in funding_round.articles:
        funding_round.articles.append(
            article
        )

    # ---------------------------------------------------------
    # Participating investors
    # ---------------------------------------------------------

    for investor_name in extraction.investors:
        investor = _resolve_or_create_investor(
            article=article,
            investor_name=investor_name,
        )

        if investor is None:
            continue

        if investor not in funding_round.investors:
            funding_round.investors.append(
                investor
            )

    # ---------------------------------------------------------
    # Lead investors
    # ---------------------------------------------------------

    for investor_name in extraction.lead_investors:
        investor = _resolve_or_create_investor(
            article=article,
            investor_name=investor_name,
        )

        if investor is None:
            continue

        if investor not in funding_round.investors:
            funding_round.investors.append(
                investor
            )

        if investor not in funding_round.lead_investors:
            funding_round.lead_investors.append(
                investor
            )

    db.session.flush()

    return funding_round


def _resolve_or_create_investor(
    article,
    investor_name,
):
    """
    Resolve one extracted investor against the knowledge base,
    creating a new Investor only when no existing entity can be
    used.

    Transaction ownership remains with the caller.
    """

    investor_resolution = resolve_entity_name(
        investor_name,
        "investor",
    )

    if investor_resolution["status"] == "invalid":
        return None

    record_entity_resolution_review(
        article=article,
        resolution=investor_resolution,
        entity_type="investor",
    )

    resolved_name = (
        investor_resolution["canonical_name"]
        or investor_resolution["normalized_name"]
    )

    investor = investor_resolution["entity"]

    if investor is None:
        investor = Investor.query.filter_by(
            name=resolved_name
        ).first()

    if investor is None:
        investor = Investor(
            name=resolved_name
        )

        db.session.add(
            investor
        )

        db.session.flush()

    return investor