from models.article import db

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(300), unique=True, nullable=False)
    website = db.Column(db.String(500))
    description = db.Column(db.Text)

    sector = db.Column(db.String(200))
    canonical_sector = db.Column(
        db.String(200),
        nullable=True,
    )
    headquarters = db.Column(db.String(200))

    city = db.Column(db.String(200))
    country = db.Column(db.String(200))
    founded_year = db.Column(db.Integer)

    def __repr__(self):
        return f"<Company {self.name}>"