from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Article class defined the shape of the database table
# 'unique=True' in url means database will not allow the same article URL to be stored twice

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(1000), unique=True, nullable=False)

    published_at = db.Column(db.DateTime)
    summary = db.Column(db.Text)
    category = db.Column(db.String(100))

    def __repr__(self):
        return f"<Article {self.title}>"