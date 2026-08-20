from models.article import db


class SourceRun(db.Model):
    """
    Persistent operational record for one source execution.

    Source configuration remains in the canonical source
    registry.

    SourceRun records what actually happened when that source
    was operated.
    """

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    source_key = db.Column(
        db.String(100),
        nullable=False,
        index=True,
    )

    source_name = db.Column(
        db.String(150),
        nullable=False,
        index=True,
    )

    source_type = db.Column(
        db.String(50),
        nullable=True,
        index=True,
    )

    mode = db.Column(
        db.String(30),
        nullable=False,
        index=True,
    )

    process_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        index=True,
    )

    started_at = db.Column(
        db.DateTime,
        nullable=False,
        index=True,
    )

    finished_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    # -----------------------------------------------------
    # Discovery
    # -----------------------------------------------------

    articles_discovered = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    articles_relevant = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    articles_saved = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    dates_populated = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    remaining_undated = db.Column(
        db.Integer,
        nullable=True,
    )

    # -----------------------------------------------------
    # Intelligence preparation
    # -----------------------------------------------------

    articles_selected = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    stale_articles_skipped = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    compound_articles_skipped = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    content_retrieved = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    content_failed = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    # -----------------------------------------------------
    # Structured intelligence
    # -----------------------------------------------------

    funding_processed = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    funding_rounds = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    fund_news_processed = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    fund_closes = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    processing_failed = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    # -----------------------------------------------------
    # Failure context
    # -----------------------------------------------------

    error = db.Column(
        db.Text,
        nullable=True,
    )

    def __repr__(self):
        return (
            f"<SourceRun "
            f"{self.source_name} "
            f"{self.mode} "
            f"{self.status}>"
        )