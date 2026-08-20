from datetime import datetime

from models.article import db
from models.entity_alias import EntityAlias
from models.entity_resolution_review import (
    EntityResolutionReview,
)


REVIEWABLE_STATUSES = {
    "review",
    "strong_candidate",
}


def record_entity_resolution_review(
    article,
    resolution,
    entity_type,
):
    """
    Persist a reviewable entity-resolution candidate.

    Candidate identity is stored using stable foreign keys.

    Transaction ownership belongs to the caller.
    """

    if (
        resolution["status"]
        not in REVIEWABLE_STATUSES
    ):
        return None

    candidate = resolution.get(
        "candidate"
    )

    candidate_name = (
        candidate.name
        if candidate is not None
        else None
    )

    candidate_company_id = None
    candidate_investor_id = None

    if candidate is not None:
        if entity_type == "company":
            candidate_company_id = (
                candidate.id
            )

        elif entity_type == "investor":
            candidate_investor_id = (
                candidate.id
            )

        else:
            raise ValueError(
                "Unsupported entity type: "
                f"{entity_type}"
            )

    query = (
        EntityResolutionReview.query
        .filter_by(
            entity_type=entity_type,
            raw_name=resolution[
                "raw_name"
            ],
            article_id=(
                article.id
                if article
                else None
            ),
            resolved_at=None,
        )
    )

    if entity_type == "company":
        query = query.filter_by(
            candidate_company_id=(
                candidate_company_id
            )
        )

    elif entity_type == "investor":
        query = query.filter_by(
            candidate_investor_id=(
                candidate_investor_id
            )
        )

    else:
        raise ValueError(
            "Unsupported entity type: "
            f"{entity_type}"
        )

    existing_review = query.first()

    if existing_review is not None:
        return existing_review

    review = EntityResolutionReview(
        entity_type=entity_type,
        raw_name=resolution[
            "raw_name"
        ],
        normalized_name=resolution[
            "normalized_name"
        ],

        # Temporary compatibility/display field.
        candidate_name=candidate_name,

        similarity_score=resolution[
            "score"
        ],
        resolution_status=resolution[
            "status"
        ],
        article=article,
    )

    if entity_type == "company":
        review.candidate_company = (
            candidate
        )

    elif entity_type == "investor":
        review.candidate_investor = (
            candidate
        )

    db.session.add(
        review
    )

    db.session.flush()

    return review


def approve_resolution_review(
    review_id,
):
    """
    Approve a resolution candidate and create an explicit alias
    pointing to the stable canonical entity.

    Transaction ownership belongs to the caller.
    """

    review = db.session.get(
        EntityResolutionReview,
        review_id,
    )

    if review is None:
        return False

    if review.resolved_at is not None:
        return False

    candidate = (
        review.candidate_entity
    )

    if candidate is None:
        return False

    existing_alias = (
        EntityAlias.query.filter_by(
            alias=review.raw_name,
            entity_type=review.entity_type,
        ).first()
    )

    if existing_alias is None:
        alias = EntityAlias(
            alias=review.raw_name,
            entity_type=review.entity_type,

            # Temporary compatibility/display field.
            canonical_name=(
                candidate.name
            ),
        )

        if (
            review.entity_type
            == "company"
        ):
            alias.canonical_company = (
                candidate
            )

        elif (
            review.entity_type
            == "investor"
        ):
            alias.canonical_investor = (
                candidate
            )

        else:
            raise ValueError(
                "Unsupported entity type: "
                f"{review.entity_type}"
            )

        db.session.add(
            alias
        )

    else:
        existing_target = (
            existing_alias.canonical_entity
        )

        if existing_target is None:
            return False

        # Never silently redirect an existing alias.
        if existing_target.id != candidate.id:
            return False

    review.decision = (
        "approved_match"
    )

    review.resolved_at = (
        datetime.now()
    )

    db.session.flush()

    return True


def reject_resolution_review(
    review_id,
):
    """
    Reject an entity-resolution candidate.

    Transaction ownership belongs to the caller.
    """

    review = db.session.get(
        EntityResolutionReview,
        review_id,
    )

    if review is None:
        return False

    if review.resolved_at is not None:
        return False

    review.decision = (
        "keep_separate"
    )

    review.resolved_at = (
        datetime.now()
    )

    db.session.flush()

    return True