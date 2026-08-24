import re

from datetime import (
    datetime,
    timezone,
)

from models.article import db

from models.extraction_record import (
    EVENT_TYPE_FUNDING_ROUND,
    EVENT_TYPE_FUND_CLOSE,
    VALIDATION_STATE_PROMOTE,
    VALIDATION_STATE_REVIEW,
    VALIDATION_STATE_REJECT,
)

from services.compound_evidence_service import (
    is_compound_funding_evidence,
)


VALIDATOR_VERSION = "deterministic-v1"


FLAG_UNSUPPORTED_EVENT_TYPE = "unsupported_event_type"
FLAG_MALFORMED_PAYLOAD = "malformed_payload"

FLAG_NOT_FUNDING_ROUND = "not_funding_round"
FLAG_NOT_FUND_CLOSE = "not_fund_close"

FLAG_COMPOUND_EVIDENCE = "compound_evidence"
FLAG_AGGREGATE_HISTORICAL_FINANCING = (
    "aggregate_historical_financing"
)

FLAG_MISSING_EVENT_EVIDENCE = "missing_event_evidence"
FLAG_MISSING_COMPANY_NAME = "missing_company_name"
FLAG_MISSING_INVESTOR_NAME = "missing_investor_name"
FLAG_MISSING_FUND_NAME = "missing_fund_name"

FLAG_INVALID_AMOUNT = "invalid_amount"
FLAG_INVALID_CURRENCY = "invalid_currency"
FLAG_INVALID_INVESTOR_LIST = "invalid_investor_list"
FLAG_INVALID_LEAD_INVESTOR_LIST = "invalid_lead_investor_list"
FLAG_LEAD_NOT_IN_INVESTORS = "lead_not_in_investors"
FLAG_INVALID_CLOSE_TYPE = "invalid_close_type"


VALID_FUND_CLOSE_TYPES = {
    "first_close",
    "interim_close",
    "final_close",
    "unknown",
}


AGGREGATE_HISTORICAL_FINANCING_PATTERNS = [
    re.compile(
        r"\b(?:has|have|had)?\s*raised\b"
        r".{0,180}"
        r"\bover\s+(?:the\s+)?(?:past|last)\s+"
        r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
        r"\s+(?:months?|years?)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:has|have|had)?\s*raised\b"
        r".{0,180}"
        r"\bsince\s+(?:19|20)\d{2}\b",
        re.IGNORECASE | re.DOTALL,
    ),
]


def _utc_now():
    """
    Return the current UTC time as a naive datetime.

    Vantage currently stores database timestamps as naive UTC
    datetimes.
    """

    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )
    )


def _has_text(value):
    """
    Return True when a value contains meaningful text.
    """

    return (
        isinstance(
            value,
            str,
        )
        and bool(
            value.strip()
        )
    )


def _is_aggregate_historical_financing(
    payload,
):
    """
    Detect high-confidence cases where an extracted amount
    describes cumulative financing across a historical period
    rather than one discrete focal funding event.

    This is deliberately narrow.

    Phrases such as "bringing total funding to $X" are not
    sufficient because legitimate focal-round announcements
    commonly include cumulative funding context.
    """

    evidence = payload.get(
        "event_evidence"
    )

    if not _has_text(
        evidence
    ):
        return False

    return any(
        pattern.search(
            evidence
        )
        is not None
        for pattern
        in AGGREGATE_HISTORICAL_FINANCING_PATTERNS
    )


def _currency_is_valid(value):
    """
    Validate the lightweight currency contract used by the
    current extraction layer.

    Currency may be absent. When present, it should be a
    three-letter alphabetic code such as USD, EUR, or GBP.
    """

    if value is None:
        return True

    if not isinstance(
        value,
        str,
    ):
        return False

    normalized = value.strip()

    return (
        len(normalized) == 3
        and normalized.isalpha()
    )


def _amount_is_valid(value):
    """
    Amount may be absent.

    When present it must be a positive numeric value.
    """

    if value is None:
        return True

    if isinstance(
        value,
        bool,
    ):
        return False

    if not isinstance(
        value,
        (
            int,
            float,
        ),
    ):
        return False

    return value > 0


