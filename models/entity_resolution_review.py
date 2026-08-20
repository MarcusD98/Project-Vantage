from models.article import db


class EntityResolutionReview(db.Model):
    __tablename__ = "entity_resolution_review"

    __table_args__ = (
        db.CheckConstraint(
            """
            NOT (
                candidate_company_id IS NOT NULL
                AND candidate_investor_id IS NOT NULL
            )
            """,
            name="ck_entity_resolution_review_single_candidate",
        ),
    )

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

    # Temporary compatibility field.
    candidate_name = db.Column(
        db.String(255),
        nullable=True,
    )

    candidate_company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=True,
    )

    candidate_investor_id = db.Column(
        db.Integer,
        db.ForeignKey("investor.id"),
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

    candidate_company = db.relationship(
        "Company",
        foreign_keys=[
            candidate_company_id
        ],
    )

    candidate_investor = db.relationship(
        "Investor",
        foreign_keys=[
            candidate_investor_id
        ],
    )

    @property
    def candidate_entity(self):
        if self.entity_type == "company":
            return self.candidate_company

        if self.entity_type == "investor":
            return self.candidate_investor

        return None

    def __repr__(self):
        return (
            f"<EntityResolutionReview "
            f"{self.raw_name} -> {self.candidate_name}>"
        )