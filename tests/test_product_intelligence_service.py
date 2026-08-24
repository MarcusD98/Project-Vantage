from types import SimpleNamespace

from services.product_intelligence_service import (
    select_investor_changes,
)


def _ranking(
    name,
    *,
    current,
    previous,
    confidence,
    status="supported",
):
    return {
        "investor":
            SimpleNamespace(
                name=name
            ),

        "current_investments":
            current,

        "previous_investments":
            previous,

        "investment_delta":
            current - previous,

        "current_leads":
            0,

        "all_time_investments":
            current + previous,

        "trend_status":
            status,

        "trend_confidence":
            confidence,
    }


def test_investor_changes_exclude_insufficient_comparisons():
    rankings = [
        _ranking(
            "Supported",
            current=6,
            previous=3,
            confidence="corpus_supported",
        ),
        _ranking(
            "Insufficient",
            current=8,
            previous=0,
            confidence="insufficient",
            status="insufficient",
        ),
    ]

    result = (
        select_investor_changes(
            rankings
        )
    )

    assert [
        item["investor"].name
        for item in result
    ] == [
        "Supported"
    ]


def test_investor_changes_exclude_flat_activity():
    rankings = [
        _ranking(
            "Flat",
            current=4,
            previous=4,
            confidence="corpus_supported",
        ),
    ]

    assert (
        select_investor_changes(
            rankings
        )
        == []
    )


def test_corpus_supported_changes_rank_before_observational():
    rankings = [
        _ranking(
            "Observational",
            current=9,
            previous=2,
            confidence="observational",
        ),
        _ranking(
            "Corpus Supported",
            current=5,
            previous=3,
            confidence="corpus_supported",
        ),
    ]

    result = (
        select_investor_changes(
            rankings
        )
    )

    assert (
        result[0]["investor"].name
        == "Corpus Supported"
    )


def test_changes_rank_by_absolute_delta_within_confidence():
    rankings = [
        _ranking(
            "Smaller",
            current=5,
            previous=3,
            confidence="corpus_supported",
        ),
        _ranking(
            "Larger",
            current=7,
            previous=3,
            confidence="corpus_supported",
        ),
        _ranking(
            "Declining",
            current=2,
            previous=6,
            confidence="corpus_supported",
        ),
    ]

    result = (
        select_investor_changes(
            rankings
        )
    )

    assert {
        result[0]["investor"].name,
        result[1]["investor"].name,
    } == {
        "Larger",
        "Declining",
    }

    assert (
        abs(
            result[0][
                "investment_delta"
            ]
        )
        == 4
    )
