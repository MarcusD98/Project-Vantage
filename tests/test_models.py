from models.article import db
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound
from models.fund import Fund
from models.fund_close import FundClose


def test_models_can_be_created():
    company = Company(
        name="Test Company"
    )

    investor = Investor(
        name="Test Investor"
    )

    funding_round = FundingRound(
        company=company,
        amount=50_000_000,
        currency="USD",
        round_type="Series B",
    )

    funding_round.investors.append(investor)
    funding_round.lead_investors.append(investor)

    fund = Fund(
        name="Test Fund I",
        investor=investor,
        strategy="Early Stage",
        geography="Europe",
        vintage_year=2026,
    )

    fund_close = FundClose(
        fund=fund,
        amount=300_000_000,
        currency="EUR",
        close_type="final_close",
    )

    assert funding_round.company.name == "Test Company"
    assert funding_round.amount == 50_000_000
    assert funding_round.round_type == "Series B"
    assert funding_round.investors[0].name == "Test Investor"
    assert funding_round.lead_investors[0].name == "Test Investor"

    assert fund.name == "Test Fund I"
    assert fund.investor.name == "Test Investor"
    assert fund.strategy == "Early Stage"

    assert fund_close.fund.name == "Test Fund I"
    assert fund_close.amount == 300_000_000
    assert fund_close.close_type == "final_close"