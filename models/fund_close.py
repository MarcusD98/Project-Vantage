from models.article import db


fund_close_articles = db.Table(
    "fund_close_articles",

    db.Column(
        "fund_close_id",
        db.Integer,
        db.ForeignKey("fund_close.id"),
        primary_key=True,
    ),

    db.Column(
        "article_id",
        db.Integer,
        db.ForeignKey("article.id"),
        primary_key=True,
    ),
)


class FundClose(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    fund_id = db.Column(
        db.Integer,
        db.ForeignKey("fund.id"),
        nullable=False,
    )

    # Primary/source article retained for backwards
    # compatibility.
    article_id = db.Column(
        db.Integer,
        db.ForeignKey("article.id"),
        nullable=True,
    )

    amount = db.Column(
        db.Float,
        nullable=True,
    )

    currency = db.Column(
        db.String(10),
        nullable=True,
    )

    close_type = db.Column(
        db.String(50),
        nullable=True,
    )

    announced_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    event_evidence = db.Column(
        db.Text,
        nullable=True,
    )

    fund = db.relationship(
        "Fund",
        backref="closes",
    )

    # Existing primary source relationship.
    article = db.relationship(
        "Article",
        foreign_keys=[article_id],
        backref="fund_closes",
    )

    # All articles that provide evidence for this
    # canonical fund-close event.
    articles = db.relationship(
        "Article",
        secondary=fund_close_articles,
        backref="supported_fund_closes",
    )

    def __repr__(self):
        return (
            f"<FundClose {self.fund.name} "
            f"{self.amount} {self.currency}>"
        )