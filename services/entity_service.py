from models.article import db, Article
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound

from services.funding_extractor import extract_funding_data
from services.llm_extractor import extract_funding_with_llm
from services.article_service import populate_article_content
from services.entity_normalizer import normalize_entity_name
from services.entity_resolution_service import resolve_entity_name
from services.entity_review_service import record_entity_resolution_review

from datetime import datetime

def create_funding_event(
    article,
    company_name,
    amount,
    currency,
    round_type,
    investor_names,
):
    company_name = normalize_entity_name(
        company_name,
        entity_type="company",
    )

    company = Company.query.filter_by(
        name=company_name
    ).first()

    if company is None:
        company = Company(
            name=company_name
        )
        db.session.add(company)

    funding_round = FundingRound(
        company=company,
        amount=amount,
        currency=currency,
        round_type=round_type,
        announced_at=article.published_at,
        article=article,
    )

    for investor_name in investor_names:
        investor_name = normalize_entity_name(
            investor_name,
            entity_type="investor",
        )

        investor = Investor.query.filter_by(
            name=investor_name
        ).first()

        if investor is None:
            investor = Investor(
                name=investor_name
            )
            db.session.add(investor)

        funding_round.investors.append(investor)

    db.session.add(funding_round)
    db.session.commit()

    return funding_round

def process_funding_article(article):
    # Try to extract structured funding data from the article title
    funding_data = extract_funding_data(article.title)

    if funding_data is None:
        return None

    # Avoid creating the same funding round twice
    existing_round = FundingRound.query.filter_by(
        article_id=article.id
    ).first()

    if existing_round:
        return existing_round

    return create_funding_event(
        article=article,
        company_name=funding_data["company_name"],
        amount=funding_data["amount"],
        currency=funding_data["currency"],
        round_type=funding_data["round_type"],
        investor_names=[],
    )

def process_funding_articles():
    articles = Article.query.filter_by(
        category="Funding Round"
    ).all()

    created_count = 0

    for article in articles:
        existing_round = FundingRound.query.filter_by(
            article_id=article.id
        ).first()

        if existing_round:
            continue

        funding_round = process_funding_article(article)

        if funding_round is not None:
            created_count += 1

    return created_count

def save_funding_extraction(article, extraction):
    if not extraction.is_funding_round:
        return None

    if not extraction.event_evidence:
        return None

    if extraction.company_name is None:
        return None

    # Resolve the extracted company against the knowledge base
    company_resolution = resolve_entity_name(
        extraction.company_name,
        "company",
    )

    if company_resolution["status"] == "invalid":
        return None

    # Persist uncertain company resolutions for review
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
        db.session.add(company)

    # Enrich company metadata
    if extraction.sector:
        company.sector = extraction.sector

    if extraction.company_city:
        company.city = extraction.company_city

    if extraction.company_country:
        company.country = extraction.company_country

    if extraction.founded_year:
        company.founded_year = extraction.founded_year

    # Find an existing funding round linked to this article
    funding_round = FundingRound.query.filter_by(
        article_id=article.id
    ).first()

    if funding_round is None:
        funding_round = FundingRound(
            company=company,
            event_evidence=extraction.event_evidence,
            amount=extraction.amount,
            currency=extraction.currency,
            round_type=extraction.round_type,
            announced_at=article.published_at,
            article=article,
        )

        db.session.add(funding_round)

    else:
        funding_round.company = company
        funding_round.event_evidence = extraction.event_evidence
        funding_round.amount = extraction.amount
        funding_round.currency = extraction.currency
        funding_round.round_type = extraction.round_type

    # Resolve and connect participating investors
    for investor_name in extraction.investors:
        investor_resolution = resolve_entity_name(
            investor_name,
            "investor",
        )

        if investor_resolution["status"] == "invalid":
            continue

        # Persist uncertain investor resolutions for review
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
            db.session.add(investor)

        if investor not in funding_round.investors:
            funding_round.investors.append(investor)

    # Resolve and connect lead investors
    for investor_name in extraction.lead_investors:
        investor_resolution = resolve_entity_name(
            investor_name,
            "investor",
        )

        if investor_resolution["status"] == "invalid":
            continue

        # Persist uncertain lead-investor resolutions for review
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
            db.session.add(investor)

        if investor not in funding_round.investors:
            funding_round.investors.append(investor)

        if investor not in funding_round.lead_investors:
            funding_round.lead_investors.append(investor)

    db.session.commit()

    return funding_round

def enrich_funding_articles_with_llm(limit=5):
    articles = Article.query.filter(
        Article.category == "Funding Round",
        Article.content.is_not(None),
        Article.llm_processed_at.is_(None),
    ).limit(limit).all()

    enriched_count = 0

    for article in articles:
        extraction = extract_funding_with_llm(article)

        if extraction is None:
            continue

        # Record that this article has now been processed by the LLM
        article.llm_processed_at = datetime.now()
        article.llm_is_funding_round = extraction.is_funding_round

        funding_round = save_funding_extraction(
            article,
            extraction,
        )

        db.session.commit()

        if funding_round is not None:
            enriched_count += 1

    return enriched_count

def process_intelligence_batch(limit=5):
    articles = Article.query.filter(
        Article.category == "Funding Round",
        Article.llm_processed_at.is_(None),
    ).limit(limit).all()

    processed_count = 0
    funding_count = 0

    for article in articles:
        # Step 1: make sure we have full article content
        if not article.content:
            content = populate_article_content(article)

            if not content:
                continue

        # Step 2: use the LLM to understand the article
        extraction = extract_funding_with_llm(article)

        if extraction is None:
            continue

        # Step 3: record that the LLM has processed the article
        article.llm_processed_at = datetime.now()
        article.llm_is_funding_round = extraction.is_funding_round

        # Step 4: save structured VC data if this is a real funding event
        funding_round = save_funding_extraction(
            article,
            extraction,
        )

        db.session.commit()

        processed_count += 1

        if funding_round is not None:
            funding_count += 1

    return {
        "processed": processed_count,
        "funding_rounds": funding_count,
    }
