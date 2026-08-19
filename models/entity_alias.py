from models.article import db


class EntityAlias(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    alias = db.Column(
        db.String(300),
        unique=True,
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
            f"<EntityAlias {self.alias} "
            f"-> {self.canonical_name}>"
        )