from models.article import Article

from services.compound_evidence_service import (
    get_compound_funding_reasons,
    get_multi_round_review_reasons,
    is_compound_funding_evidence,
)


def _article(
    title,
    category="Funding Round",
    content=None,
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
        content=content,
    )


def test_detects_biggest_funding_rounds_as_blocking():
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

    assert (
        get_compound_funding_reasons(
            article
        )
        == ["collection"]
    )


def test_detects_funding_roundup_as_blocking():
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


def test_detects_plural_startup_retrospective_as_blocking():
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


def test_explicit_three_rounds_is_review_only_not_blocking():
    article = _article(
        "Partnering with Eon",
        content=(
            "Eon announced three funding rounds as it built "
            "its cloud backup platform."
        ),
    )

    assert (
        is_compound_funding_evidence(
            article
        )
        is False
    )

    assert (
        "explicit_multiple_rounds"
        in get_multi_round_review_reasons(
            article
        )
    )


def test_seed_and_series_a_is_review_only_not_blocking():
    article = _article(
        "Our investment in Nova",
        content=(
            "Nova announced a seed round led by Accel and a "
            "Series A led by Chemistry."
        ),
    )

    assert (
        is_compound_funding_evidence(
            article
        )
        is False
    )

    assert (
        "multiple_financing_stages"
        in get_multi_round_review_reasons(
            article
        )
    )


def test_current_series_c_with_prior_series_b_is_not_blocked():
    article = _article(
        "Acme raises $100M Series C",
        content=(
            "Acme raised a new $100 million Series C led by "
            "Index. The company previously raised a Series B "
            "last year."
        ),
    )

    assert (
        is_compound_funding_evidence(
            article
        )
        is False
    )


def test_normal_single_round_has_no_review_signal():
    article = _article(
        "Acme raises $40M Series B led by Index Ventures",
        content=(
            "Acme raised a $40 million Series B led by Index."
        ),
    )

    assert (
        get_multi_round_review_reasons(
            article
        )
        == []
    )


def test_non_funding_category_is_not_blocked_or_reviewed():
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

    assert (
        get_multi_round_review_reasons(
            article
        )
        == []
    )