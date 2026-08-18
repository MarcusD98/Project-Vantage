from models.article import db, Article
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound


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