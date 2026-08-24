from datetime import datetime
from types import SimpleNamespace

from models.article import Article, db
from models.company import Company
from models.funding_round import FundingRound
from models.investor import Investor

from services.entity_service import (
    save_funding_extraction,
)


def _create_article(
    *,
    title="Funding article",
    url="https://example.com/funding",
    published_at=None,
):
    article = Article(
        title=title,
        source="Test Source",
        url=url,
        published_at=(
            published_at
            or datetime(2026, 8, 10)
        ),
        summary="Test funding article",
        category="Funding Round",
    )

    db.session.add(article)
    db.session.flush()

    return article


def _extraction(**overrides):
    values = {
        "is_funding_round": True,
        "event_evidence": "Company raised funding.",
        "company_name": "Acme",
        "sector": None,
        "company_city": None,
        "company_country": None,
        "founded_year": None,
        "amount": 20_000_000,
        "currency": "USD",
        "round_type": "Series A",
        "investors": [],
        "lead_investors": [],
    }

    values.update(overrides)

    return SimpleNamespace(**values)


def test_non_funding_extraction_is_not_persisted(app):
    with app.app_context():
        article = _create_article()

        result = save_funding_extraction(
            article,
            _extraction(
                is_funding_round=False,
            ),
        )

        assert result is None
        assert Company.query.count() == 0
        assert FundingRound.query.count() == 0


def test_extraction_without_event_evidence_is_not_persisted(app):
    with app.app_context():
        article = _create_article()

        result = save_funding_extraction(
            article,
            _extraction(
                event_evidence=None,
            ),
        )

        assert result is None
        assert Company.query.count() == 0
        assert FundingRound.query.count() == 0


def test_extraction_without_company_is_not_persisted(app):
    with app.app_context():
        article = _create_article()

        result = save_funding_extraction(
            article,
            _extraction(
                company_name=None,
            ),
        )

        assert result is None
        assert Company.query.count() == 0
        assert FundingRound.query.count() == 0


def test_save_funding_extraction_creates_company_and_round(app):
    with app.app_context():
        article = _create_article()

        result = save_funding_extraction(
            article,
            _extraction(),
        )

        assert result is not None

        company = Company.query.filter_by(
            name="Acme"
        ).one()

        assert result.company_id == company.id
        assert result.amount == 20_000_000
        assert result.currency == "USD"
        assert result.round_type == "Series A"
        assert (
            result.canonical_round_type
            == "Series A"
        )
        assert (
            result.event_evidence
            == "Company raised funding."
        )
        assert (
            result.announced_at
            == article.published_at
        )
        assert result.article_id == article.id
        assert article in result.articles


def test_save_funding_extraction_enriches_company_metadata(app):
    with app.app_context():
        article = _create_article()

        save_funding_extraction(
            article,
            _extraction(
                sector="Fintech",
                company_city="London",
                company_country=(
                    "United Kingdom"
                ),
                founded_year=2021,
            ),
        )

        company = Company.query.filter_by(
            name="Acme"
        ).one()

        assert company.sector == "Fintech"
        assert company.canonical_sector is not None
        assert company.city == "London"
        assert company.country == (
            "United Kingdom"
        )
        assert company.founded_year == 2021


def test_save_funding_extraction_creates_investors(app):
    with app.app_context():
        article = _create_article()

        result = save_funding_extraction(
            article,
            _extraction(
                investors=[
                    "Investor Alpha",
                    "Investor Beta",
                ],
            ),
        )

        assert {
            investor.name
            for investor in result.investors
        } == {
            "Investor Alpha",
            "Investor Beta",
        }

        assert Investor.query.count() == 2


def test_lead_investor_is_also_participant(app):
    with app.app_context():
        article = _create_article()

        result = save_funding_extraction(
            article,
            _extraction(
                lead_investors=[
                    "Lead Capital",
                ],
            ),
        )

        participant_names = {
            investor.name
            for investor in result.investors
        }

        lead_names = {
            investor.name
            for investor
            in result.lead_investors
        }

        assert participant_names == {
            "Lead Capital",
        }

        assert lead_names == {
            "Lead Capital",
        }


def test_duplicate_investor_names_do_not_duplicate_relationship(app):
    with app.app_context():
        article = _create_article()

        result = save_funding_extraction(
            article,
            _extraction(
                investors=[
                    "Investor Alpha",
                    "Investor Alpha",
                ],
            ),
        )

        assert [
            investor.name
            for investor in result.investors
        ] == [
            "Investor Alpha",
        ]

        assert Investor.query.count() == 1


def test_existing_company_is_reused(app):
    with app.app_context():
        company = Company(
            name="Acme"
        )

        db.session.add(company)
        db.session.flush()

        original_id = company.id

        article = _create_article()

        result = save_funding_extraction(
            article,
            _extraction(),
        )

        assert Company.query.count() == 1
        assert result.company_id == original_id


def test_existing_matching_round_is_reused(app):
    with app.app_context():
        first_article = _create_article(
            title="First report",
            url=(
                "https://example.com/"
                "first-report"
            ),
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        first_round = save_funding_extraction(
            first_article,
            _extraction(),
        )

        original_round_id = first_round.id

        second_article = _create_article(
            title="Second report",
            url=(
                "https://example.com/"
                "second-report"
            ),
            published_at=datetime(
                2026,
                8,
                11,
            ),
        )

        second_result = save_funding_extraction(
            second_article,
            _extraction(),
        )

        assert (
            second_result.id
            == original_round_id
        )

        assert FundingRound.query.count() == 1

        assert first_article in (
            second_result.articles
        )

        assert second_article in (
            second_result.articles
        )


def test_existing_round_preserves_earliest_announcement_date(app):
    with app.app_context():
        later_article = _create_article(
            title="Later report",
            url="https://example.com/later",
            published_at=datetime(
                2026,
                8,
                15,
            ),
        )

        funding_round = save_funding_extraction(
            later_article,
            _extraction(),
        )

        earlier_article = _create_article(
            title="Earlier report",
            url="https://example.com/earlier",
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        result = save_funding_extraction(
            earlier_article,
            _extraction(),
        )

        assert result.id == funding_round.id

        assert result.announced_at == datetime(
            2026,
            8,
            10,
        )


def test_second_source_does_not_duplicate_supporting_article(app):
    with app.app_context():
        article = _create_article()

        first_result = save_funding_extraction(
            article,
            _extraction(),
        )

        second_result = save_funding_extraction(
            article,
            _extraction(),
        )

        assert (
            first_result.id
            == second_result.id
        )

        assert (
            second_result.articles.count(
                article
            )
            == 1
        )


def test_existing_investor_is_reused(app):
    with app.app_context():
        investor = Investor(
            name="Investor Alpha"
        )

        db.session.add(investor)
        db.session.flush()

        original_id = investor.id

        article = _create_article()

        result = save_funding_extraction(
            article,
            _extraction(
                investors=[
                    "Investor Alpha",
                ],
            ),
        )

        assert Investor.query.count() == 1

        assert (
            result.investors[0].id
            == original_id
        )
