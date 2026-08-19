from models.article import db


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

    article = db.relationship(
        "Article",
        backref="fund_closes",
    )

    def __repr__(self):
        return (
            f"<FundClose {self.fund.name} "
            f"{self.amount} {self.currency}>"
        )