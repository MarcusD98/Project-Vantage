from models.article import db


class EntityAlias(db.Model):
    __tablename__ = "entity_alias"

    __table_args__ = (
        db.UniqueConstraint(
            "entity_type",
            "alias",
            name="uq_entity_alias_type_alias",
        ),
        db.CheckConstraint(
            """
            (
                entity_type = 'company'
                AND canonical_company_id IS NOT NULL
                AND canonical_investor_id IS NULL
            )
            OR
            (
                entity_type = 'investor'
                AND canonical_investor_id IS NOT NULL
                AND canonical_company_id IS NULL
            )
            """,
            name="ck_entity_alias_canonical_target",
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    alias = db.Column(
        db.String(300),
        nullable=False,
    )

    entity_type = db.Column(
        db.String(50),
        nullable=False,
    )

    # Temporary compatibility field.
    # We keep this while migrating application logic to stable IDs.
    canonical_name = db.Column(
        db.String(300),
        nullable=False,
    )

    canonical_company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=True,
    )

    canonical_investor_id = db.Column(
        db.Integer,
        db.ForeignKey("investor.id"),
        nullable=True,
    )

    canonical_company = db.relationship(
        "Company",
        foreign_keys=[
            canonical_company_id
        ],
    )

    canonical_investor = db.relationship(
        "Investor",
        foreign_keys=[
            canonical_investor_id
        ],
    )

    @property
    def canonical_entity(self):
        if self.entity_type == "company":
            return self.canonical_company

        if self.entity_type == "investor":
            return self.canonical_investor

        return None

    def __repr__(self):
        return (
            f"<EntityAlias "
            f"{self.entity_type}: "
            f"{self.alias} "
            f"-> {self.canonical_name}>"
        )