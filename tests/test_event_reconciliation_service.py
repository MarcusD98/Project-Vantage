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

def test_select_canonical_round_handles_missing_rounds(app):
    with app.app_context():
        company = _create_company()

        article = _create_article(
            title="Only Round",
            url="https://example.com/only-round",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        funding_round = _create_round(
            company=company,
            article=article,
            announced_at=article.published_at,
        )

        assert (
            select_canonical_round(
                None,
                funding_round,
            )
            is funding_round
        )

        assert (
            select_canonical_round(
                funding_round,
                None,
            )
            is funding_round
        )


def test_select_canonical_round_prefers_known_date(app):
    with app.app_context():
        company = _create_company()

        article_a = _create_article(
            title="Undated Round",
            url="https://example.com/undated-round",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Dated Round",
            url="https://example.com/dated-round",
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        round_a = _create_round(
            company=company,
            article=article_a,
            announced_at=None,
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
            is round_b
        )


def test_select_canonical_round_uses_lower_id_when_dates_equal(app):
    with app.app_context():
        company = _create_company()

        shared_date = datetime(
            2026,
            8,
            10,
        )

        article_a = _create_article(
            title="First ID",
            url="https://example.com/first-id",
            published_at=shared_date,
        )

        article_b = _create_article(
            title="Second ID",
            url="https://example.com/second-id",
            published_at=shared_date,
        )

        round_a = _create_round(
            company=company,
            article=article_a,
            announced_at=shared_date,
        )

        round_b = _create_round(
            company=company,
            article=article_b,
            announced_at=shared_date,
        )

        assert round_a.id < round_b.id

        assert (
            select_canonical_round(
                round_b,
                round_a,
            )
            is round_a
        )


def test_merge_funding_rounds_rejects_missing_inputs(app):
    with app.app_context():
        company = _create_company()

        article = _create_article(
            title="Existing Round",
            url="https://example.com/existing-round",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        funding_round = _create_round(
            company=company,
            article=article,
            announced_at=article.published_at,
        )

        assert (
            merge_funding_rounds(
                source_round=None,
                target_round=funding_round,
            )
            is None
        )

        assert (
            merge_funding_rounds(
                source_round=funding_round,
                target_round=None,
            )
            is None
        )


def test_merge_funding_round_with_itself_is_noop(app):
    with app.app_context():
        company = _create_company()

        article = _create_article(
            title="Same Round",
            url="https://example.com/same-round",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        funding_round = _create_round(
            company=company,
            article=article,
            announced_at=article.published_at,
        )

        result = merge_funding_rounds(
            source_round=funding_round,
            target_round=funding_round,
        )

        assert result is funding_round

        assert (
            db.session.get(
                FundingRound,
                funding_round.id,
            )
            is funding_round
        )


def test_merge_preserves_missing_target_metadata(app):
    with app.app_context():
        company = _create_company()

        article_a = _create_article(
            title="Target",
            url="https://example.com/metadata-target",
            published_at=datetime(
                2026,
                8,
                12,
            ),
        )

        article_b = _create_article(
            title="Source",
            url="https://example.com/metadata-source",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        target = _create_round(
            company=company,
            article=article_a,
            announced_at=article_a.published_at,
        )

        source = _create_round(
            company=company,
            article=article_b,
            amount=50_000_000,
            currency="EUR",
            round_type="Series B",
            announced_at=article_b.published_at,
        )

        target.amount = None
        target.currency = None
        target.round_type = None
        target.canonical_round_type = None
        target.event_evidence = None

        source.event_evidence = (
            "Preserved source evidence."
        )

        result = merge_funding_rounds(
            source_round=source,
            target_round=target,
            require_match=False,
        )

        assert result.amount == 50_000_000
        assert result.currency == "EUR"
        assert result.round_type == "Series B"
        assert (
            result.canonical_round_type
            == "Series B"
        )
        assert (
            result.event_evidence
            == "Preserved source evidence."
        )


def test_merge_does_not_overwrite_existing_target_metadata(app):
    with app.app_context():
        company = _create_company()

        article_a = _create_article(
            title="Canonical Target",
            url="https://example.com/canonical-target",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Duplicate Source",
            url="https://example.com/duplicate-source",
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        target = _create_round(
            company=company,
            article=article_a,
            amount=20_000_000,
            currency="USD",
            round_type="Series A",
            announced_at=article_a.published_at,
        )

        target.event_evidence = (
            "Canonical evidence."
        )

        source = _create_round(
            company=company,
            article=article_b,
            amount=50_000_000,
            currency="EUR",
            round_type="Series B",
            announced_at=article_b.published_at,
        )

        source.event_evidence = (
            "Duplicate evidence."
        )

        result = merge_funding_rounds(
            source_round=source,
            target_round=target,
            require_match=False,
        )

        assert result.amount == 20_000_000
        assert result.currency == "USD"
        assert result.round_type == "Series A"
        assert (
            result.canonical_round_type
            == "Series A"
        )
        assert (
            result.event_evidence
            == "Canonical evidence."
        )


def test_merge_preserves_earliest_announcement_date(app):
    with app.app_context():
        company = _create_company()

        later = datetime(
            2026,
            8,
            15,
        )

        earlier = datetime(
            2026,
            8,
            10,
        )

        article_a = _create_article(
            title="Later Evidence",
            url="https://example.com/later-evidence",
            published_at=later,
        )

        article_b = _create_article(
            title="Earlier Evidence",
            url="https://example.com/earlier-evidence",
            published_at=earlier,
        )

        target = _create_round(
            company=company,
            article=article_a,
            announced_at=later,
        )

        source = _create_round(
            company=company,
            article=article_b,
            announced_at=earlier,
        )

        result = merge_funding_rounds(
            source_round=source,
            target_round=target,
            require_match=False,
        )

        assert (
            result.announced_at
            == earlier
        )


def test_merge_preserves_source_primary_article_when_target_has_none(app):
    with app.app_context():
        company = _create_company()

        article_a = _create_article(
            title="Target Evidence",
            url="https://example.com/no-primary-target",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Source Primary",
            url="https://example.com/source-primary",
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        target = _create_round(
            company=company,
            article=article_a,
            announced_at=article_a.published_at,
        )

        source = _create_round(
            company=company,
            article=article_b,
            announced_at=article_b.published_at,
        )

        target.article = None

        result = merge_funding_rounds(
            source_round=source,
            target_round=target,
            require_match=False,
        )

        assert result.article is article_b
        assert article_b in result.articles


def test_merge_does_not_duplicate_shared_evidence_or_investors(app):
    with app.app_context():
        company = _create_company()

        investor = Investor(
            name="Shared Investor"
        )

        db.session.add(investor)

        article_a = _create_article(
            title="Shared Evidence",
            url="https://example.com/shared-evidence",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        article_b = _create_article(
            title="Source Evidence",
            url="https://example.com/source-evidence",
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        target = _create_round(
            company=company,
            article=article_a,
            announced_at=article_a.published_at,
        )

        source = _create_round(
            company=company,
            article=article_b,
            announced_at=article_b.published_at,
        )

        target.investors.append(investor)
        source.investors.append(investor)

        source.articles.append(article_a)

        result = merge_funding_rounds(
            source_round=source,
            target_round=target,
            require_match=False,
        )

        assert (
            result.investors.count(
                investor
            )
            == 1
        )

        assert (
            result.articles.count(
                article_a
            )
            == 1
        )
