from datetime import datetime
from types import SimpleNamespace

from services.event_integrity_service import (
    cross_currency_duplicate_candidate,
)


def _investor(name):
    return SimpleNamespace(
        name=name
    )


def _round(
    *,
    id,
    company_id=1,
    date=None,
    stage="Seed",
    amount=10_000_000,
    currency="USD",
    investors=None,
    leads=None,
):
    if date is None:
        date = datetime(
            2026,
            8,
            20,
        )

    if investors is None:
        investors = [
            "Investor A",
            "Investor B",
        ]

    if leads is None:
        leads = [
            "Investor A",
        ]

    return SimpleNamespace(
        id=id,
        company_id=company_id,
        company=SimpleNamespace(
            name="Example"
        ),
        announced_at=date,
        canonical_round_type=stage,
        round_type=stage,
        amount=amount,
        currency=currency,
        investors=[
            _investor(name)
            for name
            in investors
        ],
        lead_investors=[
            _investor(name)
            for name
            in leads
        ],
    )


def test_cross_currency_shared_lead_is_candidate():
    first = _round(
        id=1,
        currency="EUR",
        leads=[
            "Lead Ventures",
        ],
        investors=[
            "Lead Ventures",
        ],
    )

    second = _round(
        id=2,
        currency="USD",
        leads=[
            "Lead Ventures",
        ],
        investors=[
            "Lead Ventures",
        ],
    )

    result = (
        cross_currency_duplicate_candidate(
            first,
            second,
        )
    )

    assert result is not None

    assert (
        result["lead_overlap"]
        == ["Lead Ventures"]
    )


def test_two_shared_investors_are_candidate_without_shared_lead():
    first = _round(
        id=1,
        currency="EUR",
        investors=[
            "Investor A",
            "Investor B",
        ],
        leads=[],
    )

    second = _round(
        id=2,
        currency="USD",
        investors=[
            "Investor A",
            "Investor B",
        ],
        leads=[],
    )

    assert (
        cross_currency_duplicate_candidate(
            first,
            second,
        )
        is not None
    )


def test_same_currency_is_not_candidate():
    first = _round(
        id=1,
        currency="USD",
    )

    second = _round(
        id=2,
        currency="USD",
    )

    assert (
        cross_currency_duplicate_candidate(
            first,
            second,
        )
        is None
    )


def test_different_stage_is_not_candidate():
    first = _round(
        id=1,
        currency="EUR",
        stage="Seed",
    )

    second = _round(
        id=2,
        currency="USD",
        stage="Series A",
    )

    assert (
        cross_currency_duplicate_candidate(
            first,
            second,
        )
        is None
    )


def test_weak_syndicate_overlap_is_not_candidate():
    first = _round(
        id=1,
        currency="EUR",
        investors=[
            "Investor A",
        ],
        leads=[],
    )

    second = _round(
        id=2,
        currency="USD",
        investors=[
            "Investor A",
        ],
        leads=[],
    )

    assert (
        cross_currency_duplicate_candidate(
            first,
            second,
        )
        is None
    )


def test_distant_dates_are_not_candidate():
    first = _round(
        id=1,
        currency="EUR",
        date=datetime(
            2026,
            8,
            10,
        ),
    )

    second = _round(
        id=2,
        currency="USD",
        date=datetime(
            2026,
            8,
            20,
        ),
    )

    assert (
        cross_currency_duplicate_candidate(
            first,
            second,
        )
        is None
    )
