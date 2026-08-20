from collections import Counter

from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound
from models.fund_close import FundClose


def get_intelligence_summary():
    companies = Company.query.all()
    investors = Investor.query.all()
    funding_rounds = FundingRound.query.all()

    recent_funding_rounds = FundingRound.query.order_by(
        FundingRound.announced_at.desc()
    ).limit(
        8
    ).all()

    recent_fund_closes = FundClose.query.order_by(
        FundClose.announced_at.desc()
    ).limit(
        6
    ).all()

    investor_activity = []

    for investor in investors:
        round_count = len(
            investor.funding_rounds
        )

        if round_count == 0:
            continue

        investor_activity.append(
            {
                "investor": investor,
                "round_count": round_count,
                "lead_count": len(
                    investor.led_funding_rounds
                ),
            }
        )

    investor_activity = sorted(
        investor_activity,
        key=lambda item: (
            item["round_count"],
            item["lead_count"],
            item["investor"].name,
        ),
        reverse=True,
    )[:10]

    sector_counts = Counter()

    for funding_round in funding_rounds:
        sector = (
            funding_round.company.canonical_sector
            or funding_round.company.sector
        )

        if not sector:
            continue

        sector_counts[sector] += 1

    sector_activity = [
        {
            "sector": sector,
            "round_count": count,
        }
        for sector, count
        in sector_counts.most_common(10)
    ]

    return {
        "company_count": len(companies),
        "investor_count": len(investors),
        "funding_round_count": len(funding_rounds),

        "investor_activity":
            investor_activity,

        "sector_activity":
            sector_activity,

        "recent_funding_rounds":
            recent_funding_rounds,

        "recent_fund_closes":
            recent_fund_closes,
    }