from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound
from models.entity_alias import EntityAlias

from services.entity_candidate_service import (
    find_company_duplicate_candidates,
    find_investor_duplicate_candidates,
)


def get_data_quality_summary():
    companies = Company.query.all()
    investors = Investor.query.all()
    funding_rounds = FundingRound.query.all()
    aliases = EntityAlias.query.order_by(
        EntityAlias.entity_type,
        EntityAlias.alias,
    ).all()

    company_duplicate_candidates = (
        find_company_duplicate_candidates()
    )

    investor_duplicate_candidates = (
        find_investor_duplicate_candidates()
    )

    companies_missing_sector = sum(
        1
        for company in companies
        if not company.sector
    )

    companies_missing_country = sum(
        1
        for company in companies
        if not company.country
    )

    companies_missing_founded_year = sum(
        1
        for company in companies
        if not company.founded_year
    )

    rounds_missing_round_type = sum(
        1
        for funding_round in funding_rounds
        if not funding_round.round_type
    )

    rounds_without_investors = sum(
        1
        for funding_round in funding_rounds
        if not funding_round.investors
    )

    rounds_without_evidence = sum(
        1
        for funding_round in funding_rounds
        if not funding_round.event_evidence
    )

    return {
        "company_count": len(companies),
        "investor_count": len(investors),
        "funding_round_count": len(funding_rounds),
        "alias_count": len(aliases),

        "company_duplicate_candidates":
            company_duplicate_candidates,

        "investor_duplicate_candidates":
            investor_duplicate_candidates,

        "aliases": aliases,

        "companies_missing_sector":
            companies_missing_sector,

        "companies_missing_country":
            companies_missing_country,

        "companies_missing_founded_year":
            companies_missing_founded_year,

        "rounds_missing_round_type":
            rounds_missing_round_type,

        "rounds_without_investors":
            rounds_without_investors,

        "rounds_without_evidence":
            rounds_without_evidence,
    }