import re
from difflib import SequenceMatcher

from models.company import Company
from models.investor import Investor


GENERIC_ENTITY_WORDS = {
    "capital",
    "ventures",
    "venture",
    "partners",
    "partner",
    "investments",
    "investment",
    "fund",
    "funds",
    "group",
    "holdings",
    "management",
    "technologies",
    "technology",
    "labs",
    "lab",
}


def normalize_for_similarity(name):
    if not name:
        return ""

    normalized = name.lower()

    normalized = re.sub(
        r"[^a-z0-9\s]",
        " ",
        normalized,
    )

    tokens = normalized.split()

    distinctive_tokens = [
        token
        for token in tokens
        if token not in GENERIC_ENTITY_WORDS
    ]

    return " ".join(distinctive_tokens)


def similarity_score(name_a, name_b):
    normalized_a = normalize_for_similarity(name_a)
    normalized_b = normalize_for_similarity(name_b)

    if not normalized_a or not normalized_b:
        return 0.0

    return SequenceMatcher(
        None,
        normalized_a,
        normalized_b,
    ).ratio()


def find_company_duplicate_candidates(
    threshold=0.82,
):
    companies = Company.query.order_by(
        Company.name
    ).all()

    candidates = []

    for index, company_a in enumerate(companies):
        for company_b in companies[index + 1:]:
            score = similarity_score(
                company_a.name,
                company_b.name,
            )

            if score >= threshold:
                candidates.append(
                    {
                        "entity_type": "company",
                        "entity_a": company_a,
                        "entity_b": company_b,
                        "score": round(score, 3),
                    }
                )

    return sorted(
        candidates,
        key=lambda candidate: candidate["score"],
        reverse=True,
    )


def find_investor_duplicate_candidates(
    threshold=0.82,
):
    investors = Investor.query.order_by(
        Investor.name
    ).all()

    candidates = []

    for index, investor_a in enumerate(investors):
        for investor_b in investors[index + 1:]:
            score = similarity_score(
                investor_a.name,
                investor_b.name,
            )

            if score >= threshold:
                candidates.append(
                    {
                        "entity_type": "investor",
                        "entity_a": investor_a,
                        "entity_b": investor_b,
                        "score": round(score, 3),
                    }
                )

    return sorted(
        candidates,
        key=lambda candidate: candidate["score"],
        reverse=True,
    )