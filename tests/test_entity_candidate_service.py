from services.entity_candidate_service import (
    normalize_for_similarity,
    similarity_score,
)


def test_removes_generic_industry_words():
    assert normalize_for_similarity(
        "Sequoia Capital"
    ) == "sequoia"


def test_similar_names_score_highly():
    score = similarity_score(
        "Gallos Technologies",
        "Gallos Technology",
    )

    assert score > 0.8


def test_generic_words_do_not_create_false_match():
    score = similarity_score(
        "Sequoia Capital",
        "Ventura Capital",
    )

    assert score < 0.5


def test_venture_suffix_does_not_create_false_match():
    score = similarity_score(
        "NRW.Venture",
        "North Ventures",
    )

    assert score <= 0.5