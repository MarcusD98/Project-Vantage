"""scope entity alias uniqueness by entity type

Revision ID: 8fcd8775ad06
Revises: e1fe52ccb576
Create Date: 2026-08-20 03:44:18.643446

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8fcd8775ad06"
down_revision = "e1fe52ccb576"
branch_labels = None
depends_on = None


def upgrade():
    """
    Replace the old global UNIQUE(alias) constraint with
    UNIQUE(entity_type, alias).

    SQLite represents the old unnamed uniqueness constraint as
    an internal sqlite_autoindex, which cannot safely be dropped
    directly. Recreating the small entity_alias table is the
    reliable way to change the constraint while preserving data.
    """

    op.create_table(
        "entity_alias_new",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "alias",
            sa.String(length=300),
            nullable=False,
        ),

        sa.Column(
            "entity_type",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "canonical_name",
            sa.String(length=300),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),

        sa.UniqueConstraint(
            "entity_type",
            "alias",
            name="uq_entity_alias_type_alias",
        ),
    )

    op.execute(
        """
        INSERT INTO entity_alias_new (
            id,
            alias,
            entity_type,
            canonical_name
        )
        SELECT
            id,
            alias,
            entity_type,
            canonical_name
        FROM entity_alias
        """
    )

    op.drop_table(
        "entity_alias"
    )

    op.rename_table(
        "entity_alias_new",
        "entity_alias",
    )


def downgrade():
    """
    Restore the old global UNIQUE(alias) constraint.

    Note that downgrade will fail if the database has acquired
    the same alias text for multiple entity types after this
    migration, because that data cannot satisfy UNIQUE(alias).
    """

    op.create_table(
        "entity_alias_old",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "alias",
            sa.String(length=300),
            nullable=False,
        ),

        sa.Column(
            "entity_type",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "canonical_name",
            sa.String(length=300),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),

        sa.UniqueConstraint(
            "alias",
        ),
    )

    op.execute(
        """
        INSERT INTO entity_alias_old (
            id,
            alias,
            entity_type,
            canonical_name
        )
        SELECT
            id,
            alias,
            entity_type,
            canonical_name
        FROM entity_alias
        """
    )

    op.drop_table(
        "entity_alias"
    )

    op.rename_table(
        "entity_alias_old",
        "entity_alias",
    )