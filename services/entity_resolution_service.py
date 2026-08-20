from models.company import Company
from models.investor import Investor
from models.entity_alias import EntityAlias

from services.entity_normalizer import (
    normalize_entity_name,
)
from services.entity_candidate_service import (
    similarity_score,
)


AUTO_MATCH_THRESHOLD = 0.92
REVIEW_THRESHOLD = 0.65


def _get_model(entity_type):
    if entity_type == "company":
        return Company

    if entity_type == "investor":
        return Investor

    raise ValueError(
        f"Unsupported entity type: {entity_type}"
    )


def _find_alias(
    raw_name,
    entity_type,
):
    """
    Resolve an explicit alias directly to its canonical entity.

    The stable foreign-key reference is authoritative.
    canonical_name is retained only as compatibility/display
    metadata.
    """

    alias = EntityAlias.query.filter_by(
        alias=raw_name.strip(),
        entity_type=entity_type,
    ).first()

    if alias is None:
        return None

    return alias.canonical_entity


def _find_exact_entity(
    name,
    entity_type,
):
    model = _get_model(
        entity_type
    )

    return model.query.filter_by(
        name=name
    ).first()


def _find_best_candidate(
    name,
    entity_type,
):
    model = _get_model(
        entity_type
    )

    best_entity = None
    best_score = 0

    for entity in model.query.all():
        score = similarity_score(
            name,
            entity.name,
        )

        if score > best_score:
            best_entity = entity
            best_score = score

    return (
        best_entity,
        best_score,
    )


def resolve_entity_name(
    raw_name,
    entity_type,
):
    """
    Resolve a raw extracted entity name against the Vantage
    knowledge base without automatically creating or merging
    entities.

    Explicit aliases resolve through stable foreign-key
    references.

    Possible statuses:

    alias
        A known alias maps directly to a canonical entity.

    exact
        The normalized name exactly matches an existing entity.

    strong_candidate
        A very high-confidence fuzzy candidate exists.

    review
        A plausible candidate exists but requires human review.

    new
        No sufficiently strong existing candidate was found.
    """

    if not raw_name:
        return {
            "status": "invalid",
            "raw_name": raw_name,
            "normalized_name": None,
            "canonical_name": None,
            "entity": None,
            "candidate": None,
            "score": None,
        }

    raw_name = raw_name.strip()

    # ---------------------------------------------------------
    # 1. Explicit aliases are the strongest signal.
    # ---------------------------------------------------------

    alias_entity = _find_alias(
        raw_name,
        entity_type,
    )

    if alias_entity is not None:
        return {
            "status": "alias",
            "raw_name": raw_name,
            "normalized_name":
                alias_entity.name,
            "canonical_name":
                alias_entity.name,
            "entity":
                alias_entity,
            "candidate":
                alias_entity,
            "score": 1.0,
        }

    # ---------------------------------------------------------
    # 2. Deterministic normalization.
    # ---------------------------------------------------------

    normalized_name = (
        normalize_entity_name(
            raw_name,
            entity_type=entity_type,
        )
    )

    if not normalized_name:
        return {
            "status": "invalid",
            "raw_name": raw_name,
            "normalized_name": None,
            "canonical_name": None,
            "entity": None,
            "candidate": None,
            "score": None,
        }

    # ---------------------------------------------------------
    # 3. Exact canonical match.
    # ---------------------------------------------------------

    exact_entity = _find_exact_entity(
        normalized_name,
        entity_type,
    )

    if exact_entity is not None:
        return {
            "status": "exact",
            "raw_name": raw_name,
            "normalized_name":
                normalized_name,
            "canonical_name":
                exact_entity.name,
            "entity":
                exact_entity,
            "candidate":
                exact_entity,
            "score": 1.0,
        }

    # ---------------------------------------------------------
    # 4. Fuzzy candidate search.
    # ---------------------------------------------------------

    candidate, score = (
        _find_best_candidate(
            normalized_name,
            entity_type,
        )
    )

    if candidate is None:
        return {
            "status": "new",
            "raw_name": raw_name,
            "normalized_name":
                normalized_name,
            "canonical_name":
                normalized_name,
            "entity": None,
            "candidate": None,
            "score": None,
        }

    if score >= AUTO_MATCH_THRESHOLD:
        return {
            "status":
                "strong_candidate",
            "raw_name":
                raw_name,
            "normalized_name":
                normalized_name,
            "canonical_name":
                candidate.name,
            "entity":
                None,
            "candidate":
                candidate,
            "score":
                score,
        }

    if score >= REVIEW_THRESHOLD:
        return {
            "status": "review",
            "raw_name": raw_name,
            "normalized_name":
                normalized_name,
            "canonical_name":
                normalized_name,
            "entity":
                None,
            "candidate":
                candidate,
            "score":
                score,
        }

    return {
        "status": "new",
        "raw_name": raw_name,
        "normalized_name":
            normalized_name,
        "canonical_name":
            normalized_name,
        "entity": None,
        "candidate":
            candidate,
        "score":
            score,
    }