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

class FundingRound(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False,
    )

    amount = db.Column(db.Float)
    currency = db.Column(db.String(10))
    round_type = db.Column(db.String(100))
    announced_at = db.Column(db.DateTime)

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

    article = db.relationship(
        "Article",
        backref="funding_rounds",
    )

    def __repr__(self):
        return f"<FundingRound {self.company_id}>"