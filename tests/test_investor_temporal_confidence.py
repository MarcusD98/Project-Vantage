from datetime import datetime

from models.article import (
    Article,
    db,
)
from models.company import Company
from models.funding_round import FundingRound
from models.investor import Investor
from models.source_run import SourceRun

from services.investor_confidence_service import (
    get_investor_profile,
    get_investor_rankings,
)

from services.investor_temporal_coverage_service import (
    get_temporal_corpus_coverage,
)

from source_registry import (
    get_discovery_config,
)


AS_OF = datetime(
    2026,
    8,
    20,
    12,
    0,
    0,
)

CURRENT_START = datetime(
    2026,
    5,
    22,
    12,
    0,
    0,
)

PREVIOUS_START = datetime(
    2026,
    2,
    21,
    12,
    0,
    0,
)


def _investor(name):
    investor = Investor(
        name=name
    )

    db.session.add(
        investor
    )

    db.session.flush()

    return investor


def _round(
    investor,
    company_name,
    announced_at,
):
    company = Company(
        name=company_name,
        canonical_sector="Software",
        country="United States",
    )

    db.session.add(
        company
    )

    db.session.flush()

    funding_round = FundingRound(
        company=company,
        announced_at=announced_at,
        canonical_round_type="Series A",
    )

    funding_round.investors.append(
        investor
    )

    db.session.add(
        funding_round
    )

    db.session.flush()

    return funding_round


def _article(
    source,
    slug,
    published_at,
    processed=True,
):
    article = Article(
        title=(
            f"{slug} funding announcement"
        ),
        source=source,
        source_type="investor",
        discovery_method="sitemap",
        url=(
            f"https://example.com/{slug}"
        ),
        published_at=published_at,
        content=(
            "The company announced a financing round."
        ),
        category="Funding Round",
    )

    if processed:
        article.llm_processed_at = datetime(
            2026,
            8,
            20,
            10,
            0,
            0,
        )

    db.session.add(
        article
    )

    db.session.flush()

    return article


def _historical_run(
    source_name="Accel",
    source_key="accel",
    remaining_undated=0,
    articles_discovered=250,
):
    source_run = SourceRun(
        source_key=source_key,
        source_name=source_name,
        source_type="investor",
        mode="historical",
        process_enabled=False,
        status="success",
        started_at=datetime(
            2026,
            8,
            20,
            8,
            0,
            0,
        ),
        finished_at=datetime(
            2026,
            8,
            20,
            8,
            10,
            0,
        ),
        articles_discovered=(
            articles_discovered
        ),
        articles_relevant=(
            articles_discovered
        ),
        articles_saved=(
            articles_discovered
        ),
        dates_populated=(
            articles_discovered
        ),
        remaining_undated=(
            remaining_undated
        ),
    )

    db.session.add(
        source_run
    )

    db.session.flush()

    return source_run


def _add_two_window_articles(
    source="Accel",
    previous_processed=True,
):
    _article(
        source,
        f"{source}-current-one",
        datetime(
            2026,
            8,
            1,
        ),
    )

    _article(
        source,
        f"{source}-current-two",
        datetime(
            2026,
            7,
            1,
        ),
    )

    _article(
        source,
        f"{source}-previous-one",
        datetime(
            2026,
            4,
            1,
        ),
        processed=(
            previous_processed
        ),
    )

    _article(
        source,
        f"{source}-previous-two",
        datetime(
            2026,
            3,
            1,
        ),
    )


def _add_two_window_rounds(
    investor,
):
    _round(
        investor,
        "Current One",
        datetime(
            2026,
            8,
            1,
        ),
    )

    _round(
        investor,
        "Current Two",
        datetime(
            2026,
            7,
            1,
        ),
    )

    _round(
        investor,
        "Previous One",
        datetime(
            2026,
            4,
            1,
        ),
    )

    _round(
        investor,
        "Previous Two",
        datetime(
            2026,
            3,
            1,
        ),
    )


