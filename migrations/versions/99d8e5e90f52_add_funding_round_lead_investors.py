"""Add funding round lead investors

Revision ID: 99d8e5e90f52
Revises: 4dacb5c70e33
Create Date: 2026-08-19 17:59:40.308446

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99d8e5e90f52'
down_revision = '4dacb5c70e33'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "funding_round_lead_investors" not in inspector.get_table_names():
        op.create_table(
            "funding_round_lead_investors",
            sa.Column(
                "funding_round_id",
                sa.Integer(),
                nullable=False,
            ),
            sa.Column(
                "investor_id",
                sa.Integer(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["funding_round_id"],
                ["funding_round.id"],
            ),
            sa.ForeignKeyConstraint(
                ["investor_id"],
                ["investor.id"],
            ),
            sa.PrimaryKeyConstraint(
                "funding_round_id",
                "investor_id",
            ),
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "funding_round_lead_investors" in inspector.get_table_names():
        op.drop_table("funding_round_lead_investors")