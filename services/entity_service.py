from models.article import db, Article
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound

from services.funding_extractor import extract_funding_data
from services.llm_extractor import extract_funding_with_llm


def create_funding_event(
    article,
    company_name,
    amount,
    currency,
    round_type,
    investor_names,
):
    # Find existing company or create it
    company = Company.query.filter_by(
        name=company_name
    ).first()

    if company is None:
        company = Company(name=company_name)
        db.session.add(company)

    # Create the funding round
    funding_round = FundingRound(
        company=company,
        amount=amount,
        currency=currency,
        round_type=round_type,
        announced_at=article.published_at,
        article=article,
    )

    # Find/create each investor and connect it to the round
    for investor_name in investor_names:
        investor = Investor.query.filter_by(
            name=investor_name
        ).first()

        if investor is None:
            investor = Investor(name=investor_name)
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

    # Find or create the company
    company = Company.query.filter_by(
        name=extraction.company_name
    ).first()

    if company is None:
        company = Company(
            name=extraction.company_name
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

    # Find an existing round linked to this article
    funding_round = FundingRound.query.filter_by(
        article_id=article.id
    ).first()

    # Create it only if we don't already have one
    if funding_round is None:
        funding_round = FundingRound(
            company=company,
            amount=extraction.amount,
            currency=extraction.currency,
            round_type=extraction.round_type,
            announced_at=article.published_at,
            article=article,
        )

        db.session.add(funding_round)

    else:
        # Upgrade our existing round with the better AI extraction
        funding_round.company = company
        funding_round.event_evidence = extraction.event_evidence
        funding_round.amount = extraction.amount
        funding_round.currency = extraction.currency
        funding_round.round_type = extraction.round_type

    # Create/connect all participating investors
    for investor_name in extraction.investors:
        investor = Investor.query.filter_by(
            name=investor_name
        ).first()

        if investor is None:
            investor = Investor(name=investor_name)
            db.session.add(investor)

        if investor not in funding_round.investors:
            funding_round.investors.append(investor)

    # Mark lead investors separately
    for investor_name in extraction.lead_investors:
        investor = Investor.query.filter_by(
            name=investor_name
        ).first()

        if investor is None:
            investor = Investor(name=investor_name)
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
    ).limit(limit).all()

    enriched_count = 0

    for article in articles:
        extraction = extract_funding_with_llm(article)

        if extraction is None:
            continue

        funding_round = save_funding_extraction(
            article,
            extraction,
        )

        if funding_round is not None:
            enriched_count += 1

    return enriched_count
