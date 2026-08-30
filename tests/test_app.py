import os


# Configure an isolated database before importing the application.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app
from models.article import db
from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound


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
        assert b"What changed?" in response.data
        assert b"Activity shifts" in response.data

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



def test_productisation_directory_surfaces_load():
    """
    Productisation V1 discovery and evidence surfaces should render
    against an empty isolated database.
    """

    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        client = app.test_client()

        evidence_response = client.get(
            "/evidence"
        )
        investors_response = client.get(
            "/investors"
        )
        companies_response = client.get(
            "/companies"
        )

        assert evidence_response.status_code == 200
        assert b"Evidence feed" in evidence_response.data

        assert investors_response.status_code == 200
        assert b"Investor profiles" in investors_response.data

        assert companies_response.status_code == 200
        assert b"Company profiles" in companies_response.data

        db.session.remove()
        db.drop_all()
        db.engine.dispose()



def test_productisation_explorer_filters():
    """
    Product discovery controls should narrow the observed corpus
    without changing canonical data.
    """

    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        alpha = Investor(
            name="Alpha Ventures",
            headquarters="London",
        )
        beta = Investor(
            name="Beta Capital",
            headquarters="New York",
        )

        acme = Company(
            name="Acme AI",
            sector="AI",
            canonical_sector="AI",
            country="United Kingdom",
        )
        biotech = Company(
            name="BioCo",
            sector="Biotech",
            canonical_sector="Biotech",
            country="United States",
        )

        acme_round = FundingRound(
            company=acme,
            round_type="Seed",
            canonical_round_type="Seed",
            currency="USD",
        )
        acme_round.investors.append(alpha)
        acme_round.lead_investors.append(alpha)

        biotech_round = FundingRound(
            company=biotech,
            round_type="Series A",
            canonical_round_type="Series A",
            currency="EUR",
        )
        biotech_round.investors.append(beta)

        db.session.add_all(
            [
                alpha,
                beta,
                acme,
                biotech,
                acme_round,
                biotech_round,
            ]
        )
        db.session.commit()

        client = app.test_client()

        investor_response = client.get(
            "/investors?activity=lead&location=London"
        )
        assert investor_response.status_code == 200
        assert b"Alpha Ventures" in investor_response.data
        assert b"Beta Capital" not in investor_response.data

        company_response = client.get(
            "/companies?sector=AI&country=United%20Kingdom"
        )
        assert company_response.status_code == 200
        assert b"Acme AI" in company_response.data
        assert b"BioCo" not in company_response.data

        funding_response = client.get(
            "/funding?q=Alpha&stage=Seed&sector=AI&currency=USD"
        )
        assert funding_response.status_code == 200
        assert b"Acme AI" in funding_response.data
        assert b"BioCo" not in funding_response.data

        db.session.remove()
        db.drop_all()
        db.engine.dispose()
