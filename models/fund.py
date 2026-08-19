from models.article import db


class Fund(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(300),
        nullable=False,
    )

    investor_id = db.Column(
        db.Integer,
        db.ForeignKey("investor.id"),
        nullable=False,
    )

    strategy = db.Column(
        db.String(300),
        nullable=True,
    )

    geography = db.Column(
        db.String(200),
        nullable=True,
    )

    vintage_year = db.Column(
        db.Integer,
        nullable=True,
    )

    investor = db.relationship(
        "Investor",
        backref="funds",
    )

    def __repr__(self):
        return f"<Fund {self.name}>"