from models.article import db

from models.company import Company
from models.entity_alias import EntityAlias
from models.investor import Investor

from models.entity_resolution_review import (
    EntityResolutionReview,
)


def _upsert_entity_alias(
    alias_name,
    entity_type,
    canonical_entity,
):
    """
    Persist a durable alias pointing to a canonical entity.

    This prevents a merged entity from being recreated by a
    future extraction using the old name.
    """

    if not alias_name:
        return None

    alias_name = (
        str(alias_name)
        .strip()
    )

    if not alias_name:
        return None

    if (
        alias_name.casefold()
        == canonical_entity.name.casefold()
    ):
        return None

    alias = (
        EntityAlias.query
        .filter(
            EntityAlias.entity_type
            == entity_type,

            EntityAlias.alias.ilike(
                alias_name
            ),
        )
        .first()
    )

    if alias is None:
        alias = EntityAlias(
            alias=alias_name,
            entity_type=entity_type,
            canonical_name=(
                canonical_entity.name
            ),
        )

        db.session.add(
            alias
        )

    alias.canonical_name = (
        canonical_entity.name
    )

    if entity_type == "investor":
        alias.canonical_investor = (
            canonical_entity
        )

        alias.canonical_company = None

    elif entity_type == "company":
        alias.canonical_company = (
            canonical_entity
        )

        alias.canonical_investor = None

    else:
        raise ValueError(
            "Unsupported entity type: "
            f"{entity_type}"
        )

    return alias


def _repoint_investor_aliases(
    alias_investor,
    canonical_investor,
):
    """
    Preserve aliases that already pointed at an investor being
    merged.
    """

    aliases = (
        EntityAlias.query
        .filter_by(
            entity_type="investor",
            canonical_investor_id=(
                alias_investor.id
            ),
        )
        .all()
    )

    for alias in aliases:
        alias.canonical_investor = (
            canonical_investor
        )

        alias.canonical_name = (
            canonical_investor.name
        )


def _repoint_company_aliases(
    alias_company,
    canonical_company,
):
    """
    Preserve aliases that already pointed at a company being
    merged.
    """

    aliases = (
        EntityAlias.query
        .filter_by(
            entity_type="company",
            canonical_company_id=(
                alias_company.id
            ),
        )
        .all()
    )

    for alias in aliases:
        alias.canonical_company = (
            canonical_company
        )

        alias.canonical_name = (
            canonical_company.name
        )


def _repoint_investor_reviews(
    alias_investor,
    canonical_investor,
):
    """
    Preserve entity-resolution review candidates when an
    investor is merged into its canonical entity.
    """

    reviews = (
        EntityResolutionReview.query
        .filter_by(
            candidate_investor_id=(
                alias_investor.id
            ),
        )
        .all()
    )

    for review in reviews:
        review.candidate_investor = (
            canonical_investor
        )

        review.candidate_name = (
            canonical_investor.name
        )


def _repoint_company_reviews(
    alias_company,
    canonical_company,
):
    """
    Preserve entity-resolution review candidates when a
    company is merged into its canonical entity.
    """

    reviews = (
        EntityResolutionReview.query
        .filter_by(
            candidate_company_id=(
                alias_company.id
            ),
        )
        .all()
    )

    for review in reviews:
        review.candidate_company = (
            canonical_company
        )

        review.candidate_name = (
            canonical_company.name
        )


def merge_investors(
    alias_name,
    canonical_name,
):
    """
    Merge one duplicate investor into a canonical investor.

    Responsibilities:
    - preserve canonical metadata
    - move investment relationships
    - move lead-investor relationships
    - repoint existing aliases
    - create a durable alias for the merged name
    - delete the duplicate investor
    """

    if not alias_name:
        return False

    if not canonical_name:
        return False

    alias_name = (
        str(alias_name)
        .strip()
    )

    canonical_name = (
        str(canonical_name)
        .strip()
    )

    if not alias_name:
        return False

    if not canonical_name:
        return False

    if (
        alias_name.casefold()
        == canonical_name.casefold()
    ):
        return False

    alias_investor = (
        Investor.query
        .filter_by(
            name=alias_name
        )
        .first()
    )

    canonical_investor = (
        Investor.query
        .filter_by(
            name=canonical_name
        )
        .first()
    )

    if alias_investor is None:
        return False

    try:
        if canonical_investor is None:
            canonical_investor = Investor(
                name=canonical_name
            )

            db.session.add(
                canonical_investor
            )

            db.session.flush()

        # -------------------------------------------------
        # Preserve useful investor metadata
        # -------------------------------------------------

        if (
            not canonical_investor.website
            and alias_investor.website
        ):
            canonical_investor.website = (
                alias_investor.website
            )

        if (
            not canonical_investor.description
            and alias_investor.description
        ):
            canonical_investor.description = (
                alias_investor.description
            )

        if (
            not canonical_investor.headquarters
            and alias_investor.headquarters
        ):
            canonical_investor.headquarters = (
                alias_investor.headquarters
            )

        # -------------------------------------------------
        # Move normal investment relationships
        # -------------------------------------------------

        for funding_round in list(
            alias_investor.funding_rounds
        ):
            if (
                canonical_investor
                not in funding_round.investors
            ):
                funding_round.investors.append(
                    canonical_investor
                )

            if (
                alias_investor
                in funding_round.investors
            ):
                funding_round.investors.remove(
                    alias_investor
                )

        # -------------------------------------------------
        # Move lead relationships
        # -------------------------------------------------

        for funding_round in list(
            alias_investor.led_funding_rounds
        ):
            if (
                canonical_investor
                not in
                funding_round.lead_investors
            ):
                funding_round.lead_investors.append(
                    canonical_investor
                )

            if (
                alias_investor
                in
                funding_round.lead_investors
            ):
                funding_round.lead_investors.remove(
                    alias_investor
                )

        # -------------------------------------------------
        # Preserve previous alias graph
        # -------------------------------------------------

        _repoint_investor_aliases(
            alias_investor=alias_investor,
            canonical_investor=(
                canonical_investor
            ),
        )

        _repoint_investor_reviews(
            alias_investor=alias_investor,
            canonical_investor=(
                canonical_investor
            ),
        )

        # The duplicate entity's own former name now becomes
        # an explicit alias.
        _upsert_entity_alias(
            alias_name=alias_name,
            entity_type="investor",
            canonical_entity=(
                canonical_investor
            ),
        )

        db.session.delete(
            alias_investor
        )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return True


