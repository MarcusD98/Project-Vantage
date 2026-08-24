from pydantic import (
    BaseModel,
    Field,
)

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
    EVENT_TYPE_FUNDING_ROUND,
    EVENT_TYPE_FUND_CLOSE,
    VALIDATION_STATE_PROMOTE,
    VALIDATION_STATE_REVIEW,
    VALIDATION_STATE_REJECT,
)

from services.extraction_record_service import (
    create_extraction_record,
)

from services.extraction_validation_service import (
    VALIDATOR_VERSION,
    FLAG_NOT_FUNDING_ROUND,
    FLAG_NOT_FUND_CLOSE,
    FLAG_COMPOUND_EVIDENCE,
    FLAG_AGGREGATE_HISTORICAL_FINANCING,
    FLAG_MISSING_COMPANY_NAME,
    FLAG_MISSING_FUND_NAME,
    FLAG_INVALID_AMOUNT,
    FLAG_INVALID_CURRENCY,
    FLAG_LEAD_NOT_IN_INVESTORS,
    validate_extraction_record,
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
    title="Example raises $12M Series A",
    content=None,
    category="Funding Round",
):
    if content is None:
        content = (
            "Example raised $12 million in a "
            "Series A led by Test Ventures."
        )

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
        content=content,
        category=category,
    )


def _persist_article(
    article,
):
    db.session.add(
        article
    )

    db.session.flush()

    return article


def _funding_extraction(
    *,
    is_funding_round=True,
    event_evidence=(
        "Example raised a $12 million "
        "Series A."
    ),
    company_name="Example",
    amount=12_000_000,
    currency="USD",
    investors=None,
    lead_investors=None,
):
    if investors is None:
        investors = [
            "Test Ventures",
        ]

    if lead_investors is None:
        lead_investors = [
            "Test Ventures",
        ]

    return _FundingExtraction(
        is_funding_round=(
            is_funding_round
        ),
        event_evidence=event_evidence,
        company_name=company_name,
        amount=amount,
        currency=currency,
        round_type="Series A",
        investors=investors,
        lead_investors=lead_investors,
    )


def _fund_close_extraction(
    *,
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
):
    return _FundCloseExtraction(
        is_fund_close=is_fund_close,
        event_evidence=event_evidence,
        investor_name=investor_name,
        fund_name=fund_name,
        amount=amount,
        currency=currency,
        close_type=close_type,
        strategy="Early Stage",
        geography="Europe",
        vintage_year=2026,
    )


def _create_funding_record(
    article,
    extraction,
):
    return create_extraction_record(
        article=article,
        event_type=(
            EVENT_TYPE_FUNDING_ROUND
        ),
        extraction=extraction,
        extractor_version="funding-v1",
        model="gpt-5.6-luna",
    )


def _create_fund_close_record(
    article,
    extraction,
):
    return create_extraction_record(
        article=article,
        event_type=(
            EVENT_TYPE_FUND_CLOSE
        ),
        extraction=extraction,
        extractor_version="fund-close-v1",
        model="gpt-5.6-luna",
    )


def _assert_no_canonical_data():
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


def test_valid_funding_record_is_promoted(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article()
        )

        record = _create_funding_record(
            article,
            _funding_extraction(),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_PROMOTE
        )

        assert (
            record.validation_flags
            == []
        )

        assert (
            record.validator_version
            == VALIDATOR_VERSION
        )

        assert (
            record.validated_at
            is not None
        )

        _assert_no_canonical_data()