def _validate_funding_record(
    record,
):
    """
    Validate one company-funding extraction.

    Returns:
        (state, flags)
    """

    payload = record.payload

    reject_flags = []
    review_flags = []

    if (
        payload.get(
            "is_funding_round"
        )
        is not True
    ):
        reject_flags.append(
            FLAG_NOT_FUNDING_ROUND
        )

    if (
        record.article is not None
        and is_compound_funding_evidence(
            record.article
        )
    ):
        reject_flags.append(
            FLAG_COMPOUND_EVIDENCE
        )

    if _is_aggregate_historical_financing(
        payload
    ):
        review_flags.append(
            FLAG_AGGREGATE_HISTORICAL_FINANCING
        )

    if not _has_text(
        payload.get(
            "event_evidence"
        )
    ):
        review_flags.append(
            FLAG_MISSING_EVENT_EVIDENCE
        )

    if not _has_text(
        payload.get(
            "company_name"
        )
    ):
        review_flags.append(
            FLAG_MISSING_COMPANY_NAME
        )

    amount = payload.get(
        "amount"
    )

    if not _amount_is_valid(
        amount
    ):
        review_flags.append(
            FLAG_INVALID_AMOUNT
        )

    currency = payload.get(
        "currency"
    )

    if not _currency_is_valid(
        currency
    ):
        review_flags.append(
            FLAG_INVALID_CURRENCY
        )

    investors = payload.get(
        "investors",
        [],
    )

    lead_investors = payload.get(
        "lead_investors",
        [],
    )

    investors_valid = isinstance(
        investors,
        list,
    )

    leads_valid = isinstance(
        lead_investors,
        list,
    )

    if not investors_valid:
        review_flags.append(
            FLAG_INVALID_INVESTOR_LIST
        )

    if not leads_valid:
        review_flags.append(
            FLAG_INVALID_LEAD_INVESTOR_LIST
        )

    if (
        investors_valid
        and leads_valid
    ):
        investor_names = {
            value.strip().casefold()
            for value in investors
            if _has_text(
                value
            )
        }

        lead_names = {
            value.strip().casefold()
            for value in lead_investors
            if _has_text(
                value
            )
        }

        if not lead_names.issubset(
            investor_names
        ):
            review_flags.append(
                FLAG_LEAD_NOT_IN_INVESTORS
            )

    if reject_flags:
        return (
            VALIDATION_STATE_REJECT,
            reject_flags
            + review_flags,
        )

    if review_flags:
        return (
            VALIDATION_STATE_REVIEW,
            review_flags,
        )

    return (
        VALIDATION_STATE_PROMOTE,
        [],
    )


def _validate_fund_close_record(
    record,
):
    """
    Validate one fund-close extraction.

    Returns:
        (state, flags)
    """

    payload = record.payload

    reject_flags = []
    review_flags = []

    if (
        payload.get(
            "is_fund_close"
        )
        is not True
    ):
        reject_flags.append(
            FLAG_NOT_FUND_CLOSE
        )

    if not _has_text(
        payload.get(
            "event_evidence"
        )
    ):
        review_flags.append(
            FLAG_MISSING_EVENT_EVIDENCE
        )

    if not _has_text(
        payload.get(
            "investor_name"
        )
    ):
        review_flags.append(
            FLAG_MISSING_INVESTOR_NAME
        )

    # The current canonical fund service requires a named
    # fund before it can create or resolve a FundClose.
    if not _has_text(
        payload.get(
            "fund_name"
        )
    ):
        review_flags.append(
            FLAG_MISSING_FUND_NAME
        )

    amount = payload.get(
        "amount"
    )

    if not _amount_is_valid(
        amount
    ):
        review_flags.append(
            FLAG_INVALID_AMOUNT
        )

    currency = payload.get(
        "currency"
    )

    if not _currency_is_valid(
        currency
    ):
        review_flags.append(
            FLAG_INVALID_CURRENCY
        )

    close_type = payload.get(
        "close_type"
    )

    if (
        close_type is not None
        and close_type
        not in VALID_FUND_CLOSE_TYPES
    ):
        review_flags.append(
            FLAG_INVALID_CLOSE_TYPE
        )

    if reject_flags:
        return (
            VALIDATION_STATE_REJECT,
            reject_flags
            + review_flags,
        )

    if review_flags:
        return (
            VALIDATION_STATE_REVIEW,
            review_flags,
        )

    return (
        VALIDATION_STATE_PROMOTE,
        [],
    )


def validate_extraction_record(
    record,
):
    """
    Run deterministic validation against one persisted
    ExtractionRecord.

    Validation modifies only validation metadata on the
    ExtractionRecord.

    It does not:
    - modify the extraction payload
    - create canonical entities
    - create canonical events
    - commit the transaction

    Transaction ownership remains with the caller.
    """

    if record.id is None:
        raise ValueError(
            "ExtractionRecord must be persisted "
            "before validation."
        )

    if not isinstance(
        record.payload,
        dict,
    ):
        state = (
            VALIDATION_STATE_REJECT
        )

        flags = [
            FLAG_MALFORMED_PAYLOAD
        ]

    elif (
        record.event_type
        == EVENT_TYPE_FUNDING_ROUND
    ):
        state, flags = (
            _validate_funding_record(
                record
            )
        )

    elif (
        record.event_type
        == EVENT_TYPE_FUND_CLOSE
    ):
        state, flags = (
            _validate_fund_close_record(
                record
            )
        )

    else:
        state = (
            VALIDATION_STATE_REJECT
        )

        flags = [
            FLAG_UNSUPPORTED_EVENT_TYPE
        ]

    record.validation_state = state

    record.validation_flags = flags

    record.validator_version = (
        VALIDATOR_VERSION
    )

    record.validated_at = (
        _utc_now()
    )

    db.session.flush()

    return record