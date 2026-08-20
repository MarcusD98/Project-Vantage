from datetime import datetime

from models.article import (
    Article,
    db,
)

from models.company import Company
from models.entity_alias import EntityAlias
from models.funding_round import FundingRound
from models.investor import Investor

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


def _investor(name):
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


def test_profile_resolves_investor_alias(
    app,
):
    canonical = _investor(
        "Index Ventures"
    )

    alias = EntityAlias(
        alias="Index",
        entity_type="investor",
        canonical_name="Index Ventures",
        canonical_investor=canonical,
    )

    db.session.add(
        alias
    )

    _round(
        "Alias Company",
        datetime(
            2026,
            8,
            1,
        ),
        [canonical],
    )

    db.session.commit()

    profile = (
        get_investor_profile(
            "Index",
            as_of=AS_OF,
        )
    )

    assert profile is not None

    assert (
        profile[
            "investor"
        ].name
        == "Index Ventures"
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

    funding_round.article = first

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


def test_profile_reports_dimension_coverage(
    app,
):
    investor = _investor(
        "Coverage Capital"
    )

    _round(
        "One",
        datetime(
            2026,
            8,
            1,
        ),
        [investor],
        stage="Series A",
        sector="AI",
        country=None,
    )

    _round(
        "Two",
        datetime(
            2026,
            7,
            1,
        ),
        [investor],
        stage="Seed",
        sector="Fintech",
        country=None,
    )

    _round(
        "Three",
        datetime(
            2026,
            6,
            1,
        ),
        [investor],
        stage="Series B",
        sector=None,
        country=None,
    )

    _round(
        "Four",
        datetime(
            2026,
            4,
            1,
        ),
        [investor],
        stage=None,
        sector=None,
        country=None,
    )

    profile = (
        get_investor_profile(
            "Coverage Capital",
            as_of=AS_OF,
        )
    )

    coverage = profile[
        "coverage"
    ]

    assert (
        coverage[
            "date"
        ][
            "label"
        ]
        == "high"
    )

    assert (
        coverage[
            "stage"
        ][
            "known"
        ]
        == 3
    )

    assert (
        coverage[
            "stage"
        ][
            "label"
        ]
        == "medium"
    )

    assert (
        coverage[
            "sector"
        ][
            "known"
        ]
        == 2
    )

    assert (
        coverage[
            "sector"
        ][
            "label"
        ]
        == "medium"
    )

    assert (
        coverage[
            "geography"
        ][
            "known"
        ]
        == 0
    )

    assert (
        coverage[
            "geography"
        ][
            "label"
        ]
        == "insufficient"
    )


def test_activity_signal_supported_with_comparison_history(
    app,
):
    investor = _investor(
        "Trend Capital"
    )

    _round(
        "Current One",
        datetime(
            2026,
            8,
            1,
        ),
        [investor],
    )

    _round(
        "Current Two",
        datetime(
            2026,
            7,
            1,
        ),
        [investor],
    )

    _round(
        "Previous One",
        datetime(
            2026,
            5,
            1,
        ),
        [investor],
    )

    _round(
        "Previous Two",
        datetime(
            2026,
            3,
            1,
        ),
        [investor],
    )

    profile = (
        get_investor_profile(
            "Trend Capital",
            as_of=AS_OF,
        )
    )

    signal = profile[
        "signals"
    ][
        "activity"
    ]

    assert (
        signal[
            "status"
        ]
        == "supported"
    )

    assert (
        signal[
            "direction"
        ]
        == "flat"
    )


def test_activity_signal_rejects_current_only_history(
    app,
):
    investor = _investor(
        "Recent Only Capital"
    )

    for index, day in enumerate(
        [
            1,
            5,
            10,
            15,
        ],
        start=1,
    ):
        _round(
            f"Recent {index}",
            datetime(
                2026,
                8,
                day,
            ),
            [investor],
        )

    profile = (
        get_investor_profile(
            "Recent Only Capital",
            as_of=AS_OF,
        )
    )

    signal = profile[
        "signals"
    ][
        "activity"
    ]

    assert (
        signal[
            "status"
        ]
        == "insufficient"
    )

    assert (
        profile[
            "coverage"
        ][
            "comparison_history"
        ][
            "status"
        ]
        == "insufficient"
    )


def test_stage_signal_requires_minimum_known_observations(
    app,
):
    investor = _investor(
        "Small Sample Capital"
    )

    _round(
        "One",
        datetime(
            2026,
            8,
            1,
        ),
        [investor],
        stage="Seed",
    )

    _round(
        "Two",
        datetime(
            2026,
            7,
            1,
        ),
        [investor],
        stage="Seed",
    )

    profile = (
        get_investor_profile(
            "Small Sample Capital",
            as_of=AS_OF,
        )
    )

    assert (
        profile[
            "coverage"
        ][
            "stage"
        ][
            "label"
        ]
        == "high"
    )

    assert (
        profile[
            "signals"
        ][
            "stage"
        ][
            "status"
        ]
        == "insufficient"
    )


def test_stage_and_sector_signals_identify_leading_patterns(
    app,
):
    investor = _investor(
        "Pattern Capital"
    )

    observations = [
        (
            "One",
            "Seed",
            "AI",
        ),
        (
            "Two",
            "Seed",
            "AI",
        ),
        (
            "Three",
            "Seed",
            "AI",
        ),
        (
            "Four",
            "Series A",
            "Fintech",
        ),
        (
            "Five",
            "Series B",
            "Fintech",
        ),
    ]

    for index, (
        company,
        stage,
        sector,
    ) in enumerate(
        observations
    ):
        _round(
            company,
            datetime(
                2026,
                8,
                1,
            )
            - (
                index
                * (
                    datetime(
                        2026,
                        8,
                        1,
                    )
                    - datetime(
                        2026,
                        7,
                        31,
                    )
                )
            ),
            [investor],
            stage=stage,
            sector=sector,
        )

    profile = (
        get_investor_profile(
            "Pattern Capital",
            as_of=AS_OF,
        )
    )

    stage_signal = profile[
        "signals"
    ][
        "stage"
    ]

    sector_signal = profile[
        "signals"
    ][
        "sector"
    ]

    assert (
        stage_signal[
            "status"
        ]
        == "supported"
    )

    assert (
        stage_signal[
            "leaders"
        ]
        == [
            "Seed",
        ]
    )

    assert (
        stage_signal[
            "share"
        ]
        == 0.6
    )

    assert (
        sector_signal[
            "status"
        ]
        == "supported"
    )

    assert (
        sector_signal[
            "leaders"
        ]
        == [
            "AI",
        ]
    )

    assert (
        sector_signal[
            "share"
        ]
        == 0.6
    )


def test_geography_signal_is_gated_by_coverage(
    app,
):
    investor = _investor(
        "Unknown Geography Capital"
    )

    for index in range(4):
        _round(
            f"Company {index}",
            datetime(
                2026,
                8,
                1 + index,
            ),
            [investor],
            country=None,
        )

    profile = (
        get_investor_profile(
            "Unknown Geography Capital",
            as_of=AS_OF,
        )
    )

    assert (
        profile[
            "coverage"
        ][
            "geography"
        ][
            "known"
        ]
        == 0
    )

    assert (
        profile[
            "signals"
        ][
            "geography"
        ][
            "status"
        ]
        == "insufficient"
    )


def test_geography_signal_supported_with_enough_evidence(
    app,
):
    investor = _investor(
        "Geo Capital"
    )

    countries = [
        "United Kingdom",
        "United Kingdom",
        "United Kingdom",
        "France",
    ]

    for index, country in enumerate(
        countries
    ):
        _round(
            f"Geo Company {index}",
            datetime(
                2026,
                8,
                1 + index,
            ),
            [investor],
            country=country,
        )

    profile = (
        get_investor_profile(
            "Geo Capital",
            as_of=AS_OF,
        )
    )

    signal = profile[
        "signals"
    ][
        "geography"
    ]

    assert (
        signal[
            "status"
        ]
        == "supported"
    )

    assert (
        signal[
            "leaders"
        ]
        == [
            "United Kingdom",
        ]
    )

    assert (
        signal[
            "share"
        ]
        == 0.75
    )


def test_rankings_report_trend_support_status(
    app,
):
    investor = _investor(
        "Ranking Capital"
    )

    _round(
        "Current One",
        datetime(
            2026,
            8,
            1,
        ),
        [investor],
    )

    _round(
        "Current Two",
        datetime(
            2026,
            7,
            1,
        ),
        [investor],
    )

    _round(
        "Previous One",
        datetime(
            2026,
            5,
            1,
        ),
        [investor],
    )

    _round(
        "Previous Two",
        datetime(
            2026,
            3,
            1,
        ),
        [investor],
    )

    rankings = (
        get_investor_rankings(
            window_days=90,
            as_of=AS_OF,
        )
    )

    result = next(
        item
        for item
        in rankings
        if (
            item[
                "investor"
            ].name
            == "Ranking Capital"
        )
    )

    assert (
        result[
            "trend_status"
        ]
        == "supported"
    )