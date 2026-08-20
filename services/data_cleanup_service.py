from models.company import Company
from models.funding_round import FundingRound

from services.event_resolution_service import (
    funding_rounds_match,
)
from services.event_reconciliation_service import (
    reconcile_funding_round_pair,
)


MAX_RECONCILIATION_MERGES = 1000


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


def build_duplicate_candidate_summary(
    candidate,
):
    """
    Convert a duplicate candidate into stable primitive data.

    This is useful for CLI output and avoids returning database
    objects that may later be deleted during reconciliation.
    """

    company = candidate["company"]
    round_a = candidate["round_a"]
    round_b = candidate["round_b"]

    return {
        "company_id": company.id,
        "company_name": company.name,

        "round_a_id": round_a.id,
        "round_a_amount": round_a.amount,
        "round_a_currency": round_a.currency,
        "round_a_type": round_a.round_type,
        "round_a_announced_at": round_a.announced_at,
        "round_a_source_count": len(
            round_a.articles
        ),

        "round_b_id": round_b.id,
        "round_b_amount": round_b.amount,
        "round_b_currency": round_b.currency,
        "round_b_type": round_b.round_type,
        "round_b_announced_at": round_b.announced_at,
        "round_b_source_count": len(
            round_b.articles
        ),
    }


def reconcile_historical_funding_rounds(
    *,
    apply=False,
    max_merges=MAX_RECONCILIATION_MERGES,
):
    """
    Audit or reconcile historical funding-event duplicates.

    Dry-run mode:
        apply=False

        Returns duplicate candidates without mutating the
        database.

    Apply mode:
        apply=True

        Reconciles one candidate pair at a time, then re-runs
        duplicate detection before selecting the next pair.

        Re-querying after every merge is intentional. Candidate
        pairs can overlap, and a previously captured SQLAlchemy
        object may have been deleted by an earlier merge.

    This function never commits.

    Transaction ownership belongs to the caller.
    """

    initial_candidates = (
        find_duplicate_funding_rounds()
    )

    report = {
        "mode": (
            "apply"
            if apply
            else "dry_run"
        ),
        "initial_candidates": len(
            initial_candidates
        ),
        "merged": 0,
        "remaining_candidates": 0,
        "candidates": [
            build_duplicate_candidate_summary(
                candidate
            )
            for candidate in initial_candidates
        ],
        "merges": [],
    }

    if not apply:
        report["remaining_candidates"] = len(
            initial_candidates
        )

        return report

    merge_count = 0

    while True:
        candidates = (
            find_duplicate_funding_rounds()
        )

        if not candidates:
            break

        if merge_count >= max_merges:
            raise RuntimeError(
                "Historical reconciliation exceeded "
                f"the safety limit of {max_merges} merges."
            )

        # Always operate on the current database state.
        # After the merge we re-run candidate detection.
        candidate = candidates[0]

        round_a = candidate[
            "round_a"
        ]

        round_b = candidate[
            "round_b"
        ]

        round_a_id = round_a.id
        round_b_id = round_b.id
        company_name = candidate[
            "company"
        ].name

        reconciled_round = (
            reconcile_funding_round_pair(
                round_a,
                round_b,
            )
        )

        if reconciled_round is None:
            raise RuntimeError(
                "Duplicate candidate could not be "
                "reconciled even though it was produced "
                "by the shared event matcher."
            )

        surviving_round_id = (
            reconciled_round.id
        )

        if surviving_round_id == round_a_id:
            removed_round_id = (
                round_b_id
            )
        else:
            removed_round_id = (
                round_a_id
            )

        report["merges"].append(
            {
                "company_name":
                    company_name,

                "surviving_round_id":
                    surviving_round_id,

                "removed_round_id":
                    removed_round_id,
            }
        )

        merge_count += 1

    report["merged"] = merge_count

    remaining_candidates = (
        find_duplicate_funding_rounds()
    )

    report["remaining_candidates"] = len(
        remaining_candidates
    )

    return report


def print_duplicate_funding_round_audit():
    """
    Print human-readable historical duplicate candidates.

    Diagnostic only.
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