from models.article import db

class EntityResolutionReview(db.Model):
    __tablename__ = "entity_resolution_review"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    entity_type = db.Column(
        db.String(50),
        nullable=False,
    )

    raw_name = db.Column(
        db.String(255),
        nullable=False,
    )

    normalized_name = db.Column(
        db.String(255),
        nullable=True,
    )

    candidate_name = db.Column(
        db.String(255),
        nullable=True,
    )

    similarity_score = db.Column(
        db.Float,
        nullable=True,
    )

    resolution_status = db.Column(
        db.String(50),
        nullable=False,
    )

    article_id = db.Column(
        db.Integer,
        db.ForeignKey("article.id"),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=db.func.now(),
        nullable=False,
    )

    resolved_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    decision = db.Column(
        db.String(50),
        nullable=True,
    )

    article = db.relationship(
        "Article",
        backref="entity_resolution_reviews",
    )

    def __repr__(self):
        return (
            f"<EntityResolutionReview "
            f"{self.raw_name} -> {self.candidate_name}>"
        )