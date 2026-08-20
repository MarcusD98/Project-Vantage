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


def test_measure_source_counts_v2_metrics(
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
        result[
            "funding_candidates"
        ]
        == 1
    )

    assert (
        result[
            "eligible_funding_candidates"
        ]
        == 1
    )

    assert (
        result[
            "processed_funding"
        ]
        == 1
    )

    assert (
        result[
            "funding_backlog"
        ]
        == 0
    )

    assert (
        result[
            "funding_processing_rate"
        ]
        == 1.0
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
            "funding_event_conversion_rate"
        ]
        == 1.0
    )

    assert (
        result[
            "unique_funding_events"
        ]
        == 1
    )

    assert (
        result[
            "multi_source_funding_events"
        ]
        == 0
    )

    assert (
        result[
            "funding_overlap_rate"
        ]
        == 0.0
    )


def test_measure_source_detects_backlog(
    app,
):
    processed = Article(
        title="Acme raises $10M",
        source="Test Publication",
        source_type="publication",
        discovery_method="rss",
        url="https://example.com/processed",
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

    unprocessed = Article(
        title="Beta raises $5M",
        source="Test Publication",
        source_type="publication",
        discovery_method="rss",
        url="https://example.com/unprocessed",
        published_at=datetime(
            2026,
            8,
            2,
        ),
        category="Funding Round",
    )

    db.session.add_all(
        [
            processed,
            unprocessed,
        ]
    )

    db.session.commit()

    source = {
        "name": "Test Publication",
        "type": "publication",
        "method": "rss",
    }

    result = measure_source(
        source
    )

    assert (
        result[
            "eligible_funding_candidates"
        ]
        == 2
    )

    assert (
        result[
            "processed_funding"
        ]
        == 1
    )

    assert (
        result[
            "funding_backlog"
        ]
        == 1
    )

    assert (
        result[
            "funding_processing_rate"
        ]
        == 0.5
    )


def test_stale_candidates_do_not_count_as_backlog(
    app,
):
    stale = Article(
        title="Old funding event",
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

    current = Article(
        title="Current funding event",
        source="Test Investor",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/current",
        published_at=datetime(
            2026,
            8,
            1,
        ),
        category="Funding Round",
    )

    db.session.add_all(
        [
            stale,
            current,
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
            "funding_candidates"
        ]
        == 2
    )

    assert (
        result[
            "stale_funding_candidates"
        ]
        == 1
    )

    assert (
        result[
            "eligible_funding_candidates"
        ]
        == 1
    )

    assert (
        result[
            "funding_backlog"
        ]
        == 1
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
        },
        {
            "name": "Test Publication",
            "type": "publication",
            "method": "rss",
        },
    ]

    results = get_source_measurements(
        sources=sources
    )

    for result in results:
        assert (
            result[
                "multi_source_funding_events"
            ]
            == 1
        )

        assert (
            result[
                "unique_funding_events"
            ]
            == 0
        )

        assert (
            result[
                "funding_overlap_rate"
            ]
            == 1.0
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
            "funding_processing_rate"
        ]
        is None
    )

    assert (
        result[
            "funding_confirmation_rate"
        ]
        is None
    )

    assert (
        result[
            "funding_event_conversion_rate"
        ]
        is None
    )

    assert (
        result[
            "funding_overlap_rate"
        ]
        is None
    )


def test_format_source_measurement_report():
    measurements = [
        {
            "name":
                "Example",

            "source_type":
                "investor",

            "stored_evidence":
                10,

            "eligible_funding_candidates":
                5,

            "processed_funding":
                4,

            "funding_backlog":
                1,

            "funding_processing_rate":
                0.8,

            "confirmed_funding_evidence":
                4,

            "funding_confirmation_rate":
                1.0,

            "supported_funding_events":
                3,

            "funding_event_conversion_rate":
                0.75,

            "unique_funding_events":
                2,

            "multi_source_funding_events":
                1,

            "funding_overlap_rate":
                1 / 3,
        }
    ]

    report = (
        format_source_measurement_report(
            measurements
        )
    )

    assert "Example" in report
    assert "80.0%" in report
    assert "100.0%" in report
    assert "75.0%" in report
    assert "33.3%" in report
    assert "Backlog" in report
    assert "Unique" in report
    assert "Overlap %" in report

def test_stale_confirmed_event_does_not_inflate_current_event_rate(
    app,
):
    current_article = Article(
        title="Current Acme funding",
        source="Test Investor",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/current-acme",
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

    stale_article = Article(
        title="Historical Beta funding",
        source="Test Investor",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/historical-beta",
        published_at=datetime(
            2025,
            1,
            1,
        ),
        category="Funding Round",
        llm_processed_at=datetime(
            2025,
            1,
            2,
        ),
        llm_is_funding_round=True,
    )

    current_company = Company(
        name="Current Acme"
    )

    historical_company = Company(
        name="Historical Beta"
    )

    db.session.add_all(
        [
            current_article,
            stale_article,
            current_company,
            historical_company,
        ]
    )

    db.session.flush()

    current_round = FundingRound(
        company=current_company,
        amount=10_000_000,
        currency="USD",
        round_type="Series A",
        announced_at=datetime(
            2026,
            8,
            1,
        ),
        article=current_article,
    )

    historical_round = FundingRound(
        company=historical_company,
        amount=5_000_000,
        currency="USD",
        round_type="Seed",
        announced_at=datetime(
            2025,
            1,
            1,
        ),
        article=stale_article,
    )

    current_round.articles.append(
        current_article
    )

    historical_round.articles.append(
        stale_article
    )

    db.session.add_all(
        [
            current_round,
            historical_round,
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
            "eligible_funding_candidates"
        ]
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
            "supported_funding_events"
        ]
        == 1
    )

    assert (
        result[
            "funding_event_conversion_rate"
        ]
        == 1.0
    )

def test_compound_funding_evidence_is_not_eligible_backlog(
    app,
):
    article = Article(
        title=(
            "The Week's 10 Biggest Funding Rounds: "
            "AI, Fintech And Defense"
        ),
        source="Test Publication",
        source_type="publication",
        discovery_method="rss",
        url="https://example.com/roundup",
        published_at=datetime(
            2026,
            8,
            20,
        ),
        category="Funding Round",
    )

    db.session.add(
        article
    )

    db.session.commit()

    source = {
        "name": "Test Publication",
        "type": "publication",
        "method": "rss",
    }

    result = measure_source(
        source
    )

    assert (
        result[
            "funding_candidates"
        ]
        == 1
    )

    assert (
        result[
            "compound_funding_candidates"
        ]
        == 1
    )

    assert (
        result[
            "eligible_funding_candidates"
        ]
        == 0
    )

    assert (
        result[
            "funding_backlog"
        ]
        == 0
    )