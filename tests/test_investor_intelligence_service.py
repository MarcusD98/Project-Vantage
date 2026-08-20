from datetime import (
    datetime,
)

from models.article import (
    Article,
    db,
)

from models.company import (
    Company,
)

from models.funding_round import (
    FundingRound,
)

from models.investor import (
    Investor,
)

from services.investor_intelligence_service import (
    get_investor_profile,
    get_investor_rankings,
)


AS_OF = datetime(
    2026,
    8,
    20,
    12,
    0,
    0,
)


def _investor(
    name,
):
    investor = Investor(
        name=name
    )

    db.session.add(
        investor
    )

    db.session.flush()

    return investor


def _round(
    company_name,
    announced_at,
    investors,
    leads=None,
    stage="Series A",
    sector="Software",
    country="United States",
    amount=None,
    currency=None,
):
    company = Company(
        name=company_name,
        canonical_sector=sector,
        country=country,
    )

    db.session.add(
        company
    )

    db.session.flush()

    funding_round = FundingRound(
        company=company,
        announced_at=announced_at,
        canonical_round_type=stage,
        amount=amount,
        currency=currency,
    )

    db.session.add(
        funding_round
    )

    for investor in investors:
        funding_round.investors.append(
            investor
        )

    for investor in (
        leads
        or []
    ):
        if (
            investor
            not in funding_round.investors
        ):
            funding_round.investors.append(
                investor
            )

        funding_round.lead_investors.append(
            investor
        )

    db.session.flush()

    return funding_round


def test_unknown_investor_returns_none(
    app,
):
    assert (
        get_investor_profile(
            "Missing Investor",
            as_of=AS_OF,
        )
        is None
    )


def test_profile_compares_current_and_previous_windows(
    app,
):
    investor = _investor(
        "Test Capital"
    )

    _round(
        "Current One",
        datetime(
            2026,
            8,
            10,
        ),
        [investor],
    )

    _round(
        "Current Two",
        datetime(
            2026,
            6,
            15,
        ),
        [investor],
    )

    _round(
        "Previous One",
        datetime(
            2026,
            4,
            1,
        ),
        [investor],
    )

    _round(
        "Undated",
        None,
        [investor],
    )

    profile = (
        get_investor_profile(
            "Test Capital",
            window_days=90,
            as_of=AS_OF,
        )
    )

    assert (
        profile[
            "current_window"
        ][
            "investment_count"
        ]
        == 2
    )

    assert (
        profile[
            "previous_window"
        ][
            "investment_count"
        ]
        == 1
    )

    assert (
        profile[
            "change"
        ][
            "investment_delta"
        ]
        == 1
    )

    assert (
        profile[
            "all_time"
        ][
            "investment_count"
        ]
        == 4
    )

    assert (
        profile[
            "coverage"
        ][
            "undated_rounds"
        ]
        == 1
    )


def test_profile_counts_lead_investments(
    app,
):
    investor = _investor(
        "Lead Capital"
    )

    _round(
        "Lead Company",
        datetime(
            2026,
            8,
            1,
        ),
        [investor],
        leads=[
            investor
        ],
    )

    _round(
        "Non Lead Company",
        datetime(
            2026,
            7,
            1,
        ),
        [investor],
    )

    profile = (
        get_investor_profile(
            "Lead Capital",
            as_of=AS_OF,
        )
    )

    assert (
        profile[
            "current_window"
        ][
            "lead_count"
        ]
        == 1
    )

    assert (
        profile[
            "all_time"
        ][
            "lead_count"
        ]
        == 1
    )


def test_profile_builds_stage_sector_and_geography_exposure(
    app,
):
    investor = _investor(
        "Exposure Capital"
    )

    _round(
        "Alpha",
        datetime(
            2026,
            8,
            1,
        ),
        [investor],
        stage="Series A",
        sector="AI",
        country="United Kingdom",
    )

    _round(
        "Beta",
        datetime(
            2026,
            7,
            1,
        ),
        [investor],
        stage="Series A",
        sector="AI",
        country="United Kingdom",
    )

    _round(
        "Gamma",
        datetime(
            2026,
            6,
            1,
        ),
        [investor],
        stage="Seed",
        sector="Fintech",
        country="France",
    )

    profile = (
        get_investor_profile(
            "Exposure Capital",
            as_of=AS_OF,
        )
    )

    assert (
        profile[
            "stage_exposure"
        ][
            "all_time"
        ][0]
        == {
            "stage": "Series A",
            "count": 2,
        }
    )

    assert (
        profile[
            "sector_exposure"
        ][
            "all_time"
        ][0]
        == {
            "sector": "AI",
            "count": 2,
        }
    )

    assert (
        profile[
            "geography_exposure"
        ][
            "all_time"
        ][0]
        == {
            "location":
                "United Kingdom",

            "count":
                2,
        }
    )


