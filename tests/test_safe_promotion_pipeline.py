from pydantic import (
    BaseModel,
    Field,
)

from models.article import (
    Article,
    db,
)

from models.extraction_record import (
    ExtractionRecord,
    VALIDATION_STATE_PROMOTE,
    VALIDATION_STATE_REVIEW,
    VALIDATION_STATE_REJECT,
)

from services.intelligence_pipeline import (
    _process_funding_article,
    _process_fund_news_article,
)


class _FundingExtraction(BaseModel):
    is_funding_round: bool

    event_evidence: str | None = None
    company_name: str | None = None

    amount: float | None = None
    currency: str | None = None
    round_type: str | None = None

    investors: list[str] = Field(
        default_factory=list
    )

    lead_investors: list[str] = Field(
        default_factory=list
    )


class _FundCloseExtraction(BaseModel):
    is_fund_close: bool

    event_evidence: str | None = None

    investor_name: str | None = None
    fund_name: str | None = None

    amount: float | None = None
    currency: str | None = None

    close_type: str | None = None

    strategy: str | None = None
    geography: str | None = None
    vintage_year: int | None = None


def _make_article(
    *,
    title,
    category,
):
    return Article(
        title=title,
        source="Example Source",
        source_type="publication",
        discovery_method="rss",
        url=(
            "https://example.com/"
            + title
            .lower()
            .replace(
                " ",
                "-",
            )
            .replace(
                "$",
                "",
            )
        ),
        content=(
            "Structured test evidence "
            "for the focal event."
        ),
        category=category,
    )


def _persist_article(
    article,
):
    db.session.add(
        article
    )

    db.session.commit()

    return article


def _stats():
    return {
        "content_retrieved": 0,
        "content_failed": 0,
        "funding_processed": 0,
        "funding_rounds": 0,
        "fund_news_processed": 0,
        "fund_closes": 0,
        "processing_failed": 0,
    }


def _valid_funding_extraction():
    return _FundingExtraction(
        is_funding_round=True,
        event_evidence=(
            "Example raised a $12 million "
            "Series A."
        ),
        company_name="Example",
        amount=12_000_000,
        currency="USD",
        round_type="Series A",
        investors=[
            "Test Ventures",
        ],
        lead_investors=[
            "Test Ventures",
        ],
    )


def _review_funding_extraction():
    return _FundingExtraction(
        is_funding_round=True,
        event_evidence=(
            "An apparent financing event "
            "was reported."
        ),
        company_name=None,
        amount=12_000_000,
        currency="USD",
        round_type="Series A",
        investors=[
            "Test Ventures",
        ],
        lead_investors=[
            "Test Ventures",
        ],
    )


def _rejected_funding_extraction():
    return _FundingExtraction(
        is_funding_round=False,
        event_evidence=None,
        company_name=None,
        amount=None,
        currency=None,
        round_type=None,
        investors=[],
        lead_investors=[],
    )


def _valid_fund_close_extraction():
    return _FundCloseExtraction(
        is_fund_close=True,
        event_evidence=(
            "Test Ventures closed "
            "Test Fund III."
        ),
        investor_name="Test Ventures",
        fund_name="Test Fund III",
        amount=300_000_000,
        currency="USD",
        close_type="final_close",
        strategy="Early Stage",
        geography="Europe",
        vintage_year=2026,
    )


def _review_fund_close_extraction():
    return _FundCloseExtraction(
        is_fund_close=True,
        event_evidence=(
            "Test Ventures announced "
            "a new fund."
        ),
        investor_name="Test Ventures",
        fund_name=None,
        amount=300_000_000,
        currency="USD",
        close_type="final_close",
        strategy="Early Stage",
        geography="Europe",
        vintage_year=2026,
    )


def test_review_funding_record_never_reaches_canonicalization(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Review funding example",
                category="Funding Round",
            )
        )

        called = {
            "canonicalized": False,
        }

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "extract_funding_with_llm"
            ),
            lambda article: (
                _review_funding_extraction()
            ),
        )

        def _should_not_run(
            article,
            extraction,
        ):
            called[
                "canonicalized"
            ] = True

            raise AssertionError(
                "REVIEW extraction reached "
                "canonicalization."
            )

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "save_funding_extraction"
            ),
            _should_not_run,
        )

        stats = _stats()

        _process_funding_article(
            article,
            stats,
        )

        record = (
            ExtractionRecord.query.one()
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REVIEW
        )

        assert (
            record.promoted_at
            is None
        )

        assert (
            called["canonicalized"]
            is False
        )

        assert (
            article.llm_processed_at
            is not None
        )

        assert (
            article.llm_is_funding_round
            is True
        )

        assert (
            stats["funding_processed"]
            == 1
        )

        assert (
            stats["funding_rounds"]
            == 0
        )

        assert (
            stats["processing_failed"]
            == 0
        )


