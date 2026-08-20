from datetime import (
    datetime,
    timezone,
)

from models.article import (
    db,
    Article,
)

from models.company import Company

from models.funding_round import (
    FundingRound,
)

from services.source_measurement_service import (
    _article_is_known_stale,
    format_source_measurement_report,
    get_source_measurements,
    measure_source,
)


def test_known_stale_article():
    article = Article(
        title="Old investment",
        source="Test Investor",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/old",
        published_at=datetime(
            2025,
            1,
            1,
        ),
        category="Funding Round",
    )

    source = {
        "name": "Test Investor",
        "type": "investor",
        "method": "sitemap",
        "max_published_age_days": 180,
    }

    now = datetime(
        2026,
        8,
        20,
        tzinfo=timezone.utc,
    )

    assert _article_is_known_stale(
        article,
        source,
        now=now,
    )


def test_undated_article_is_not_called_stale():
    article = Article(
        title="Undated investment",
        source="Test Investor",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/undated",
        published_at=None,
        category="Funding Round",
    )

    source = {
        "name": "Test Investor",
        "type": "investor",
        "method": "sitemap",
        "max_published_age_days": 180,
    }

    now = datetime(
        2026,
        8,
        20,
        tzinfo=timezone.utc,
    )

    assert not _article_is_known_stale(
        article,
        source,
        now=now,
    )


def test_measure_source_counts_evidence_and_events(
    app,
):
    article = Article(
        title="Partnering with Acme",
        source="Test Investor",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/acme",
        published_at=datetime(
            2026,
            8,
            1,
        ),
        category="Funding Round",
        llm_processed_at=datetime(
            2026,
            8,
            2,
        ),
        llm_is_funding_round=True,
    )

    company = Company(
        name="Acme"
    )

    db.session.add_all(
        [
            article,
            company,
        ]
    )

    db.session.flush()

    funding_round = FundingRound(
        company=company,
        amount=10_000_000,
        currency="USD",
        round_type="Series A",
        announced_at=datetime(
            2026,
            8,
            1,
        ),
        article=article,
    )

    funding_round.articles.append(
        article
    )

    db.session.add(
        funding_round
    )

    db.session.commit()

    source = {
        "name": "Test Investor",
        "type": "investor",
        "method": "sitemap",
        "enabled": True,
        "max_published_age_days": 180,
    }

    result = measure_source(
        source,
        now=datetime(
            2026,
            8,
            20,
            tzinfo=timezone.utc,
        ),
    )

    assert (
        result["stored_evidence"]
        == 1
    )

    assert (
        result["funding_candidates"]
        == 1
    )

    assert (
        result[
            "stale_funding_candidates"
        ]
        == 0
    )

    assert (
        result["processed_funding"]
        == 1
    )

    assert (
        result[
            "confirmed_funding_evidence"
        ]
        == 1
    )

    assert (
        result[
            "funding_confirmation_rate"
        ]
        == 1.0
    )

    assert (
        result[
            "supported_funding_events"
        ]
        == 1
    )

    assert (
        result[
            "funding_event_yield"
        ]
        == 1.0
    )

    assert (
        result[
            "multi_source_funding_events"
        ]
        == 0
    )


def test_measure_source_detects_multi_source_event(
    app,
):
    investor_article = Article(
        title="Partnering with Acme",
        source="Test Investor",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/investor-acme",
        published_at=datetime(
            2026,
            8,
            1,
        ),
        category="Funding Round",
        llm_processed_at=datetime(
            2026,
            8,
            2,
        ),
        llm_is_funding_round=True,
    )

    publication_article = Article(
        title="Acme raises $10M Series A",
        source="Test Publication",
        source_type="publication",
        discovery_method="rss",
        url="https://example.com/publication-acme",
        published_at=datetime(
            2026,
            8,
            1,
        ),
        category="Funding Round",
        llm_processed_at=datetime(
            2026,
            8,
            2,
        ),
        llm_is_funding_round=True,
    )

    company = Company(
        name="Acme"
    )

    db.session.add_all(
        [
            investor_article,
            publication_article,
            company,
        ]
    )

    db.session.flush()

    funding_round = FundingRound(
        company=company,
        amount=10_000_000,
        currency="USD",
        round_type="Series A",
        announced_at=datetime(
            2026,
            8,
            1,
        ),
        article=investor_article,
    )

    funding_round.articles.extend(
        [
            investor_article,
            publication_article,
        ]
    )

    db.session.add(
        funding_round
    )

    db.session.commit()

    sources = [
        {
            "name": "Test Investor",
            "type": "investor",
            "method": "sitemap",
            "enabled": True,
        },
        {
            "name": "Test Publication",
            "type": "publication",
            "method": "rss",
            "enabled": True,
        },
    ]

    results = get_source_measurements(
        sources=sources
    )

    investor_result = results[0]

    publication_result = results[1]

    assert (
        investor_result[
            "multi_source_funding_events"
        ]
        == 1
    )

    assert (
        publication_result[
            "multi_source_funding_events"
        ]
        == 1
    )


def test_measure_source_separates_stale_categories(
    app,
):
    funding_article = Article(
        title="Old funding event",
        source="Test Investor",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/old-funding",
        published_at=datetime(
            2025,
            1,
            1,
        ),
        category="Funding Round",
    )

    fund_news_article = Article(
        title="Old fund announcement",
        source="Test Investor",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/old-fund",
        published_at=datetime(
            2025,
            1,
            1,
        ),
        category="Fund News",
    )

    db.session.add_all(
        [
            funding_article,
            fund_news_article,
        ]
    )

    db.session.commit()

    source = {
        "name": "Test Investor",
        "type": "investor",
        "method": "sitemap",
        "max_published_age_days": 180,
    }

    result = measure_source(
        source,
        now=datetime(
            2026,
            8,
            20,
            tzinfo=timezone.utc,
        ),
    )

    assert (
        result[
            "stale_funding_candidates"
        ]
        == 1
    )

    assert (
        result[
            "stale_fund_news_candidates"
        ]
        == 1
    )


def test_measure_source_returns_none_for_empty_ratios(
    app,
):
    source = {
        "name": "Empty Source",
        "type": "investor",
        "method": "sitemap",
    }

    result = measure_source(
        source
    )

    assert (
        result[
            "funding_confirmation_rate"
        ]
        is None
    )

    assert (
        result[
            "funding_event_yield"
        ]
        is None
    )


def test_format_source_measurement_report():
    measurements = [
        {
            "name": "Example",
            "source_type": "investor",
            "stored_evidence": 10,
            "funding_candidates": 5,
            "stale_funding_candidates": 2,
            "fund_news_candidates": 1,
            "stale_fund_news_candidates": 1,
            "processed_funding": 3,
            "confirmed_funding_evidence": 3,
            "funding_confirmation_rate": 1.0,
            "supported_funding_events": 2,
            "funding_event_yield": 0.2,
            "multi_source_funding_events": 1,
        }
    ]

    report = (
        format_source_measurement_report(
            measurements
        )
    )

    assert "Example" in report
    assert "100.0%" in report
    assert "20.0%" in report
    assert "F-Stale" in report
    assert "FN-Stale" in report