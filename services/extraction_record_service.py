from pydantic import BaseModel

from models.article import db
from models.extraction_record import ExtractionRecord


def create_extraction_record(
    *,
    article,
    event_type,
    extraction,
    extractor_version,
    model,
):
    """
    Persist one immutable structured extraction attempt.

    This service deliberately does not commit the transaction.
    Transaction ownership remains with the caller.

    Reprocessing should create a new ExtractionRecord rather
    than update or replace an existing record.
    """

    if article.id is None:
        raise ValueError(
            "Article must be persisted before extraction "
            "can be recorded."
        )

    if not event_type:
        raise ValueError(
            "event_type is required."
        )

    if not extractor_version:
        raise ValueError(
            "extractor_version is required."
        )

    if not model:
        raise ValueError(
            "model is required."
        )

    if not isinstance(
        extraction,
        BaseModel,
    ):
        raise TypeError(
            "extraction must be a Pydantic BaseModel."
        )

    payload = extraction.model_dump(
        mode="json"
    )

    record = ExtractionRecord(
        article_id=article.id,
        event_type=event_type,
        payload=payload,
        extractor_version=extractor_version,
        model=model,
    )

    db.session.add(
        record
    )

    db.session.flush()

    return record