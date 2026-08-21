import pytest

from pydantic import BaseModel, Field

from models.article import (
    Article,
    db,
)

from models.company import Company
from models.investor import Investor
from models.funding_round import FundingRound
from models.fund import Fund
from models.fund_close import FundClose

from models.extraction_record import (
    ExtractionRecord,
    EVENT_TYPE_FUNDING_ROUND,
    VALIDATION_STATE_PENDING,
)

from services.extraction_record_service import (
    create_extraction_record,
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


def _make_article():
    return Article(
        title="Example raises $12M Series A",
        source="Example Source",
        source_type="publication",
        discovery_method="rss",
        url=(
            "https://example.com/"
            "example-raises-series-a"
        ),
        content=(
            "Example raised $12 million in a "
            "Series A led by Test Ventures."
        ),
        category="Funding Round",
    )


def _make_extraction(
    amount=12_000_000,
):
    return _FundingExtraction(
        is_funding_round=True,
        event_evidence=(
            "Example raised a $12 million "
            "Series A."
        ),
        company_name="Example",
        amount=amount,
        currency="USD",
        round_type="Series A",
        investors=[
            "Test Ventures",
        ],
        lead_investors=[
            "Test Ventures",
        ],
    )


def test_extraction_record_persists_payload_and_provenance(
    app,
):
    with app.app_context():
        article = _make_article()

        db.session.add(
            article
        )

        db.session.flush()

        record = create_extraction_record(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
            extraction=_make_extraction(),
            extractor_version="funding-v1",
            model="gpt-5.6-luna",
        )

        assert record.id is not None

        assert (
            record.article_id
            == article.id
        )

        assert (
            record.event_type
            == EVENT_TYPE_FUNDING_ROUND
        )

        assert (
            record.extractor_version
            == "funding-v1"
        )

        assert (
            record.model
            == "gpt-5.6-luna"
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_PENDING
        )

        assert (
            record.validation_flags
            == []
        )

        assert (
            record.payload[
                "company_name"
            ]
            == "Example"
        )

        assert (
            record.payload[
                "amount"
            ]
            == 12_000_000
        )

        assert (
            record.payload[
                "lead_investors"
            ]
            == [
                "Test Ventures",
            ]
        )


def test_multiple_extractor_versions_can_coexist(
    app,
):
    with app.app_context():
        article = _make_article()

        db.session.add(
            article
        )

        db.session.flush()

        first = create_extraction_record(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
            extraction=_make_extraction(
                amount=12_000_000
            ),
            extractor_version="funding-v1",
            model="gpt-5.6-luna",
        )

        second = create_extraction_record(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
            extraction=_make_extraction(
                amount=12_500_000
            ),
            extractor_version="funding-v2",
            model="gpt-5.6-luna",
        )

        assert (
            first.id
            != second.id
        )

        assert (
            ExtractionRecord.query.count()
            == 2
        )

        versions = {
            record.extractor_version
            for record
            in ExtractionRecord.query.all()
        }

        assert versions == {
            "funding-v1",
            "funding-v2",
        }


def test_same_extractor_version_can_be_replayed(
    app,
):
    with app.app_context():
        article = _make_article()

        db.session.add(
            article
        )

        db.session.flush()

        first = create_extraction_record(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
            extraction=_make_extraction(),
            extractor_version="funding-v1",
            model="gpt-5.6-luna",
        )

        second = create_extraction_record(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
            extraction=_make_extraction(),
            extractor_version="funding-v1",
            model="gpt-5.6-luna",
        )

        assert (
            first.id
            != second.id
        )

        assert (
            ExtractionRecord.query.count()
            == 2
        )


def test_extraction_record_does_not_create_canonical_data(
    app,
):
    with app.app_context():
        article = _make_article()

        db.session.add(
            article
        )

        db.session.flush()

        create_extraction_record(
            article=article,
            event_type=(
                EVENT_TYPE_FUNDING_ROUND
            ),
            extraction=_make_extraction(),
            extractor_version="funding-v1",
            model="gpt-5.6-luna",
        )

        assert (
            ExtractionRecord.query.count()
            == 1
        )

        assert (
            Company.query.count()
            == 0
        )

        assert (
            Investor.query.count()
            == 0
        )

        assert (
            FundingRound.query.count()
            == 0
        )

        assert (
            Fund.query.count()
            == 0
        )

        assert (
            FundClose.query.count()
            == 0
        )

        assert (
            article.llm_processed_at
            is None
        )

        assert (
            article.llm_is_funding_round
            is None
        )


def test_extraction_record_requires_persisted_article(
    app,
):
    with app.app_context():
        article = _make_article()

        with pytest.raises(
            ValueError,
            match=(
                "Article must be persisted"
            ),
        ):
            create_extraction_record(
                article=article,
                event_type=(
                    EVENT_TYPE_FUNDING_ROUND
                ),
                extraction=_make_extraction(),
                extractor_version="funding-v1",
                model="gpt-5.6-luna",
            )