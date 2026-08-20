from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Article(db.Model):
    """
    Persisted public evidence document.

    The model retains the historical Article name for
    backwards compatibility, but evidence may increasingly
    originate from publications, investors, ecosystem
    sources, company websites, and other public sources.
    """

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.String(500),
        nullable=False,
    )

    source = db.Column(
        db.String(100),
        nullable=False,
    )

    source_type = db.Column(
        db.String(50),
        nullable=True,
    )

    discovery_method = db.Column(
        db.String(50),
        nullable=True,
    )

    url = db.Column(
        db.String(1000),
        unique=True,
        nullable=False,
    )

    published_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    summary = db.Column(
        db.Text,
        nullable=True,
    )

    content = db.Column(
        db.Text,
        nullable=True,
    )

    category = db.Column(
        db.String(100),
        nullable=True,
    )

    # Track whether the LLM has processed this evidence.
    llm_processed_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    # Store the LLM's company-funding classification.
    llm_is_funding_round = db.Column(
        db.Boolean,
        nullable=True,
    )

    def __repr__(self):
        return (
            f"<Article "
            f"{self.title}>"
        )