def test_profile_counts_co_investors(
    app,
):
    primary = _investor(
        "Primary Capital"
    )

    partner = _investor(
        "Partner Ventures"
    )

    occasional = _investor(
        "Occasional Fund"
    )

    _round(
        "Alpha",
        datetime(
            2026,
            8,
            1,
        ),
        [
            primary,
            partner,
        ],
    )

    _round(
        "Beta",
        datetime(
            2026,
            7,
            1,
        ),
        [
            primary,
            partner,
            occasional,
        ],
    )

    profile = (
        get_investor_profile(
            "Primary Capital",
            as_of=AS_OF,
        )
    )

    assert (
        profile[
            "co_investors"
        ][0]
        == {
            "investor":
                "Partner Ventures",

            "shared_rounds":
                2,
        }
    )


def test_round_volume_keeps_currencies_separate(
    app,
):
    investor = _investor(
        "Volume Capital"
    )

    _round(
        "USD Company",
        datetime(
            2026,
            8,
            1,
        ),
        [investor],
        amount=100_000_000,
        currency="USD",
    )

    _round(
        "EUR Company",
        datetime(
            2026,
            7,
            1,
        ),
        [investor],
        amount=50_000_000,
        currency="EUR",
    )

    profile = (
        get_investor_profile(
            "Volume Capital",
            as_of=AS_OF,
        )
    )

    volumes = {
        item["currency"]:
            item["amount"]
        for item
        in profile[
            "all_time"
        ][
            "round_volume_by_currency"
        ]
    }

    assert (
        volumes["USD"]
        == 100_000_000
    )

    assert (
        volumes["EUR"]
        == 50_000_000
    )


def test_recent_investment_reports_evidence_sources(
    app,
):
    investor = _investor(
        "Evidence Capital"
    )

    funding_round = (
        _round(
            "Evidence Company",
            datetime(
                2026,
                8,
                10,
            ),
            [investor],
        )
    )

    first = Article(
        title="First-party announcement",
        source="Evidence Capital",
        url=(
            "https://example.com/"
            "first-party"
        ),
        category="Funding Round",
    )

    second = Article(
        title="Editorial confirmation",
        source="TechCrunch",
        url=(
            "https://example.com/"
            "editorial"
        ),
        category="Funding Round",
    )

    db.session.add_all(
        [
            first,
            second,
        ]
    )

    db.session.flush()

    funding_round.article = (
        first
    )

    funding_round.articles.append(
        first
    )

    funding_round.articles.append(
        second
    )

    db.session.flush()

    profile = (
        get_investor_profile(
            "Evidence Capital",
            as_of=AS_OF,
        )
    )

    recent = (
        profile[
            "recent_investments"
        ][0]
    )

    assert (
        recent[
            "evidence_count"
        ]
        == 2
    )

    assert set(
        recent[
            "evidence_sources"
        ]
    ) == {
        "Evidence Capital",
        "TechCrunch",
    }


def test_rankings_prioritize_current_activity(
    app,
):
    active = _investor(
        "Active Capital"
    )

    historical = _investor(
        "Historical Capital"
    )

    _investor(
        "No Activity Capital"
    )

    _round(
        "Active One",
        datetime(
            2026,
            8,
            1,
        ),
        [active],
    )

    _round(
        "Active Two",
        datetime(
            2026,
            7,
            1,
        ),
        [active],
    )

    _round(
        "Historical One",
        datetime(
            2026,
            4,
            1,
        ),
        [historical],
    )

    rankings = (
        get_investor_rankings(
            window_days=90,
            as_of=AS_OF,
            limit=10,
        )
    )

    names = [
        item[
            "investor"
        ].name
        for item
        in rankings
    ]

    assert (
        names[0]
        == "Active Capital"
    )

    assert (
        "Historical Capital"
        in names
    )

    assert (
        "No Activity Capital"
        not in names
    )