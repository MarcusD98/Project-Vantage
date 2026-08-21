from datetime import (
    datetime,
    timedelta,
)

from types import SimpleNamespace

from models.article import (
    Article,
    db,
)

from models.funding_round import (
    FundingRound,
)

from services.entity_service import (
    save_funding_extraction,
)


def _create_article(
    *,
    title,
    source,
    url,
    published_at,
):
    article = Article(
        title=title,
        source=source,
        source_type="investor",
        discovery_method="html",
        url=url,
        published_at=published_at,
        summary="Funding evidence.",
        content="Funding evidence.",
        category="Funding Round",
    )

    db.session.add(
        article
    )

    db.session.flush()

    return article


def _funding_extraction(
    *,
    company_name="Idempotency Labs",
    amount=20_000_000,
    currency="USD",
    round_type="Series A",
):
    return SimpleNamespace(
        is_funding_round=True,
        event_evidence=(
            "Idempotency Labs announced "
            "a financing round."
        ),
        company_name=company_name,
        sector=None,
        company_city=None,
        company_country=None,
        founded_year=None,
        amount=amount,
        currency=currency,
        round_type=round_type,
        investors=[],
        lead_investors=[],
    )


def test_replaying_same_evidence_does_not_duplicate_round(
    app,
):
    with app.app_context():
        article = _create_article(
            title="Idempotency Labs raises",
            source="Test Investor",
            url=(
                "https://example.com/"
                "idempotency-replay"
            ),
            published_at=datetime(
                2026,
                8,
                10,
            ),
        )

        extraction = (
            _funding_extraction()
        )

        first = save_funding_extraction(
            article,
            extraction,
        )

        db.session.flush()

        second = save_funding_extraction(
            article,
            extraction,
        )

        db.session.flush()

        assert (
            FundingRound.query.count()
            == 1
        )

        assert (
            first.id
            == second.id
        )

        funding_round = (
            FundingRound.query.one()
        )

        assert (
            len(
                funding_round.articles
            )
            == 1
        )

        assert (
            funding_round.articles[0].id
            == article.id
        )

        db.session.rollback()


def test_two_sources_attach_to_one_canonical_round(
    app,
):
    with app.app_context():
        announced_at = datetime(
            2026,
            8,
            10,
        )

        investor_article = (
            _create_article(
                title=(
                    "Investor announces "
                    "Idempotency Labs round"
                ),
                source="Test Investor",
                url=(
                    "https://example.com/"
                    "idempotency-investor"
                ),
                published_at=announced_at,
            )
        )

        publication_article = (
            _create_article(
                title=(
                    "Publication covers "
                    "Idempotency Labs round"
                ),
                source="Test Publication",
                url=(
                    "https://example.com/"
                    "idempotency-publication"
                ),
                published_at=(
                    announced_at
                    + timedelta(
                        days=1
                    )
                ),
            )
        )

        complete_extraction = (
            _funding_extraction(
                amount=20_000_000,
                currency="USD",
                round_type="Series A",
            )
        )

        sparse_extraction = (
            _funding_extraction(
                amount=None,
                currency=None,
                round_type="Series A",
            )
        )

        first = save_funding_extraction(
            investor_article,
            complete_extraction,
        )

        db.session.flush()

        second = save_funding_extraction(
            publication_article,
            sparse_extraction,
        )

        db.session.flush()

        assert (
            FundingRound.query.count()
            == 1
        )

        assert (
            first.id
            == second.id
        )

        funding_round = (
            FundingRound.query.one()
        )

        evidence_ids = {
            article.id
            for article
            in funding_round.articles
        }

        assert evidence_ids == {
            investor_article.id,
            publication_article.id,
        }

        assert (
            funding_round.amount
            == 20_000_000
        )

        assert (
            funding_round.currency
            == "USD"
        )

        assert (
            funding_round.announced_at
            == announced_at
        )

        db.session.rollback()


def test_uncertain_sparse_events_are_not_unsafely_merged(
    app,
):
    with app.app_context():
        first_article = (
            _create_article(
                title="First uncertain event",
                source="Test Investor",
                url=(
                    "https://example.com/"
                    "uncertain-one"
                ),
                published_at=datetime(
                    2026,
                    8,
                    10,
                ),
            )
        )

        second_article = (
            _create_article(
                title="Second uncertain event",
                source="Test Publication",
                url=(
                    "https://example.com/"
                    "uncertain-two"
                ),
                published_at=datetime(
                    2026,
                    8,
                    11,
                ),
            )
        )

        extraction = (
            _funding_extraction(
                company_name=(
                    "Uncertain Events Labs"
                ),
                amount=None,
                currency=None,
                round_type=None,
            )
        )

        first = save_funding_extraction(
            first_article,
            extraction,
        )

        db.session.flush()

        second = save_funding_extraction(
            second_article,
            extraction,
        )

        db.session.flush()

        assert (
            FundingRound.query.count()
            == 2
        )

        assert (
            first.id
            != second.id
        )

        db.session.rollback()