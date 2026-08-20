from models.company import Company
from models.funding_round import FundingRound

from services.event_resolution_service import (
    funding_rounds_match,
)


def find_duplicate_funding_rounds():
    """
    Find historical FundingRound records that may represent the
    same real-world financing event.

    This audit uses the exact same matching engine as live
    ingestion.

    It performs no database writes and never merges records
    automatically.
    """

    duplicate_candidates = []

    companies = Company.query.order_by(
        Company.id
    ).all()

    for company in companies:
        funding_rounds = FundingRound.query.filter_by(
            company_id=company.id
        ).order_by(
            FundingRound.announced_at,
            FundingRound.id,
        ).all()

        if len(funding_rounds) < 2:
            continue

        for index, funding_round_a in enumerate(
            funding_rounds
        ):
            for funding_round_b in funding_rounds[
                index + 1:
            ]:
                if not funding_rounds_match(
                    funding_round_a,
                    funding_round_b,
                ):
                    continue

                duplicate_candidates.append(
                    {
                        "company": company,
                        "round_a": funding_round_a,
                        "round_b": funding_round_b,
                    }
                )

    return duplicate_candidates


def print_duplicate_funding_round_audit():
    """
    Print human-readable historical duplicate candidates.

    This function is diagnostic only.
    """

    duplicate_candidates = (
        find_duplicate_funding_rounds()
    )

    if not duplicate_candidates:
        print(
            "No potential historical duplicates found."
        )
        return

    print()
    print(
        "Potential historical funding duplicates"
    )
    print(
        "---------------------------------------"
    )

    for candidate in duplicate_candidates:
        company = candidate[
            "company"
        ]

        round_a = candidate[
            "round_a"
        ]

        round_b = candidate[
            "round_b"
        ]

        print()
        print(
            company.name
        )

        _print_round(
            "A",
            round_a,
        )

        _print_round(
            "B",
            round_b,
        )


def _print_round(
    label,
    funding_round,
):
    """
    Print one FundingRound and its supporting evidence.
    """

    print(
        "   ",
        label,
        "| Round ID:",
        funding_round.id,
        "|",
        funding_round.amount,
        funding_round.currency,
        "|",
        funding_round.round_type,
        "|",
        funding_round.announced_at,
        "| Sources:",
        len(funding_round.articles),
    )

    for article in funding_round.articles:
        print(
            "       ",
            article.source,
            "|",
            article.title,
        )