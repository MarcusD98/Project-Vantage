import pytest

from flask import Flask

from models.article import db, Article
from models.entity_resolution_review import EntityResolutionReview

from services.entity_review_service import (
    record_entity_resolution_review,
)


@pytest.fixture
def test_app():
    app = Flask(__name__)

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()

def test_records_review_candidate(test_app):
    with test_app.app_context():
        article = Article(
            title="Test article",
            source="Test",
            url="https://example.com/test",
        )

        db.session.add(article)
        db.session.flush()

        resolution = {
            "status": "review",
            "raw_name": "North Venture",
            "normalized_name": "North Venture",
            "canonical_name": "North Venture",
            "entity": None,
            "candidate": None,
            "score": 0.74,
        }

        review = record_entity_resolution_review(
            article=article,
            resolution=resolution,
            entity_type="investor",
        )

        db.session.commit()

        assert review is not None
        assert review.raw_name == "North Venture"
        assert review.entity_type == "investor"
        assert review.similarity_score == 0.74

def test_exact_match_does_not_create_review(test_app):
    with test_app.app_context():
        article = Article(
            title="Test article",
            source="Test",
            url="https://example.com/test-2",
        )

        db.session.add(article)
        db.session.flush()

        resolution = {
            "status": "exact",
            "raw_name": "Sequoia Capital",
            "normalized_name": "Sequoia Capital",
            "canonical_name": "Sequoia Capital",
            "entity": None,
            "candidate": None,
            "score": 1.0,
        }

        review = record_entity_resolution_review(
            article=article,
            resolution=resolution,
            entity_type="investor",
        )

        assert review is None

        assert (
            EntityResolutionReview.query.count()
            == 0
        )