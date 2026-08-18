from models.article import db

class Investor(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(300), unique=True, nullable=False)
    website = db.Column(db.String(500))
    description = db.Column(db.Text)

    headquarters = db.Column(db.String(200))

    def __repr__(self):
        return f"<Investor {self.name}>"