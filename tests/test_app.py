import os


# Configure an isolated database before importing the application.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app
from models.article import db


def test_homepage_loads():
    """
    The homepage should load successfully against a clean,
    empty database and must not depend on the developer's
    persisted local Vantage corpus.
    """

    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        client = app.test_client()
        response = client.get("/")

        assert response.status_code == 200

        db.session.remove()
        db.drop_all()
        db.engine.dispose()


def test_intelligence_page_loads():
    """
    The product intelligence surface should render successfully
    against a clean database without requiring the developer's
    persisted corpus.
    """

    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        client = app.test_client()
        response = client.get(
            "/intelligence"
        )

        assert response.status_code == 200
        assert b"What changed?" in response.data
        assert b"Activity shifts" in response.data
        assert b"Sector momentum" in response.data

        db.session.remove()
        db.drop_all()
        db.engine.dispose()
