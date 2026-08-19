from models.article import db, Article
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound

from services.funding_extractor import extract_funding_data


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