def test_non_funding_classification_is_rejected(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article()
        )

        record = _create_funding_record(
            article,
            _funding_extraction(
                is_funding_round=False
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REJECT
        )

        assert (
            FLAG_NOT_FUNDING_ROUND
            in record.validation_flags
        )

        _assert_no_canonical_data()


def test_missing_company_name_requires_review(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article()
        )

        record = _create_funding_record(
            article,
            _funding_extraction(
                company_name=None
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REVIEW
        )

        assert (
            FLAG_MISSING_COMPANY_NAME
            in record.validation_flags
        )

        _assert_no_canonical_data()


def test_invalid_amount_requires_review(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article()
        )

        record = _create_funding_record(
            article,
            _funding_extraction(
                amount=-1
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REVIEW
        )

        assert (
            FLAG_INVALID_AMOUNT
            in record.validation_flags
        )

        _assert_no_canonical_data()


def test_invalid_currency_requires_review(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article()
        )

        record = _create_funding_record(
            article,
            _funding_extraction(
                currency="US"
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REVIEW
        )

        assert (
            FLAG_INVALID_CURRENCY
            in record.validation_flags
        )

        _assert_no_canonical_data()


def test_lead_investor_must_also_be_in_investors(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article()
        )

        record = _create_funding_record(
            article,
            _funding_extraction(
                investors=[
                    "Test Ventures",
                ],
                lead_investors=[
                    "Other Ventures",
                ],
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REVIEW
        )

        assert (
            FLAG_LEAD_NOT_IN_INVESTORS
            in record.validation_flags
        )

        _assert_no_canonical_data()


def test_compound_funding_evidence_is_rejected(
    app,
    monkeypatch,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title=(
                    "Five startups announce "
                    "new funding rounds"
                ),
            )
        )

        monkeypatch.setattr(
            (
                "services."
                "extraction_validation_service."
                "is_compound_funding_evidence"
            ),
            lambda article: True,
        )

        record = _create_funding_record(
            article,
            _funding_extraction(),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REJECT
        )

        assert (
            FLAG_COMPOUND_EVIDENCE
            in record.validation_flags
        )

        _assert_no_canonical_data()


def test_valid_fund_close_record_is_promoted(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title=(
                    "Test Ventures closes "
                    "Test Fund III"
                ),
                category="Fund News",
            )
        )

        record = _create_fund_close_record(
            article,
            _fund_close_extraction(),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_PROMOTE
        )

        assert (
            record.validation_flags
            == []
        )

        _assert_no_canonical_data()


def test_non_fund_close_classification_is_rejected(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title="Not a fund close",
                category="Fund News",
            )
        )

        record = _create_fund_close_record(
            article,
            _fund_close_extraction(
                is_fund_close=False
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REJECT
        )

        assert (
            FLAG_NOT_FUND_CLOSE
            in record.validation_flags
        )

        _assert_no_canonical_data()


def test_missing_fund_name_requires_review(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title=(
                    "Test Ventures announces "
                    "new fund"
                ),
                category="Fund News",
            )
        )

        record = _create_fund_close_record(
            article,
            _fund_close_extraction(
                fund_name=None
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REVIEW
        )

        assert (
            FLAG_MISSING_FUND_NAME
            in record.validation_flags
        )

        _assert_no_canonical_data()

def test_aggregate_multi_period_financing_requires_review(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title=(
                    "Domyn raises over $1bn"
                ),
            )
        )

        record = _create_funding_record(
            article,
            _funding_extraction(
                event_evidence=(
                    "Domyn has raised $1.1 billion "
                    "in debt and equity funding over "
                    "the past two years."
                ),
                company_name="Domyn",
                amount=1_100_000_000,
                currency="USD",
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_REVIEW
        )

        assert (
            FLAG_AGGREGATE_HISTORICAL_FINANCING
            in record.validation_flags
        )

        _assert_no_canonical_data()


def test_discrete_round_with_total_funding_context_is_promoted(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title=(
                    "Venice raises $25M Series A"
                ),
            )
        )

        record = _create_funding_record(
            article,
            _funding_extraction(
                event_evidence=(
                    "Venice raised $25 million in "
                    "Series A funding led by IVP, "
                    "following an $8 million seed round "
                    "and bringing total funding to "
                    "$33 million."
                ),
                company_name="Venice",
                amount=25_000_000,
                currency="USD",
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_PROMOTE
        )

        assert (
            FLAG_AGGREGATE_HISTORICAL_FINANCING
            not in record.validation_flags
        )

        _assert_no_canonical_data()


def test_discrete_round_with_bringing_total_funding_is_promoted(
    app,
):
    with app.app_context():
        article = _persist_article(
            _make_article(
                title=(
                    "Ankar raises $20M Series A"
                ),
            )
        )

        record = _create_funding_record(
            article,
            _funding_extraction(
                event_evidence=(
                    "Ankar raised a $20 million "
                    "Series A, bringing its total "
                    "funding to $24 million."
                ),
                company_name="Ankar",
                amount=20_000_000,
                currency="USD",
            ),
        )

        validate_extraction_record(
            record
        )

        assert (
            record.validation_state
            == VALIDATION_STATE_PROMOTE
        )

        assert (
            FLAG_AGGREGATE_HISTORICAL_FINANCING
            not in record.validation_flags
        )

        _assert_no_canonical_data()
