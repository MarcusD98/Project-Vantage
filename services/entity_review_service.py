from datetime import datetime

from models.article import db
from models.entity_alias import EntityAlias
from models.entity_resolution_review import EntityResolutionReview


REVIEWABLE_STATUSES = {
    "review",
    "strong_candidate",
}


def record_entity_resolution_review(
    article,
    resolution,
    entity_type,
):
    if resolution["status"] not in REVIEWABLE_STATUSES:
        return None

    candidate = resolution.get("candidate")

    candidate_name = (
        candidate.name
        if candidate is not None
        else None
    )

    existing_review = EntityResolutionReview.query.filter_by(
        entity_type=entity_type,
        raw_name=resolution["raw_name"],
        candidate_name=candidate_name,
        article_id=article.id if article else None,
        resolved_at=None,
    ).first()

    if existing_review is not None:
        return existing_review

    review = EntityResolutionReview(
        entity_type=entity_type,
        raw_name=resolution["raw_name"],
        normalized_name=resolution["normalized_name"],
        candidate_name=candidate_name,
        similarity_score=resolution["score"],
        resolution_status=resolution["status"],
        article=article,
    )

    db.session.add(review)

    return review


def approve_resolution_review(review_id):
    review = EntityResolutionReview.query.get(review_id)

    if review is None:
        return False

    if review.resolved_at is not None:
        return False

    if not review.candidate_name:
        return False

    existing_alias = EntityAlias.query.filter_by(
        alias=review.raw_name,
        entity_type=review.entity_type,
    ).first()

    if existing_alias is None:
        alias = EntityAlias(
            alias=review.raw_name,
            entity_type=review.entity_type,
            canonical_name=review.candidate_name,
        )

        db.session.add(alias)

    review.decision = "approved_match"
    review.resolved_at = datetime.now()

    db.session.commit()

    return True


def reject_resolution_review(review_id):
    review = EntityResolutionReview.query.get(review_id)

    if review is None:
        return False

    if review.resolved_at is not None:
        return False

    review.decision = "keep_separate"
    review.resolved_at = datetime.now()

    db.session.commit()

    return True