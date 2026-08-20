from models.article import db, Article
from models.investor import Investor
from models.entity_alias import EntityAlias
from models.entity_resolution_review import (
    EntityResolutionReview,
)

from services.entity_review_service import (
    approve_resolution_review,
    record_entity_resolution_review,
    reject_resolution_review,
)


def _create_article(
    url,
):
    article = Article(
        title="Test article",
        source="Test",
        url=url,
    )

    db.session.add(
        article
    )

    db.session.flush()

    return article


def test_records_review_candidate(
    app,
):
    with app.app_context():
        article = _create_article(
            "https://example.com/review-test"
        )

        investor = Investor(
            name="North Ventures"
        )

        db.session.add(
            investor
        )

        db.session.flush()

        resolution = {
            "status": "review",
            "raw_name":
                "North Venture",
            "normalized_name":
                "North Venture",
            "canonical_name":
                "North Venture",
            "entity":
                None,
            "candidate":
                investor,
            "score":
                0.74,
        }

        review = (
            record_entity_resolution_review(
                article=article,
                resolution=resolution,
                entity_type="investor",
            )
        )

        assert review is not None

        assert (
            review.raw_name
            == "North Venture"
        )

        assert (
            review.entity_type
            == "investor"
        )

        assert (
            review.similarity_score
            == 0.74
        )

        assert (
            review.candidate_investor_id
            == investor.id
        )

        assert (
            review.candidate_entity
            is investor
        )

        db.session.rollback()


def test_exact_match_does_not_create_review(
    app,
):
    with app.app_context():
        article = _create_article(
            "https://example.com/review-exact"
        )

        resolution = {
            "status": "exact",
            "raw_name":
                "Sequoia Capital",
            "normalized_name":
                "Sequoia Capital",
            "canonical_name":
                "Sequoia Capital",
            "entity":
                None,
            "candidate":
                None,
            "score":
                1.0,
        }

        review = (
            record_entity_resolution_review(
                article=article,
                resolution=resolution,
                entity_type="investor",
            )
        )

        assert review is None

        assert (
            EntityResolutionReview
            .query.count()
            == 0
        )

        db.session.rollback()


def test_approval_creates_stable_alias(
    app,
):
    with app.app_context():
        article = _create_article(
            "https://example.com/review-approve"
        )

        investor = Investor(
            name="Canonical Capital"
        )

        db.session.add(
            investor
        )

        db.session.flush()

        review = EntityResolutionReview(
            entity_type="investor",
            raw_name="Canonical Ventures",
            normalized_name=(
                "Canonical Ventures"
            ),
            candidate_name=investor.name,
            candidate_investor=investor,
            similarity_score=0.90,
            resolution_status="review",
            article=article,
        )

        db.session.add(
            review
        )

        db.session.flush()

        result = (
            approve_resolution_review(
                review.id
            )
        )

        assert result is True

        alias = EntityAlias.query.filter_by(
            alias="Canonical Ventures",
            entity_type="investor",
        ).one()

        assert (
            alias.canonical_investor_id
            == investor.id
        )

        assert (
            alias.canonical_entity
            is investor
        )

        assert (
            alias.canonical_name
            == investor.name
        )

        assert (
            review.decision
            == "approved_match"
        )

        assert (
            review.resolved_at
            is not None
        )

        db.session.rollback()


def test_rejection_does_not_create_alias(
    app,
):
    with app.app_context():
        article = _create_article(
            "https://example.com/review-reject"
        )

        investor = Investor(
            name="Rejected Capital"
        )

        db.session.add(
            investor
        )

        db.session.flush()

        review = EntityResolutionReview(
            entity_type="investor",
            raw_name="Rejected Ventures",
            normalized_name=(
                "Rejected Ventures"
            ),
            candidate_name=investor.name,
            candidate_investor=investor,
            similarity_score=0.80,
            resolution_status="review",
            article=article,
        )

        db.session.add(
            review
        )

        db.session.flush()

        result = (
            reject_resolution_review(
                review.id
            )
        )

        assert result is True

        assert (
            EntityAlias.query.filter_by(
                alias="Rejected Ventures",
                entity_type="investor",
            ).first()
            is None
        )

        assert (
            review.decision
            == "keep_separate"
        )

        assert (
            review.resolved_at
            is not None
        )

        db.session.rollback()


def test_approval_does_not_redirect_existing_alias(
    app,
):
    with app.app_context():
        article = _create_article(
            "https://example.com/review-conflict"
        )

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

        db.session.flush()

        alias = EntityAlias(
            alias="Shared Alias",
            entity_type="investor",
            canonical_name=investor_a.name,
            canonical_investor=investor_a,
        )

        review = EntityResolutionReview(
            entity_type="investor",
            raw_name="Shared Alias",
            normalized_name="Shared Alias",
            candidate_name=investor_b.name,
            candidate_investor=investor_b,
            similarity_score=0.95,
            resolution_status="review",
            article=article,
        )

        db.session.add_all(
            [
                alias,
                review,
            ]
        )

        db.session.flush()

        result = (
            approve_resolution_review(
                review.id
            )
        )

        assert result is False

        assert (
            alias.canonical_entity
            is investor_a
        )

        assert (
            review.resolved_at
            is None
        )

        db.session.rollback()