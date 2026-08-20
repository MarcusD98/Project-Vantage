from models.article import Article

from services.compound_evidence_service import (
    is_compound_funding_evidence,
)


def _article(
    title,
    category="Funding Round",
):
    return Article(
        title=title,
        source="Test",
        source_type="publication",
        discovery_method="rss",
        url=(
            "https://example.com/"
            + str(
                abs(
                    hash(title)
                )
            )
        ),
        category=category,
    )


def test_detects_biggest_funding_rounds():
    article = _article(
        "The Week’s 10 Biggest Funding Rounds: "
        "Data, Neolab, AI Infrastructure"
    )

    assert (
        is_compound_funding_evidence(
            article
        )
        is True
    )


def test_detects_funding_roundup():
    article = _article(
        "Weekly Funding Roundup: "
        "The biggest deals this week"
    )

    assert (
        is_compound_funding_evidence(
            article
        )
        is True
    )


def test_detects_plural_startup_retrospective():
    article = _article(
        "These Kenyan startups raised "
        "$500 million before shutting down"
    )

    assert (
        is_compound_funding_evidence(
            article
        )
        is True
    )


def test_does_not_block_normal_single_round():
    article = _article(
        "Acme raises $40M Series B "
        "led by Index Ventures"
    )

    assert (
        is_compound_funding_evidence(
            article
        )
        is False
    )


def test_does_not_block_single_round_with_week_word():
    article = _article(
        "Acme raises $20M one week "
        "after launching"
    )

    assert (
        is_compound_funding_evidence(
            article
        )
        is False
    )


def test_non_funding_category_is_not_blocked():
    article = _article(
        "The week’s 10 biggest funding rounds",
        category="Other",
    )

    assert (
        is_compound_funding_evidence(
            article
        )
        is False
    )