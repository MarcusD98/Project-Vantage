from models.article import db


class EntityAlias(db.Model):
    __tablename__ = "entity_alias"

    __table_args__ = (
        db.UniqueConstraint(
            "entity_type",
            "alias",
            name="uq_entity_alias_type_alias",
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

    canonical_name = db.Column(
        db.String(300),
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<EntityAlias "
            f"{self.entity_type}: "
            f"{self.alias} "
            f"-> {self.canonical_name}>"
        )