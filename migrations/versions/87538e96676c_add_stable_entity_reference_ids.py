"""add stable entity reference ids

Revision ID: 87538e96676c
Revises: 8fcd8775ad06
Create Date: 2026-08-20 04:01:23.491710

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "87538e96676c"
down_revision = "8fcd8775ad06"
branch_labels = None
depends_on = None


def upgrade():
    # ---------------------------------------------------------
    # 1. Add stable-reference columns first.
    #
    # They must initially be nullable because existing rows
    # still reference canonical entities by name.
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "entity_alias",
        schema=None,
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "canonical_company_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "canonical_investor_id",
                sa.Integer(),
                nullable=True,
            )
        )

    with op.batch_alter_table(
        "entity_resolution_review",
        schema=None,
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "candidate_company_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "candidate_investor_id",
                sa.Integer(),
                nullable=True,
            )
        )

    # ---------------------------------------------------------
    # 2. Backfill EntityAlias stable references.
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE entity_alias
        SET canonical_company_id = (
            SELECT company.id
            FROM company
            WHERE company.name = entity_alias.canonical_name
        )
        WHERE entity_type = 'company'
        """
    )

    op.execute(
        """
        UPDATE entity_alias
        SET canonical_investor_id = (
            SELECT investor.id
            FROM investor
            WHERE investor.name = entity_alias.canonical_name
        )
        WHERE entity_type = 'investor'
        """
    )

    # ---------------------------------------------------------
    # 3. Backfill EntityResolutionReview candidate references.
    #
    # Reviews without candidate_name legitimately remain NULL.
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE entity_resolution_review
        SET candidate_company_id = (
            SELECT company.id
            FROM company
            WHERE company.name = entity_resolution_review.candidate_name
        )
        WHERE entity_type = 'company'
          AND candidate_name IS NOT NULL
        """
    )

    op.execute(
        """
        UPDATE entity_resolution_review
        SET candidate_investor_id = (
            SELECT investor.id
            FROM investor
            WHERE investor.name = entity_resolution_review.candidate_name
        )
        WHERE entity_type = 'investor'
          AND candidate_name IS NOT NULL
        """
    )

    # ---------------------------------------------------------
    # 4. Validate alias backfill before enforcing constraints.
    #
    # Entity aliases must always resolve to a real canonical
    # entity. If historical data violates that invariant, fail
    # the migration instead of silently accepting bad data.
    # ---------------------------------------------------------

    connection = op.get_bind()

    unresolved_alias_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM entity_alias
            WHERE
                (
                    entity_type = 'company'
                    AND canonical_company_id IS NULL
                )
                OR
                (
                    entity_type = 'investor'
                    AND canonical_investor_id IS NULL
                )
            """
        )
    ).scalar()

    if unresolved_alias_count:
        raise RuntimeError(
            "Cannot migrate entity aliases: "
            f"{unresolved_alias_count} alias(es) could not "
            "be resolved to a canonical entity."
        )

    # ---------------------------------------------------------
    # 5. Add foreign keys and database invariants.
    # ---------------------------------------------------------

    with op.batch_alter_table(
        "entity_alias",
        schema=None,
    ) as batch_op:
        batch_op.create_foreign_key(
            "fk_entity_alias_canonical_company",
            "company",
            ["canonical_company_id"],
            ["id"],
        )

        batch_op.create_foreign_key(
            "fk_entity_alias_canonical_investor",
            "investor",
            ["canonical_investor_id"],
            ["id"],
        )

        batch_op.create_check_constraint(
            "ck_entity_alias_canonical_target",
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
        )

    with op.batch_alter_table(
        "entity_resolution_review",
        schema=None,
    ) as batch_op:
        batch_op.create_foreign_key(
            "fk_entity_resolution_review_candidate_company",
            "company",
            ["candidate_company_id"],
            ["id"],
        )

        batch_op.create_foreign_key(
            "fk_entity_resolution_review_candidate_investor",
            "investor",
            ["candidate_investor_id"],
            ["id"],
        )

        batch_op.create_check_constraint(
            "ck_entity_resolution_review_single_candidate",
            """
            NOT (
                candidate_company_id IS NOT NULL
                AND candidate_investor_id IS NOT NULL
            )
            """,
        )


def downgrade():
    with op.batch_alter_table(
        "entity_resolution_review",
        schema=None,
    ) as batch_op:
        batch_op.drop_constraint(
            "ck_entity_resolution_review_single_candidate",
            type_="check",
        )

        batch_op.drop_constraint(
            "fk_entity_resolution_review_candidate_investor",
            type_="foreignkey",
        )

        batch_op.drop_constraint(
            "fk_entity_resolution_review_candidate_company",
            type_="foreignkey",
        )

        batch_op.drop_column(
            "candidate_investor_id"
        )

        batch_op.drop_column(
            "candidate_company_id"
        )

    with op.batch_alter_table(
        "entity_alias",
        schema=None,
    ) as batch_op:
        batch_op.drop_constraint(
            "ck_entity_alias_canonical_target",
            type_="check",
        )

        batch_op.drop_constraint(
            "fk_entity_alias_canonical_investor",
            type_="foreignkey",
        )

        batch_op.drop_constraint(
            "fk_entity_alias_canonical_company",
            type_="foreignkey",
        )

        batch_op.drop_column(
            "canonical_investor_id"
        )

        batch_op.drop_column(
            "canonical_company_id"
        )