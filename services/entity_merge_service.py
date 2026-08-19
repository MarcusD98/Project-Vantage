from models.article import db
from models.company import Company
from models.investor import Investor


def merge_investors(alias_name, canonical_name):
    alias_investor = Investor.query.filter_by(
        name=alias_name
    ).first()

    canonical_investor = Investor.query.filter_by(
        name=canonical_name
    ).first()

    if alias_investor is None:
        return False

    if canonical_investor is None:
        canonical_investor = Investor(
            name=canonical_name
        )
        db.session.add(canonical_investor)
        db.session.flush()

    # Move normal investment relationships
    for funding_round in list(alias_investor.funding_rounds):
        if canonical_investor not in funding_round.investors:
            funding_round.investors.append(
                canonical_investor
            )

        if alias_investor in funding_round.investors:
            funding_round.investors.remove(
                alias_investor
            )

    # Move lead-investor relationships
    for funding_round in list(alias_investor.led_funding_rounds):
        if canonical_investor not in funding_round.lead_investors:
            funding_round.lead_investors.append(
                canonical_investor
            )

        if alias_investor in funding_round.lead_investors:
            funding_round.lead_investors.remove(
                alias_investor
            )

    db.session.delete(alias_investor)
    db.session.commit()

    return True


def merge_companies(alias_name, canonical_name):
    alias_company = Company.query.filter_by(
        name=alias_name
    ).first()

    canonical_company = Company.query.filter_by(
        name=canonical_name
    ).first()

    if alias_company is None:
        return False

    if canonical_company is None:
        canonical_company = Company(
            name=canonical_name
        )
        db.session.add(canonical_company)
        db.session.flush()

    # Preserve useful metadata if canonical record is missing it
    if not canonical_company.website and alias_company.website:
        canonical_company.website = alias_company.website

    if not canonical_company.description and alias_company.description:
        canonical_company.description = alias_company.description

    if not canonical_company.sector and alias_company.sector:
        canonical_company.sector = alias_company.sector

    if not canonical_company.headquarters and alias_company.headquarters:
        canonical_company.headquarters = alias_company.headquarters

    if not canonical_company.city and alias_company.city:
        canonical_company.city = alias_company.city

    if not canonical_company.country and alias_company.country:
        canonical_company.country = alias_company.country

    if not canonical_company.founded_year and alias_company.founded_year:
        canonical_company.founded_year = alias_company.founded_year

    # Move funding rounds to the canonical company
    for funding_round in list(alias_company.funding_rounds):
        funding_round.company = canonical_company

    db.session.delete(alias_company)
    db.session.commit()

    return True

def remove_invalid_investor(investor_name):
    investor = Investor.query.filter_by(
        name=investor_name
    ).first()

    if investor is None:
        return False

    # Remove normal investment relationships
    for funding_round in list(investor.funding_rounds):
        if investor in funding_round.investors:
            funding_round.investors.remove(investor)

    # Remove lead-investor relationships
    for funding_round in list(investor.led_funding_rounds):
        if investor in funding_round.lead_investors:
            funding_round.lead_investors.remove(investor)

    db.session.delete(investor)
    db.session.commit()

    return True

def rename_company(current_name, canonical_name):
    company = Company.query.filter_by(
        name=current_name
    ).first()

    if company is None:
        return False

    existing_company = Company.query.filter_by(
        name=canonical_name
    ).first()

    if existing_company is not None:
        return False

    company.name = canonical_name
    db.session.commit()

    return True