def test_rejected_funding_record_never_reaches_canonicalization(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Rejected funding example",
                category="Funding Round",
            )
        )

        called = {
            "canonicalized": False,
        }

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "extract_funding_with_llm"
            ),
            lambda article: (
                _rejected_funding_extraction()
            ),
        )

        def _should_not_run(
            article,
            extraction,
        ):
            called[
                "canonicalized"
            ] = True

            raise AssertionError(
                "REJECT extraction reached "
                "canonicalization."
            )

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "save_funding_extraction"
            ),
            _should_not_run,
        )

        stats = _stats()

        _process_funding_article(
            article,
            stats,
        )

        record = (
            ExtractionRecord.query.one()
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REJECT
        )

        assert (
            record.promoted_at
            is None
        )

        assert (
            called["canonicalized"]
            is False
        )

        assert (
            article.llm_processed_at
            is not None
        )

        assert (
            article.llm_is_funding_round
            is False
        )

        assert (
            stats["funding_processed"]
            == 1
        )

        assert (
            stats["funding_rounds"]
            == 0
        )


def test_promote_funding_record_reaches_canonicalization(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Promoted funding example",
                category="Funding Round",
            )
        )

        called = {
            "canonicalized": False,
        }

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "extract_funding_with_llm"
            ),
            lambda article: (
                _valid_funding_extraction()
            ),
        )

        def _canonicalize(
            article,
            extraction,
        ):
            called[
                "canonicalized"
            ] = True

            return object()

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "save_funding_extraction"
            ),
            _canonicalize,
        )

        stats = _stats()

        _process_funding_article(
            article,
            stats,
        )

        record = (
            ExtractionRecord.query.one()
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_PROMOTE
        )

        assert (
            record.promoted_at
            is not None
        )

        assert (
            called["canonicalized"]
            is True
        )

        assert (
            stats["funding_processed"]
            == 1
        )

        assert (
            stats["funding_rounds"]
            == 1
        )

        assert (
            stats["processing_failed"]
            == 0
        )


def test_failed_funding_promotion_remains_retryable(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Failed promotion example",
                category="Funding Round",
            )
        )

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "extract_funding_with_llm"
            ),
            lambda article: (
                _valid_funding_extraction()
            ),
        )

        def _fail_promotion(
            article,
            extraction,
        ):
            raise RuntimeError(
                "Canonical persistence failed."
            )

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "save_funding_extraction"
            ),
            _fail_promotion,
        )

        stats = _stats()

        _process_funding_article(
            article,
            stats,
        )

        # The extraction + validation transaction was committed
        # before promotion began, so it survives the rollback.
        record = (
            ExtractionRecord.query.one()
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_PROMOTE
        )

        assert (
            record.promoted_at
            is None
        )

        assert (
            article.llm_processed_at
            is not None
        )

        assert (
            stats["funding_processed"]
            == 1
        )

        assert (
            stats["funding_rounds"]
            == 0
        )

        assert (
            stats["processing_failed"]
            == 1
        )


def test_review_fund_close_never_reaches_canonicalization(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Review fund close example",
                category="Fund News",
            )
        )

        called = {
            "canonicalized": False,
        }

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "extract_fund_close_with_llm"
            ),
            lambda article: (
                _review_fund_close_extraction()
            ),
        )

        def _should_not_run(
            article,
            extraction,
        ):
            called[
                "canonicalized"
            ] = True

            raise AssertionError(
                "REVIEW fund close reached "
                "canonicalization."
            )

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "save_fund_close_extraction"
            ),
            _should_not_run,
        )

        stats = _stats()

        _process_fund_news_article(
            article,
            stats,
        )

        record = (
            ExtractionRecord.query.one()
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REVIEW
        )

        assert (
            record.promoted_at
            is None
        )

        assert (
            called["canonicalized"]
            is False
        )

        assert (
            stats["fund_news_processed"]
            == 1
        )

        assert (
            stats["fund_closes"]
            == 0
        )


def test_promote_fund_close_reaches_canonicalization(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Promoted fund close example",
                category="Fund News",
            )
        )

        called = {
            "canonicalized": False,
        }

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "extract_fund_close_with_llm"
            ),
            lambda article: (
                _valid_fund_close_extraction()
            ),
        )

        def _canonicalize(
            article,
            extraction,
        ):
            called[
                "canonicalized"
            ] = True

            return object()

        monkeypatch.setattr(
            (
                "services.intelligence_pipeline."
                "save_fund_close_extraction"
            ),
            _canonicalize,
        )

        stats = _stats()

        _process_fund_news_article(
            article,
            stats,
        )

        record = (
            ExtractionRecord.query.one()
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_PROMOTE
        )

        assert (
            record.promoted_at
            is not None
        )

        assert (
            called["canonicalized"]
            is True
        )

        assert (
            stats["fund_news_processed"]
            == 1
        )

        assert (
            stats["fund_closes"]
            == 1
        )

        assert (
            stats["processing_failed"]
            == 0
        )