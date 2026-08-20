import pytest

from services.corpus_operations_service import (
    _get_live_source,
    _select_stored_articles,
    _validate_source,
)


def test_get_live_source():
    source = (
        _get_live_source(
            "TechCrunch"
        )
    )

    assert source is not None

    assert (
        source["name"]
        == "TechCrunch"
    )


def test_get_unknown_live_source():
    source = (
        _get_live_source(
            "Not Real"
        )
    )

    assert source is None


def test_validate_source():
    source = (
        _validate_source(
            "TechCrunch"
        )
    )

    assert (
        source["name"]
        == "TechCrunch"
    )


def test_validate_unknown_source_raises():
    with pytest.raises(
        ValueError
    ):
        _validate_source(
            "Not Real"
        )


def test_zero_limit_selects_no_articles():
    result = (
        _select_stored_articles(
            source_name="TechCrunch",
            category="Funding Round",
            limit=0,
            stats={},
            now=None,
        )
    )

    assert result == []


def test_negative_limit_selects_no_articles():
    result = (
        _select_stored_articles(
            source_name="TechCrunch",
            category="Funding Round",
            limit=-1,
            stats={},
            now=None,
        )
    )

    assert result == []