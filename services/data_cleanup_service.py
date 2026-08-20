from collections import defaultdict

from models.company import Company
from models.funding_round import FundingRound


def find_duplicate_funding_rounds():
    """
    Find funding rounds that may represent the same real-world event.

    This is intentionally conservative. It does not modify data.
    """

    duplicate_groups = []

    companies = Company.query.all()

    for company in companies:
        rounds = FundingRound.query.filter_by(
            company_id=company.id
        ).order_by(
            FundingRound.announced_at
        ).all()

        if len(rounds) < 2:
            continue

        grouped = defaultdict(list)

        for funding_round in rounds:
            key = (
                funding_round.canonical_round_type,
                funding_round.currency,
                funding_round.amount,
            )

            grouped[key].append(
                funding_round
            )

        for key, matching_rounds in grouped.items():
            if len(matching_rounds) < 2:
                continue

            duplicate_groups.append({
                "company": company,
                "canonical_round_type": key[0],
                "currency": key[1],
                "amount": key[2],
                "rounds": matching_rounds,
            })

    return duplicate_groups


def print_duplicate_funding_round_audit():
    duplicate_groups = (
        find_duplicate_funding_rounds()
    )

    if not duplicate_groups:
        print(
            "No potential historical duplicates found."
        )
        return

    print()
    print("Potential historical funding duplicates")
    print("---------------------------------------")

    for group in duplicate_groups:
        print()
        print(
            group["company"].name,
            "|",
            group["canonical_round_type"],
            "|",
            group["amount"],
            group["currency"],
        )

        for funding_round in group["rounds"]:
            print(
                "   ",
                "Round ID:",
                funding_round.id,
                "| Date:",
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