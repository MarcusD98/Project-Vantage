from models.article import db


funding_round_investors = db.Table(
    "funding_round_investors",

    db.Column(
        "funding_round_id",
        db.Integer,
        db.ForeignKey("funding_round.id"),
        primary_key=True,
    ),

    db.Column(
        "investor_id",
        db.Integer,
        db.ForeignKey("investor.id"),
        primary_key=True,
    ),
)


funding_round_lead_investors = db.Table(
    "funding_round_lead_investors",

    db.Column(
        "funding_round_id",
        db.Integer,
        db.ForeignKey("funding_round.id"),
        primary_key=True,
    ),

    db.Column(
        "investor_id",
        db.Integer,
        db.ForeignKey("investor.id"),
        primary_key=True,
    ),
)


funding_round_articles = db.Table(
    "funding_round_articles",

    db.Column(
        "funding_round_id",
        db.Integer,
        db.ForeignKey("funding_round.id"),
        primary_key=True,
    ),

    db.Column(
        "article_id",
        db.Integer,
        db.ForeignKey("article.id"),
        primary_key=True,
    ),
)


class FundingRound(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False,
    )

    event_evidence = db.Column(
        db.Text
    )

    amount = db.Column(
        db.Float
    )

    currency = db.Column(
        db.String(10)
    )

    round_type = db.Column(
        db.String(100)
    )

    announced_at = db.Column(
        db.DateTime
    )

    # Primary/source article retained for backwards compatibility.
    article_id = db.Column(
        db.Integer,
        db.ForeignKey("article.id"),
    )

    company = db.relationship(
        "Company",
        backref="funding_rounds",
    )

    investors = db.relationship(
        "Investor",
        secondary=funding_round_investors,
        backref="funding_rounds",
    )

    lead_investors = db.relationship(
        "Investor",
        secondary=funding_round_lead_investors,
        backref="led_funding_rounds",
    )

    # Existing primary source relationship.
    article = db.relationship(
        "Article",
        foreign_keys=[article_id],
        backref="primary_funding_rounds",
    )

    # All articles that provide evidence for this event.
    articles = db.relationship(
        "Article",
        secondary=funding_round_articles,
        backref="supported_funding_rounds",
    )

    def __repr__(self):
        return (
            f"<FundingRound "
            f"{self.company_id} "
            f"{self.amount} "
            f"{self.currency}>"
        )