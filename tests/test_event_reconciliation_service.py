from datetime import datetime

from models.article import db, Article
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound

from services.event_reconciliation_service import (
    merge_funding_rounds,
    reconcile_funding_round_pair,
    select_canonical_round,
)


def _create_company(name="Test Company"):
    company = Company(
        name=name
    )

    db.session.add(company)
    db.session.flush()

    return company


def _create_article(
    *,
    title,
    url,
    published_at,
):
    article = Article(
        title=title,
        source="Test Source",
        url=url,
        published_at=published_at,
        summary="Test article",
        category="Funding Round",
    )

    db.session.add(article)
    db.session.flush()

    return article


def _create_round(
    *,
    company,
    article,
    amount=20_000_000,
    currency="USD",
    round_type="Series A",
    announced_at=None,
):
    funding_round = FundingRound(
        company=company,
        article=article,
        amount=amount,
        currency=currency,
        round_type=round_type,
        canonical_round_type=round_type,
        announced_at=announced_at,
        event_evidence="Funding event evidence.",
    )

    funding_round.articles.append(
        article
    )

    db.session.add(
        funding_round
    )

    db.session.flush()

    return funding_round


def test_selects_earlier_round_as_canonical(app):
    with app.app_context():
        company = _create_company()

        article_a = _create_article(
            title="Round A",
            url="https://example.com/reconcile-a",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Round B",
            url="https://example.com/reconcile-b",
            published_at=datetime(
                2026,
                8,
                12,
            ),
        )

        round_a = _create_round(
            company=company,
            article=article_a,
            announced_at=article_a.published_at,
        )

        round_b = _create_round(
            company=company,
            article=article_b,
            announced_at=article_b.published_at,
        )

        assert (
            select_canonical_round(
                round_a,
                round_b,
            )
            is round_a
        )

        db.session.rollback()


def test_reconciliation_preserves_both_articles(app):
    with app.app_context():
        company = _create_company()

        article_a = _create_article(
            title="Round A",
            url="https://example.com/articles-a",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Round B",
            url="https://example.com/articles-b",
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        round_a = _create_round(
            company=company,
            article=article_a,
            announced_at=article_a.published_at,
        )

        round_b = _create_round(
            company=company,
            article=article_b,
            announced_at=article_b.published_at,
        )

        result = reconcile_funding_round_pair(
            round_a,
            round_b,
        )

        assert result is round_a

        assert len(
            result.articles
        ) == 2

        assert article_a in result.articles
        assert article_b in result.articles

        db.session.rollback()


def test_reconciliation_preserves_investors(app):
    with app.app_context():
        company = _create_company()

        investor_a = Investor(
            name="Investor A"
        )

        investor_b = Investor(
            name="Investor B"
        )

        db.session.add_all(
            [
                investor_a,
                investor_b,
            ]
        )

        article_a = _create_article(
            title="Investor Round A",
            url="https://example.com/investors-a",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Investor Round B",
            url="https://example.com/investors-b",
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        round_a = _create_round(
            company=company,
            article=article_a,
            announced_at=article_a.published_at,
        )

        round_b = _create_round(
            company=company,
            article=article_b,
            announced_at=article_b.published_at,
        )

        round_a.investors.append(
            investor_a
        )

        round_b.investors.append(
            investor_b
        )

        result = reconcile_funding_round_pair(
            round_a,
            round_b,
        )

        assert investor_a in result.investors
        assert investor_b in result.investors

        db.session.rollback()


def test_reconciliation_preserves_lead_investors(app):
    with app.app_context():
        company = _create_company()

        lead_investor = Investor(
            name="Lead Investor"
        )

        db.session.add(
            lead_investor
        )

        article_a = _create_article(
            title="Lead Round A",
            url="https://example.com/leads-a",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Lead Round B",
            url="https://example.com/leads-b",
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        round_a = _create_round(
            company=company,
            article=article_a,
            announced_at=article_a.published_at,
        )

        round_b = _create_round(
            company=company,
            article=article_b,
            announced_at=article_b.published_at,
        )

        round_b.lead_investors.append(
            lead_investor
        )

        result = reconcile_funding_round_pair(
            round_a,
            round_b,
        )

        assert (
            lead_investor
            in result.lead_investors
        )

        assert (
            lead_investor
            in result.investors
        )

        db.session.rollback()


def test_non_matching_rounds_are_not_reconciled(app):
    with app.app_context():
        company = _create_company()

        article_a = _create_article(
            title="Series A",
            url="https://example.com/nonmatch-a",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Series B",
            url="https://example.com/nonmatch-b",
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        round_a = _create_round(
            company=company,
            article=article_a,
            amount=20_000_000,
            round_type="Series A",
            announced_at=article_a.published_at,
        )

        round_b = _create_round(
            company=company,
            article=article_b,
            amount=50_000_000,
            round_type="Series B",
            announced_at=article_b.published_at,
        )

        result = reconcile_funding_round_pair(
            round_a,
            round_b,
        )

        assert result is None

        assert (
            FundingRound.query.filter_by(
                company_id=company.id
            ).count()
            == 2
        )

        db.session.rollback()


def test_source_round_is_deleted_after_merge(app):
    with app.app_context():
        company = _create_company()

        article_a = _create_article(
            title="Delete A",
            url="https://example.com/delete-a",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Delete B",
            url="https://example.com/delete-b",
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        round_a = _create_round(
            company=company,
            article=article_a,
            announced_at=article_a.published_at,
        )

        round_b = _create_round(
            company=company,
            article=article_b,
            announced_at=article_b.published_at,
        )

        source_id = round_b.id

        result = merge_funding_rounds(
            source_round=round_b,
            target_round=round_a,
            require_match=True,
        )

        assert result is round_a

        assert (
            db.session.get(
                FundingRound,
                source_id,
            )
            is None
        )

        db.session.rollback()