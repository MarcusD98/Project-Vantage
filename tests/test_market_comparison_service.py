from datetime import (
    datetime,
    timedelta,
)

from models.article import db
from models.company import Company
from models.funding_round import FundingRound
from models.investor import Investor

from services.market_comparison_service import (
    compare_market_activity,
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


def _company(
    name,
    sector,
    canonical_sector=None,
):
    company = Company(
        name=name,
        sector=sector,
        canonical_sector=(
            canonical_sector
        ),
    )

    db.session.add(
        company
    )

    db.session.flush()

    return company


def _round(
    *,
    company,
    announced_at,
    investors,
    lead_investors=None,
):
    funding_round = FundingRound(
        company=company,
        announced_at=announced_at,
        round_type="Series A",
    )

    funding_round.investors.extend(
        investors
    )

    funding_round.lead_investors.extend(
        lead_investors
        or []
    )

    db.session.add(
        funding_round
    )

    db.session.flush()

    return funding_round


def _patch_temporal_coverage(
    monkeypatch,
    statuses,
):
    def fake_temporal_coverage(
        investor_name,
        current_start,
        current_end,
        previous_start,
        previous_end,
    ):
        status = (
            statuses[
                investor_name
            ]
        )

        return {
            "status":
                status,

            "reason":
                (
                    None
                    if status
                    == "complete"
                    else (
                        "Incomplete test corpus."
                    )
                ),

            "source_name":
                investor_name,
        }

    monkeypatch.setattr(
        (
            "services.market_comparison_service."
            "get_temporal_corpus_coverage"
        ),
        fake_temporal_coverage,
    )


def test_sector_comparison_uses_only_complete_cohort(
    app,
    monkeypatch,
):
    with app.app_context():
        as_of = datetime(
            2026,
            6,
            30,
        )

        investor_a = (
            _investor(
                "Investor A"
            )
        )

        investor_b = (
            _investor(
                "Investor B"
            )
        )

        investor_c = (
            _investor(
                "Investor C"
            )
        )

        _patch_temporal_coverage(
            monkeypatch,
            {
                "Investor A":
                    "complete",

                "Investor B":
                    "complete",

                "Investor C":
                    "incomplete",
            },
        )

        ai_previous = (
            _company(
                "AI Previous",
                sector="Software",
                canonical_sector=(
                    "AI Infrastructure"
                ),
            )
        )

        ai_current = (
            _company(
                "AI Current",
                sector="Software",
                canonical_sector=(
                    "AI Infrastructure"
                ),
            )
        )

        ignored_fintech = (
            _company(
                "Ignored Fintech",
                sector="Fintech",
            )
        )

        _round(
            company=ai_previous,
            announced_at=(
                as_of
                - timedelta(
                    days=250
                )
            ),
            investors=[
                investor_a
            ],
        )

        current_round = (
            _round(
                company=ai_current,
                announced_at=(
                    as_of
                    - timedelta(
                        days=30
                    )
                ),
                investors=[
                    investor_a,
                    investor_b,
                ],
                lead_investors=[
                    investor_b
                ],
            )
        )

        _round(
            company=ignored_fintech,
            announced_at=(
                as_of
                - timedelta(
                    days=20
                )
            ),
            investors=[
                investor_c
            ],
        )

        result = (
            compare_market_activity(
                window_days=180,
                as_of=as_of,
                investor_names=[
                    "Investor A",
                    "Investor B",
                    "Investor C",
                ],
            )
        )

        assert (
            result[
                "cohort"
            ][
                "comparable_investor_count"
            ]
            == 2
        )

        assert (
            result[
                "current_round_count"
            ]
            == 1
        )

        assert (
            result[
                "previous_round_count"
            ]
            == 1
        )

        assert (
            len(
                result[
                    "comparison"
                ]
            )
            == 1
        )

        ai = (
            result[
                "comparison"
            ][0]
        )

        assert (
            ai[
                "value"
            ]
            == "AI Infrastructure"
        )

        assert (
            ai[
                "current_event_count"
            ]
            == 1
        )

        assert (
            ai[
                "previous_event_count"
            ]
            == 1
        )

        assert (
            ai[
                "delta"
            ]
            == 0
        )

        assert (
            ai[
                "current_investor_count"
            ]
            == 2
        )

        assert (
            ai[
                "current_lead_event_count"
            ]
            == 1
        )

        assert (
            ai[
                "current_event_ids"
            ]
            == [
                current_round.id
            ]
        )

        db.session.rollback()


def test_multi_investor_round_counts_once_as_canonical_event(
    app,
    monkeypatch,
):
    with app.app_context():
        as_of = datetime(
            2026,
            6,
            30,
        )

        investor_a = (
            _investor(
                "Investor A"
            )
        )

        investor_b = (
            _investor(
                "Investor B"
            )
        )

        _patch_temporal_coverage(
            monkeypatch,
            {
                "Investor A":
                    "complete",

                "Investor B":
                    "complete",
            },
        )

        company = (
            _company(
                "Shared Company",
                sector="AI",
            )
        )

        funding_round = (
            _round(
                company=company,
                announced_at=(
                    as_of
                    - timedelta(
                        days=10
                    )
                ),
                investors=[
                    investor_a,
                    investor_b,
                ],
            )
        )

        result = (
            compare_market_activity(
                window_days=180,
                as_of=as_of,
                investor_names=[
                    "Investor A",
                    "Investor B",
                ],
            )
        )

        ai = (
            result[
                "comparison"
            ][0]
        )

        assert (
            ai[
                "current_event_count"
            ]
            == 1
        )

        assert (
            ai[
                "current_investor_count"
            ]
            == 2
        )

        assert (
            ai[
                "current_event_ids"
            ]
            == [
                funding_round.id
            ]
        )

        db.session.rollback()


def test_new_sector_has_no_percentage_change(
    app,
    monkeypatch,
):
    with app.app_context():
        as_of = datetime(
            2026,
            6,
            30,
        )

        investor = (
            _investor(
                "Investor A"
            )
        )

        _patch_temporal_coverage(
            monkeypatch,
            {
                "Investor A":
                    "complete",
            },
        )

        company = (
            _company(
                "Robotics Company",
                sector="Robotics",
            )
        )

        _round(
            company=company,
            announced_at=(
                as_of
                - timedelta(
                    days=15
                )
            ),
            investors=[
                investor
            ],
        )

        result = (
            compare_market_activity(
                window_days=180,
                as_of=as_of,
                investor_names=[
                    "Investor A"
                ],
            )
        )

        robotics = (
            result[
                "comparison"
            ][0]
        )

        assert (
            robotics[
                "value"
            ]
            == "Robotics"
        )

        assert (
            robotics[
                "current_event_count"
            ]
            == 1
        )

        assert (
            robotics[
                "previous_event_count"
            ]
            == 0
        )

        assert (
            robotics[
                "delta"
            ]
            == 1
        )

        assert (
            robotics[
                "change_pct"
            ]
            is None
        )

        db.session.rollback()


def test_invalid_market_dimension_is_rejected(
    app,
):
    with app.app_context():
        try:
            compare_market_activity(
                dimension="stage",
            )

        except ValueError as exc:
            assert (
                "Unsupported market comparison dimension"
                in str(exc)
            )

        else:
            raise AssertionError(
                "Expected unsupported dimension to fail."
            )