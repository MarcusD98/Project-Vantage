from datetime import datetime

from models.article import (
    Article,
    db,
)

from models.extraction_record import (
    EVENT_TYPE_FUNDING_ROUND,
    EVENT_TYPE_FUND_CLOSE,
    VALIDATION_STATE_PROMOTE,
)

from services.article_service import (
    populate_article_content,
)

from services.entity_service import (
    save_funding_extraction,
)

from services.extraction_record_service import (
    create_extraction_record,
)

from services.extraction_validation_service import (
    validate_extraction_record,
)

from services.fund_service import (
    save_fund_close_extraction,
)

from services.llm_extractor import (
    EXTRACTION_MODEL,
    FUNDING_EXTRACTOR_VERSION,
    FUND_CLOSE_EXTRACTOR_VERSION,
    extract_funding_with_llm,
    extract_fund_close_with_llm,
)


SUPPORTED_EVENT_TYPES = {
    EVENT_TYPE_FUNDING_ROUND,
    EVENT_TYPE_FUND_CLOSE,
}


def _ensure_article_content(
    article,
):
    """
    Ensure stored evidence has usable content before replay.

    Replay deliberately operates on persisted evidence and does
    not apply the live pipeline's publication-age policy.
    """

    if article.content:
        return True

    content = populate_article_content(
        article
    )

    return bool(
        content
    )


def _extract_current_version(
    article,
    event_type,
):
    """
    Run the currently configured extractor for one event type.

    Returns:
        extraction,
        extractor_version,
        model
    """

    if (
        event_type
        == EVENT_TYPE_FUNDING_ROUND
    ):
        extraction = (
            extract_funding_with_llm(
                article
            )
        )

        return (
            extraction,
            FUNDING_EXTRACTOR_VERSION,
            EXTRACTION_MODEL,
        )

    if (
        event_type
        == EVENT_TYPE_FUND_CLOSE
    ):
        extraction = (
            extract_fund_close_with_llm(
                article
            )
        )

        return (
            extraction,
            FUND_CLOSE_EXTRACTOR_VERSION,
            EXTRACTION_MODEL,
        )

    raise ValueError(
        f"Unsupported event type: {event_type}"
    )


def _promote_record(
    *,
    article,
    event_type,
    extraction,
    record,
):
    """
    Promote one validated extraction through the existing
    canonical persistence layer.

    This function deliberately reuses Vantage's established
    entity and event resolution services.

    It does not commit the transaction.
    """

    if (
        record.validation_state
        != VALIDATION_STATE_PROMOTE
    ):
        return None

    if (
        event_type
        == EVENT_TYPE_FUNDING_ROUND
    ):
        return save_funding_extraction(
            article,
            extraction,
        )

    if (
        event_type
        == EVENT_TYPE_FUND_CLOSE
    ):
        return save_fund_close_extraction(
            article,
            extraction,
        )

    raise ValueError(
        f"Unsupported event type: {event_type}"
    )


def replay_article(
    *,
    article,
    event_type,
):
    """
    Reprocess one persisted evidence document using the current
    extractor version.

    Replay is intentionally independent of
    Article.llm_processed_at.

    Every replay creates a NEW ExtractionRecord. Existing
    extraction history is never overwritten.

    Lifecycle:

        stored evidence
            ↓
        current extractor
            ↓
        new ExtractionRecord
            ↓
        deterministic validation
            ↓
        PROMOTE / REVIEW / REJECT
            ↓
        canonicalization only for PROMOTE

    Extraction + validation are committed before canonical
    promotion begins.

    Therefore, if canonical persistence subsequently fails, the
    new ExtractionRecord survives with:

        validation_state = promote
        promoted_at = None

    making the failed promotion observable and retryable.
    """

    if article.id is None:
        raise ValueError(
            "Article must be persisted before replay."
        )

    if (
        event_type
        not in SUPPORTED_EVENT_TYPES
    ):
        raise ValueError(
            f"Unsupported event type: {event_type}"
        )

    if not _ensure_article_content(
        article
    ):
        raise ValueError(
            "Article has no usable content for replay."
        )

    (
        extraction,
        extractor_version,
        model,
    ) = _extract_current_version(
        article,
        event_type,
    )

    if extraction is None:
        raise RuntimeError(
            "Extractor returned no structured result."
        )

    record = create_extraction_record(
        article=article,
        event_type=event_type,
        extraction=extraction,
        extractor_version=(
            extractor_version
        ),
        model=model,
    )

    validate_extraction_record(
        record
    )

    # Keep the legacy Article fields as a compatibility
    # projection while ExtractionRecord becomes authoritative.
    #
    # Replay does NOT require these fields to be reset first.
    article.llm_processed_at = (
        datetime.now()
    )

    if (
        event_type
        == EVENT_TYPE_FUNDING_ROUND
    ):
        article.llm_is_funding_round = (
            extraction.is_funding_round
        )

    # Persist extraction + validation before canonical writes.
    db.session.commit()

    result = {
        "article_id": article.id,
        "event_type": event_type,
        "record_id": record.id,
        "extractor_version": (
            record.extractor_version
        ),
        "model": record.model,
        "validation_state": (
            record.validation_state
        ),
        "validation_flags": list(
            record.validation_flags
            or []
        ),
        "promoted": False,
        "promoted_at": None,
    }

    if (
        record.validation_state
        != VALIDATION_STATE_PROMOTE
    ):
        return result

    try:
        canonical_object = (
            _promote_record(
                article=article,
                event_type=event_type,
                extraction=extraction,
                record=record,
            )
        )

        if canonical_object is not None:
            record.promoted_at = (
                datetime.now()
            )

        db.session.commit()

    except Exception:
        # Canonical writes are rolled back while the committed
        # extraction + validation history remains intact.
        db.session.rollback()
        raise

    result[
        "promoted"
    ] = (
        canonical_object
        is not None
    )

    result[
        "promoted_at"
    ] = record.promoted_at

    return result


def replay_article_by_id(
    *,
    article_id,
    event_type,
):
    """
    Convenience entry point for replaying one stored Article by
    database ID.
    """

    article = db.session.get(
        Article,
        article_id,
    )

    if article is None:
        raise ValueError(
            f"Article not found: {article_id}"
        )

    return replay_article(
        article=article,
        event_type=event_type,
    )