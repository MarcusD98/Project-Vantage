from datetime import (
    datetime,
    timezone,
)

from models.article import db


def _utc_now():
    """
    Return the current UTC time as a naive datetime.

    Vantage currently stores database timestamps as naive UTC
    datetimes. This preserves that convention while avoiding
    the deprecated datetime.utcnow().
    """

    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )
    )


EVENT_TYPE_FUNDING_ROUND = "funding_round"
EVENT_TYPE_FUND_CLOSE = "fund_close"

VALIDATION_STATE_PENDING = "pending"
VALIDATION_STATE_PROMOTE = "promote"
VALIDATION_STATE_REVIEW = "review"
VALIDATION_STATE_REJECT = "reject"


class ExtractionRecord(db.Model):
    """
    Durable record of one structured interpretation of one
    evidence document.

    Extraction payloads are append-oriented: reprocessing an
    article creates a new ExtractionRecord rather than
    overwriting a previous extraction.

    Validation and promotion metadata may evolve after the
    extraction itself has been persisted.
    """

    __tablename__ = "extraction_record"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    article_id = db.Column(
        db.Integer,
        db.ForeignKey("article.id"),
        nullable=False,
        index=True,
    )

    event_type = db.Column(
        db.String(50),
        nullable=False,
        index=True,
    )

    # Structured extractor output.
    #
    # This payload should be treated as immutable once the
    # ExtractionRecord has been created.
    payload = db.Column(
        db.JSON,
        nullable=False,
    )

    # Identifies the prompt/schema/extraction contract.
    #
    # This is deliberately separate from the model name.
    extractor_version = db.Column(
        db.String(100),
        nullable=False,
        index=True,
    )

    model = db.Column(
        db.String(100),
        nullable=False,
    )

    validation_state = db.Column(
        db.String(30),
        nullable=False,
        default=VALIDATION_STATE_PENDING,
        index=True,
    )

    validation_flags = db.Column(
        db.JSON,
        nullable=False,
        default=list,
    )

    validator_version = db.Column(
        db.String(100),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=_utc_now,
        index=True,
    )

    validated_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    promoted_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    article = db.relationship(
        "Article",
        backref="extraction_records",
    )

    def __repr__(self):
        return (
            f"<ExtractionRecord "
            f"{self.id} "
            f"{self.event_type} "
            f"{self.extractor_version} "
            f"{self.validation_state}>"
        )