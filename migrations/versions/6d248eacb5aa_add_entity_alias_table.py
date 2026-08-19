"""Add entity alias table

Revision ID: 6d248eacb5aa
Revises: db57bcbd9325
Create Date: 2026-08-19 19:24:43.646089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d248eacb5aa'
down_revision = 'db57bcbd9325'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "entity_alias" not in inspector.get_table_names():
        op.create_table(
            "entity_alias",
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
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("alias"),
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "entity_alias" in inspector.get_table_names():
        op.drop_table("entity_alias")
