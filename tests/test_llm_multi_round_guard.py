from models.article import Article

from services import llm_extractor


def test_collection_guard_short_circuits_llm_call(
    monkeypatch,
):
    article = Article(
        title="Weekly Funding Roundup: biggest deals",
        source="Test",
        source_type="publication",
        discovery_method="rss",
        url="https://example.com/collection-guard",
        category="Funding Round",
        content=(
            "Several companies announced new funding."
        ),
    )

    called = {
        "value": False
    }

    def fail_parse(*args, **kwargs):
        called[
            "value"
        ] = True

        raise AssertionError(
            "LLM should not be called for blocked collections."
        )

    monkeypatch.setattr(
        llm_extractor.client.responses,
        "parse",
        fail_parse,
    )

    extraction = (
        llm_extractor.extract_funding_with_llm(
            article
        )
    )

    assert (
        called[
            "value"
        ]
        is False
    )

    assert (
        extraction.is_funding_round
        is False
    )


def test_multi_stage_review_signal_still_reaches_extractor(
    monkeypatch,
):
    article = Article(
        title="Our investment in Nova",
        source="Test",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/review-signal",
        category="Funding Round",
        content=(
            "Nova announced a seed round led by Accel and a "
            "Series A led by Chemistry."
        ),
    )

    called = {
        "value": False
    }

    class Response:
        output_parsed = (
            llm_extractor.FundingExtraction(
                is_funding_round=False
            )
        )

    def fake_parse(*args, **kwargs):
        called[
            "value"
        ] = True
        return Response()

    monkeypatch.setattr(
        llm_extractor.client.responses,
        "parse",
        fake_parse,
    )

    extraction = (
        llm_extractor.extract_funding_with_llm(
            article
        )
    )

    assert (
        called[
            "value"
        ]
        is True
    )

    assert (
        extraction.is_funding_round
        is False
    )


def test_investor_source_context_is_passed_to_extractor(
    monkeypatch,
):
    article = Article(
        title="Leading Acme's Series A",
        source="Accel",
        source_type="investor",
        discovery_method="sitemap",
        url="https://example.com/source-aware",
        category="Funding Round",
        content=(
            "We are proud to lead Acme's Series A."
        ),
    )

    captured = {}

    class Response:
        output_parsed = (
            llm_extractor.FundingExtraction(
                is_funding_round=True,
                company_name="Acme",
                event_evidence=(
                    "Acme raised a Series A."
                ),
            )
        )

    def fake_parse(*args, **kwargs):
        captured.update(
            kwargs
        )
        return Response()

    monkeypatch.setattr(
        llm_extractor.client.responses,
        "parse",
        fake_parse,
    )

    extraction = (
        llm_extractor.extract_funding_with_llm(
            article
        )
    )

    assert (
        extraction.is_funding_round
        is True
    )

    messages = captured[
        "input"
    ]

    developer_text = (
        messages[0][
            "content"
        ]
    )

    user_text = (
        messages[1][
            "content"
        ]
    )

    assert (
        "SOURCE-PERSPECTIVE RULE"
        in developer_text
    )

    assert (
        "article authors"
        in developer_text
    )

    assert (
        "SOURCE NAME:\nAccel"
        in user_text
    )

    assert (
        "SOURCE TYPE:\ninvestor"
        in user_text
    )