def test_temporal_coverage_unavailable_without_first_party_source(
    app,
):
    coverage = (
        get_temporal_corpus_coverage(
            investor_name="Y Combinator",
            current_start=CURRENT_START,
            current_end=AS_OF,
            previous_start=PREVIOUS_START,
            previous_end=CURRENT_START,
        )
    )

    assert (
        coverage[
            "status"
        ]
        == "unavailable"
    )

    assert (
        coverage[
            "source_matched"
        ]
        is False
    )


def test_temporal_coverage_requires_historical_run(
    app,
):
    _add_two_window_articles()

    coverage = (
        get_temporal_corpus_coverage(
            investor_name="Accel",
            current_start=CURRENT_START,
            current_end=AS_OF,
            previous_start=PREVIOUS_START,
            previous_end=CURRENT_START,
        )
    )

    assert (
        coverage[
            "status"
        ]
        == "unavailable"
    )

    assert (
        coverage[
            "source_matched"
        ]
        is True
    )


def test_temporal_coverage_complete_when_both_windows_processed(
    app,
):
    _historical_run()
    _add_two_window_articles()

    coverage = (
        get_temporal_corpus_coverage(
            investor_name="Accel",
            current_start=CURRENT_START,
            current_end=AS_OF,
            previous_start=PREVIOUS_START,
            previous_end=CURRENT_START,
        )
    )

    assert (
        coverage[
            "status"
        ]
        == "complete"
    )

    assert (
        coverage[
            "current_window"
        ][
            "processed_candidates"
        ]
        == 2
    )

    assert (
        coverage[
            "current_window"
        ][
            "total_candidates"
        ]
        == 2
    )

    assert (
        coverage[
            "previous_window"
        ][
            "processed_candidates"
        ]
        == 2
    )

    assert (
        coverage[
            "previous_window"
        ][
            "total_candidates"
        ]
        == 2
    )


def test_temporal_coverage_incomplete_when_candidate_backlog_exists(
    app,
):
    _historical_run()

    _add_two_window_articles(
        previous_processed=False
    )

    coverage = (
        get_temporal_corpus_coverage(
            investor_name="Accel",
            current_start=CURRENT_START,
            current_end=AS_OF,
            previous_start=PREVIOUS_START,
            previous_end=CURRENT_START,
        )
    )

    assert (
        coverage[
            "status"
        ]
        == "incomplete"
    )

    assert (
        coverage[
            "previous_window"
        ][
            "backlog"
        ]
        == 1
    )


def test_confidence_is_observational_without_temporal_corpus(
    app,
):
    investor = _investor(
        "Y Combinator"
    )

    _add_two_window_rounds(
        investor
    )

    profile = (
        get_investor_profile(
            "Y Combinator",
            window_days=90,
            as_of=AS_OF,
        )
    )

    activity = profile[
        "signals"
    ][
        "activity"
    ]

    assert (
        activity[
            "status"
        ]
        == "supported"
    )

    assert (
        activity[
            "confidence"
        ]
        == "observational"
    )


def test_confidence_is_corpus_supported_with_complete_windows(
    app,
):
    investor = _investor(
        "Accel"
    )

    _add_two_window_rounds(
        investor
    )

    _historical_run()
    _add_two_window_articles()

    profile = (
        get_investor_profile(
            "Accel",
            window_days=90,
            as_of=AS_OF,
        )
    )

    activity = profile[
        "signals"
    ][
        "activity"
    ]

    assert (
        activity[
            "status"
        ]
        == "supported"
    )

    assert (
        activity[
            "confidence"
        ]
        == "corpus_supported"
    )

    rankings = (
        get_investor_rankings(
            window_days=90,
            as_of=AS_OF,
            limit=10,
        )
    )

    item = next(
        result
        for result in rankings
        if (
            result[
                "investor"
            ].name
            == "Accel"
        )
    )

    assert (
        item[
            "trend_confidence"
        ]
        == "corpus_supported"
    )


def test_index_incremental_uses_real_publication_recency_not_sitemap_age():
    config = (
        get_discovery_config(
            "Index Ventures",
            mode="incremental",
        )
    )

    assert config is not None

    assert (
        "max_age_days"
        not in config
    )

    assert (
        config[
            "max_published_age_days"
        ]
        == 180
    )

    assert (
        config[
            "max_discovery_items"
        ]
        == 100
    )