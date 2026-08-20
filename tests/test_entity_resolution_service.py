import pytest

from flask import Flask

from models.article import db
from models.company import Company
from models.investor import Investor
from models.entity_alias import EntityAlias

from services.entity_resolution_service import (
    resolve_entity_name,
)


@pytest.fixture
def test_app():
    app = Flask(__name__)

    app.config["TESTING"] = True

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "sqlite:///:memory:"

    app.config[
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    ] = False

    db.init_app(
        app
    )

    with app.app_context():
        db.create_all()

        yield app

        db.session.rollback()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def resolution_data(
    test_app,
):
    with test_app.app_context():
        andreessen = Investor(
            name="Andreessen Horowitz"
        )

        sequoia = Investor(
            name="Sequoia Capital"
        )

        quantumlight = Company(
            name="QuantumLight"
        )

        db.session.add_all(
            [
                andreessen,
                sequoia,
                quantumlight,
            ]
        )

        db.session.flush()

        alias = EntityAlias(
            alias="a16z",
            entity_type="investor",
            canonical_name=andreessen.name,
            canonical_investor=andreessen,
        )

        db.session.add(
            alias
        )

        db.session.commit()

        yield


def test_resolves_known_alias(
    test_app,
    resolution_data,
):
    with test_app.app_context():
        result = resolve_entity_name(
            "a16z",
            "investor",
        )

        assert (
            result["status"]
            == "alias"
        )

        assert (
            result["canonical_name"]
            == "Andreessen Horowitz"
        )

        assert (
            result["entity"]
            is not None
        )

        assert (
            result["entity"].name
            == "Andreessen Horowitz"
        )


def test_alias_resolution_uses_stable_reference(
    test_app,
    resolution_data,
):
    """
    Prove canonical_name is no longer authoritative.

    Even if the compatibility string becomes stale, the alias
    still resolves through its foreign-key relationship.
    """

    with test_app.app_context():
        alias = EntityAlias.query.filter_by(
            alias="a16z",
            entity_type="investor",
        ).one()

        alias.canonical_name = (
            "Stale Historical Name"
        )

        db.session.flush()

        result = resolve_entity_name(
            "a16z",
            "investor",
        )

        assert (
            result["status"]
            == "alias"
        )

        assert (
            result["entity"].name
            == "Andreessen Horowitz"
        )

        assert (
            result["canonical_name"]
            == "Andreessen Horowitz"
        )

        db.session.rollback()


def test_resolves_exact_existing_entity(
    test_app,
    resolution_data,
):
    with test_app.app_context():
        result = resolve_entity_name(
            "Sequoia Capital",
            "investor",
        )

        assert (
            result["status"]
            == "exact"
        )

        assert (
            result["canonical_name"]
            == "Sequoia Capital"
        )

        assert (
            result["entity"]
            is not None
        )


def test_resolves_exact_company(
    test_app,
    resolution_data,
):
    with test_app.app_context():
        result = resolve_entity_name(
            "QuantumLight",
            "company",
        )

        assert (
            result["status"]
            == "exact"
        )

        assert (
            result["canonical_name"]
            == "QuantumLight"
        )

        assert (
            result["entity"]
            is not None
        )


def test_new_entity_is_not_forced_into_existing_entity(
    test_app,
    resolution_data,
):
    with test_app.app_context():
        result = resolve_entity_name(
            "Completely Different Ventures",
            "investor",
        )

        assert (
            result["status"]
            in {
                "new",
                "review",
            }
        )

        assert (
            result["entity"]
            is None
        )


def test_invalid_name(
    test_app,
    resolution_data,
):
    with test_app.app_context():
        result = resolve_entity_name(
            None,
            "company",
        )

        assert (
            result["status"]
            == "invalid"
        )

        assert (
            result["entity"]
            is None
        )