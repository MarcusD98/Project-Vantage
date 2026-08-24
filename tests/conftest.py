import pytest

from flask import Flask

from models.article import db


@pytest.fixture
def app():
    """
    Provide an isolated Flask application and in-memory
    database for database-backed tests.

    Database sessions and pooled connections are explicitly
    closed during teardown so tests do not leak SQLite
    resources between runs.
    """

    test_app = Flask(__name__)

    test_app.config["TESTING"] = True
    test_app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "sqlite:///:memory:"
    test_app.config[
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    ] = False

    db.init_app(
        test_app
    )

    with test_app.app_context():
        db.create_all()

        yield test_app

        db.session.rollback()
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