def merge_companies(
    alias_name,
    canonical_name,
):
    """
    Merge one duplicate company into a canonical company while
    preserving relationships, metadata and aliases.
    """

    if not alias_name:
        return False

    if not canonical_name:
        return False

    alias_name = (
        str(alias_name)
        .strip()
    )

    canonical_name = (
        str(canonical_name)
        .strip()
    )

    if not alias_name:
        return False

    if not canonical_name:
        return False

    if (
        alias_name.casefold()
        == canonical_name.casefold()
    ):
        return False

    alias_company = (
        Company.query
        .filter_by(
            name=alias_name
        )
        .first()
    )

    canonical_company = (
        Company.query
        .filter_by(
            name=canonical_name
        )
        .first()
    )

    if alias_company is None:
        return False

    try:
        if canonical_company is None:
            canonical_company = Company(
                name=canonical_name
            )

            db.session.add(
                canonical_company
            )

            db.session.flush()

        # -------------------------------------------------
        # Preserve useful metadata
        # -------------------------------------------------

        if (
            not canonical_company.website
            and alias_company.website
        ):
            canonical_company.website = (
                alias_company.website
            )

        if (
            not canonical_company.description
            and alias_company.description
        ):
            canonical_company.description = (
                alias_company.description
            )

        if (
            not canonical_company.sector
            and alias_company.sector
        ):
            canonical_company.sector = (
                alias_company.sector
            )

        if (
            not canonical_company.canonical_sector
            and alias_company.canonical_sector
        ):
            canonical_company.canonical_sector = (
                alias_company.canonical_sector
            )

        if (
            not canonical_company.headquarters
            and alias_company.headquarters
        ):
            canonical_company.headquarters = (
                alias_company.headquarters
            )

        if (
            not canonical_company.city
            and alias_company.city
        ):
            canonical_company.city = (
                alias_company.city
            )

        if (
            not canonical_company.country
            and alias_company.country
        ):
            canonical_company.country = (
                alias_company.country
            )

        if (
            not canonical_company.founded_year
            and alias_company.founded_year
        ):
            canonical_company.founded_year = (
                alias_company.founded_year
            )

        # -------------------------------------------------
        # Move funding events
        # -------------------------------------------------

        for funding_round in list(
            alias_company.funding_rounds
        ):
            funding_round.company = (
                canonical_company
            )

        # -------------------------------------------------
        # Preserve aliases
        # -------------------------------------------------

        _repoint_company_aliases(
            alias_company=alias_company,
            canonical_company=(
                canonical_company
            ),
        )

        _repoint_company_reviews(
            alias_company=alias_company,
            canonical_company=(
                canonical_company
            ),
        )

        _upsert_entity_alias(
            alias_name=alias_name,
            entity_type="company",
            canonical_entity=(
                canonical_company
            ),
        )

        db.session.delete(
            alias_company
        )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return True


def remove_invalid_investor(
    investor_name,
):
    investor = (
        Investor.query
        .filter_by(
            name=investor_name
        )
        .first()
    )

    if investor is None:
        return False

    try:
        for funding_round in list(
            investor.funding_rounds
        ):
            if (
                investor
                in funding_round.investors
            ):
                funding_round.investors.remove(
                    investor
                )

        for funding_round in list(
            investor.led_funding_rounds
        ):
            if (
                investor
                in
                funding_round.lead_investors
            ):
                funding_round.lead_investors.remove(
                    investor
                )

        db.session.delete(
            investor
        )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return True


def rename_company(
    current_name,
    canonical_name,
):
    company = (
        Company.query
        .filter_by(
            name=current_name
        )
        .first()
    )

    if company is None:
        return False

    existing_company = (
        Company.query
        .filter_by(
            name=canonical_name
        )
        .first()
    )

    if existing_company is not None:
        return False

    try:
        old_name = company.name

        company.name = (
            canonical_name
        )

        db.session.flush()

        _upsert_entity_alias(
            alias_name=old_name,
            entity_type="company",
            canonical_entity=company,
        )

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return True