from datetime import datetime, timedelta
from types import SimpleNamespace

from models.article import db, Article
from models.investor import Investor
from models.fund import Fund
from models.fund_close import FundClose

from services.fund_event_resolution_service import (
    close_types_compatible,
    fund_close_events_match,
    find_matching_fund_close,
)

from services.fund_service import (
    save_fund_close_extraction,
)


def test_close_types_compatible_with_unknown():
    assert close_types_compatible(
        "final_close",
        "unknown",
    )

    assert close_types_compatible(
        "unknown",
        "first_close",
    )


def test_close_types_reject_different_known_types():
    assert not close_types_compatible(
        "first_close",
        "final_close",
    )


def test_fund_close_events_match_same_event():
    announced_at = datetime(
        2026,
        8,
        20,
    )

    assert fund_close_events_match(
        fund_id_a=1,
        amount_a=500_000_000,
        currency_a="USD",
        close_type_a="final_close",
        announced_at_a=announced_at,

        fund_id_b=1,
        amount_b=500_000_000,
        currency_b="USD",
        close_type_b="final_close",
        announced_at_b=(
            announced_at
            + timedelta(days=2)
        ),
    )


def test_fund_close_events_reject_different_funds():
    announced_at = datetime(
        2026,
        8,
        20,
    )

    assert not fund_close_events_match(
        fund_id_a=1,
        amount_a=500_000_000,
        currency_a="USD",
        close_type_a="final_close",
        announced_at_a=announced_at,

        fund_id_b=2,
        amount_b=500_000_000,
        currency_b="USD",
        close_type_b="final_close",
        announced_at_b=announced_at,
    )


def test_fund_close_events_reject_different_amounts():
    announced_at = datetime(
        2026,
        8,
        20,
    )

    assert not fund_close_events_match(
        fund_id_a=1,
        amount_a=200_000_000,
        currency_a="USD",
        close_type_a="first_close",
        announced_at_a=announced_at,

        fund_id_b=1,
        amount_b=500_000_000,
        currency_b="USD",
        close_type_b="final_close",
        announced_at_b=announced_at,
    )


def test_find_matching_fund_close(
    app,
):
    with app.app_context():
        investor = Investor(
            name="Test Ventures"
        )

        fund = Fund(
            name="Test Fund III",
            investor=investor,
        )

        existing_close = FundClose(
            fund=fund,
            amount=500_000_000,
            currency="USD",
            close_type="final_close",
            announced_at=datetime(
                2026,
                8,
                18,
            ),
        )

        db.session.add_all(
            [
                investor,
                fund,
                existing_close,
            ]
        )

        db.session.flush()

        match = find_matching_fund_close(
            fund=fund,
            amount=500_000_000,
            currency="USD",
            close_type="final_close",
            announced_at=datetime(
                2026,
                8,
                20,
            ),
        )

        assert match is existing_close

        db.session.rollback()


def test_fund_close_multi_source_evidence(
    app,
):
    with app.app_context():
        investor = Investor(
            name="Test Ventures"
        )

        fund = Fund(
            name="Test Fund III",
            investor=investor,
        )

        article_one = Article(
            title=(
                "Test Ventures closes "
                "$500M Test Fund III"
            ),
            source="Test Publication",
            url=(
                "https://example.com/"
                "fund-close-editorial"
            ),
            published_at=datetime(
                2026,
                8,
                18,
            ),
            category="Fund News",
        )

        existing_close = FundClose(
            fund=fund,
            article=article_one,
            amount=500_000_000,
            currency="USD",
            close_type="final_close",
            announced_at=article_one.published_at,
            event_evidence=(
                "Test Ventures closed "
                "Test Fund III at $500M."
            ),
        )

        existing_close.articles.append(
            article_one
        )

        db.session.add_all(
            [
                investor,
                fund,
                article_one,
                existing_close,
            ]
        )

        db.session.flush()

        article_two = Article(
            title="Introducing Test Fund III",
            source="Test Ventures",
            url=(
                "https://example.com/"
                "fund-close-investor"
            ),
            published_at=datetime(
                2026,
                8,
                20,
            ),
            category="Fund News",
        )

        db.session.add(
            article_two
        )

        db.session.flush()

        extraction = SimpleNamespace(
            is_fund_close=True,
            event_evidence=(
                "Test Ventures announced "
                "the $500M final close of "
                "Test Fund III."
            ),
            investor_name="Test Ventures",
            fund_name="Test Fund III",
            amount=500_000_000,
            currency="USD",
            close_type="final_close",
            strategy=None,
            geography=None,
            vintage_year=2026,
        )

        result = save_fund_close_extraction(
            article_two,
            extraction,
        )

        assert result.id == existing_close.id

        assert (
            FundClose.query.count()
            == 1
        )

        assert (
            article_one
            in result.articles
        )

        assert (
            article_two
            in result.articles
        )

        assert (
            len(result.articles)
            == 2
        )

        db.session.rollback()