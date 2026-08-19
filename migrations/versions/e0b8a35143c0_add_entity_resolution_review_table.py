"""Add entity resolution review table

Revision ID: e0b8a35143c0
Revises: 6d248eacb5aa
Create Date: 2026-08-19 21:14:49.346874

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0b8a35143c0'
down_revision = '6d248eacb5aa'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "entity_resolution_review" not in inspector.get_table_names():
        op.create_table(
            "entity_resolution_review",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("entity_type", sa.String(length=50), nullable=False),
            sa.Column("raw_name", sa.String(length=255), nullable=False),
            sa.Column("normalized_name", sa.String(length=255), nullable=True),
            sa.Column("candidate_name", sa.String(length=255), nullable=True),
            sa.Column("similarity_score", sa.Float(), nullable=True),
            sa.Column("resolution_status", sa.String(length=50), nullable=False),
            sa.Column("article_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("resolved_at", sa.DateTime(), nullable=True),
            sa.Column("decision", sa.String(length=50), nullable=True),
            sa.ForeignKeyConstraint(
                ["article_id"],
                ["article.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "entity_resolution_review" in inspector.get_table_names():
        op.drop_table("entity_resolution_review")