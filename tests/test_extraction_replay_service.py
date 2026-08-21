from datetime import datetime

import pytest

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
    EVENT_TYPE_FUNDING_ROUND,
    EVENT_TYPE_FUND_CLOSE,
    VALIDATION_STATE_PROMOTE,
    VALIDATION_STATE_REVIEW,
)

from services.extraction_record_service import (
    create_extraction_record,
)

from services.extraction_replay_service import (
    replay_article,
    replay_article_by_id,
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
        source="Replay Test Source",
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
        ),
        content=(
            "Stored evidence used for "
            "extraction replay."
        ),
        category=category,
        llm_processed_at=datetime(
            2026,
            1,
            1,
        ),
    )


def _persist_article(
    article,
):
    db.session.add(
        article
    )

    db.session.commit()

    return article


def _funding_extraction(
    *,
    company_name="Example",
):
    return _FundingExtraction(
        is_funding_round=True,
        event_evidence=(
            "Example raised a $12 million "
            "Series A."
        ),
        company_name=company_name,
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


def _fund_close_extraction():
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


def test_replay_ignores_legacy_processed_state_and_appends_record(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Replay funding example",
                category="Funding Round",
            )
        )

        old_record = (
            create_extraction_record(
                article=article,
                event_type=(
                    EVENT_TYPE_FUNDING_ROUND
                ),
                extraction=(
                    _funding_extraction()
                ),
                extractor_version="funding-v1",
                model="old-model",
            )
        )

        db.session.commit()

        old_record_id = (
            old_record.id
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "FUNDING_EXTRACTOR_VERSION"
            ),
            "funding-v2",
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "EXTRACTION_MODEL"
            ),
            "new-model",
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "extract_funding_with_llm"
            ),
            lambda article: (
                _funding_extraction()
            ),
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "save_funding_extraction"
            ),
            lambda article, extraction: (
                object()
            ),
        )

        result = replay_article(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
        )

        records = (
            ExtractionRecord.query
            .order_by(
                ExtractionRecord.id
            )
            .all()
        )

        assert len(
            records
        ) == 2

        assert (
            records[0].id
            == old_record_id
        )

        assert (
            records[0].extractor_version
            == "funding-v1"
        )

        assert (
            records[0].model
            == "old-model"
        )

        assert (
            records[1].extractor_version
            == "funding-v2"
        )

        assert (
            records[1].model
            == "new-model"
        )

        assert (
            records[1].validation_state
            == VALIDATION_STATE_PROMOTE
        )

        assert (
            records[1].promoted_at
            is not None
        )

        assert (
            result["promoted"]
            is True
        )


def test_review_record_does_not_block_later_successful_replay(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Improved replay example",
                category="Funding Round",
            )
        )

        old_record = (
            create_extraction_record(
                article=article,
                event_type=(
                    EVENT_TYPE_FUNDING_ROUND
                ),
                extraction=(
                    _funding_extraction(
                        company_name=None
                    )
                ),
                extractor_version="funding-v1",
                model="old-model",
            )
        )

        from services.extraction_validation_service import (
            validate_extraction_record,
        )

        validate_extraction_record(
            old_record
        )

        db.session.commit()

        assert (
            old_record.validation_state
            == VALIDATION_STATE_REVIEW
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "FUNDING_EXTRACTOR_VERSION"
            ),
            "funding-v2",
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "extract_funding_with_llm"
            ),
            lambda article: (
                _funding_extraction(
                    company_name="Example"
                )
            ),
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "save_funding_extraction"
            ),
            lambda article, extraction: (
                object()
            ),
        )

        result = replay_article(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
        )

        records = (
            ExtractionRecord.query
            .order_by(
                ExtractionRecord.id
            )
            .all()
        )

        assert len(
            records
        ) == 2

        assert (
            records[0].validation_state
            == VALIDATION_STATE_REVIEW
        )

        assert (
            records[0].promoted_at
            is None
        )

        assert (
            records[1].validation_state
            == VALIDATION_STATE_PROMOTE
        )

        assert (
            records[1].promoted_at
            is not None
        )

        assert (
            result["promoted"]
            is True
        )


def test_replay_review_is_quarantined(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Replay review example",
                category="Funding Round",
            )
        )

        called = {
            "canonicalized": False,
        }

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "extract_funding_with_llm"
            ),
            lambda article: (
                _funding_extraction(
                    company_name=None
                )
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
                "REVIEW replay reached "
                "canonicalization."
            )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "save_funding_extraction"
            ),
            _should_not_run,
        )

        result = replay_article(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
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
            result["promoted"]
            is False
        )


def test_failed_replay_promotion_preserves_new_record(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Replay failure example",
                category="Funding Round",
            )
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "extract_funding_with_llm"
            ),
            lambda article: (
                _funding_extraction()
            ),
        )

        def _fail(
            article,
            extraction,
        ):
            raise RuntimeError(
                "Canonical persistence failed."
            )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "save_funding_extraction"
            ),
            _fail,
        )

        with pytest.raises(
            RuntimeError,
            match=(
                "Canonical persistence failed"
            ),
        ):
            replay_article(
                article=article,
                event_type=(
                    EVENT_TYPE_FUNDING_ROUND
                ),
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
            is None
        )


def test_fund_close_can_be_replayed(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Replay fund close example",
                category="Fund News",
            )
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "FUND_CLOSE_EXTRACTOR_VERSION"
            ),
            "fund-close-v2",
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "extract_fund_close_with_llm"
            ),
            lambda article: (
                _fund_close_extraction()
            ),
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_replay_service."
                "save_fund_close_extraction"
            ),
            lambda article, extraction: (
                object()
            ),
        )

        result = replay_article_by_id(
            article_id=article.id,
            event_type=(
                EVENT_TYPE_FUND_CLOSE
            ),
        )

        record = (
            ExtractionRecord.query.one()
        )

        assert (
            record.event_type
            == EVENT_TYPE_FUND_CLOSE
        )

        assert (
            record.extractor_version
            == "fund-close-v2"
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
            result["promoted"]
            is True
        )


def test_replay_missing_article_fails_cleanly(
    app,
):
    with app.app_context():
        with pytest.raises(
            ValueError,
            match="Article not found",
        ):
            replay_article_by_id(
                article_id=999999,
                event_type=(
                    EVENT_TYPE_FUNDING_ROUND
                ),
            )