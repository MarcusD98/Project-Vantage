from hypothesis import given
from hypothesis import strategies as st

from services.entity_normalizer import (
    clean_entity_name,
)
from services.taxonomy_service import (
    canonicalize_sector,
    normalize_sector_text,
)
from services.round_taxonomy_service import (
    canonicalize_round_type,
    normalize_round_type_text,
)


SAFE_TEXT = st.text(
    alphabet=st.characters(
        blacklist_categories=(
            "Cs",
        ),
    ),
    max_size=200,
)


@given(SAFE_TEXT)
def test_sector_text_normalization_is_idempotent(value):
    first = normalize_sector_text(value)
    second = normalize_sector_text(first)

    assert second == first


@given(SAFE_TEXT)
def test_round_type_normalization_is_idempotent(value):
    first = normalize_round_type_text(value)
    second = normalize_round_type_text(first)

    assert second == first


@given(SAFE_TEXT)
def test_sector_canonicalization_is_stable(value):
    canonical = canonicalize_sector(value)

    assert (
        canonicalize_sector(canonical)
        == canonical
    )


@given(SAFE_TEXT)
def test_round_type_canonicalization_is_stable(value):
    canonical = canonicalize_round_type(value)

    assert (
        canonicalize_round_type(canonical)
        == canonical
    )


@given(SAFE_TEXT)
def test_clean_entity_name_collapses_whitespace(value):
    cleaned = clean_entity_name(value)

    if cleaned is None:
        return

    assert "  " not in cleaned
    assert cleaned == cleaned.strip()


@given(SAFE_TEXT)
def test_clean_entity_name_is_idempotent(value):
    first = clean_entity_name(value)
    second = clean_entity_name(first)

    assert second == first
