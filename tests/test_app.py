import os


# The application must be configured for an isolated test
# database before app.py is imported.
os.environ["DATABASE_URL"] = (
    "sqlite:///:memory:"
)

from app import app
from models.article import db


def test_homepage_loads():
    """
    The homepage should respond successfully against a clean,
    empty database.

    This test must not depend on the developer's persisted
    local Vantage corpus.
    """

    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        client = app.test_client()

        response = client.get("/")

        assert (
            response.status_code
            == 200
        )

        db.session.remove()
        db.drop_all()
