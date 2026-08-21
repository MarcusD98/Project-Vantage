from models.article import (
    Article,
    db,
)

from services.compound_evidence_service import (
    get_compound_funding_reasons,
    get_multi_round_review_reasons,
)


def _unique_rounds_for_article(article):
    rounds = {}

    for funding_round in (
        article.primary_funding_rounds
    ):
        rounds[
            funding_round.id
        ] = funding_round

    for funding_round in (
        article.supported_funding_rounds
    ):
        rounds[
            funding_round.id
        ] = funding_round

    return list(
        rounds.values()
    )


def _unique_evidence_articles(funding_round):
    articles = {}

    if funding_round.article is not None:
        articles[
            funding_round.article.id
        ] = funding_round.article

    for article in funding_round.articles:
        articles[
            article.id
        ] = article

    return list(
        articles.values()
    )


def _round_audit_row(
    article,
    blocking_reasons,
    review_reasons,
    funding_round,
):
    evidence_articles = (
        _unique_evidence_articles(
            funding_round
        )
    )

    other_evidence = [
        evidence
        for evidence in evidence_articles
        if evidence.id
        != article.id
    ]

    company = funding_round.company

    if blocking_reasons:
        recommended_action = (
            "automatic_repair_candidate"
            if not other_evidence
            else "manual_review"
        )
    else:
        recommended_action = (
            "review_only"
        )

    return {
        "article_id":
            article.id,
        "source":
            article.source,
        "published_at":
            article.published_at,
        "title":
            article.title,
        "url":
            article.url,
        "blocking_reasons":
            blocking_reasons,
        "review_reasons":
            review_reasons,
        "round_id":
            funding_round.id,
        "company":
            (
                company.name
                if company is not None
                else "Unknown"
            ),
        "round_type":
            (
                funding_round.canonical_round_type
                or funding_round.round_type
                or "Unknown"
            ),
        "amount":
            funding_round.amount,
        "currency":
            funding_round.currency,
        "announced_at":
            funding_round.announced_at,
        "evidence_count":
            len(
                evidence_articles
            ),
        "other_evidence_count":
            len(
                other_evidence
            ),
        "other_evidence_sources":
            sorted(
                {
                    evidence.source
                    for evidence
                    in other_evidence
                    if evidence.source
                },
                key=str.casefold,
            ),
        "recommended_action":
            recommended_action,
    }


def audit_multi_round_integrity(
    source_name=None,
):
    """
    Audit persisted Funding Round evidence for multi-round risk.

    Crucial distinction:

    - blocking reasons are high-confidence enough for automatic
      quarantine;
    - review reasons are diagnostic only and never prove that an
      attached canonical round is invalid.

    The audit is read-only.
    """

    query = (
        Article.query
        .filter(
            Article.category
            == "Funding Round"
        )
        .order_by(
            Article.published_at.desc(),
            Article.id.desc(),
        )
    )

    if source_name:
        query = query.filter(
            Article.source
            == source_name
        )

    suspect_articles = []
    rows = []

    for article in query.all():
        blocking_reasons = (
            get_compound_funding_reasons(
                article
            )
        )

        review_reasons = (
            get_multi_round_review_reasons(
                article
            )
        )

        if not review_reasons:
            continue

        suspect_articles.append(
            article
        )

        rounds = (
            _unique_rounds_for_article(
                article
            )
        )

        if not rounds:
            rows.append(
                {
                    "article_id":
                        article.id,
                    "source":
                        article.source,
                    "published_at":
                        article.published_at,
                    "title":
                        article.title,
                    "url":
                        article.url,
                    "blocking_reasons":
                        blocking_reasons,
                    "review_reasons":
                        review_reasons,
                    "round_id":
                        None,
                    "company":
                        None,
                    "round_type":
                        None,
                    "amount":
                        None,
                    "currency":
                        None,
                    "announced_at":
                        None,
                    "evidence_count":
                        0,
                    "other_evidence_count":
                        0,
                    "other_evidence_sources":
                        [],
                    "recommended_action":
                        (
                            "already_quarantined"
                            if blocking_reasons
                            else "no_attached_round"
                        ),
                }
            )

            continue

        for funding_round in rounds:
            rows.append(
                _round_audit_row(
                    article=article,
                    blocking_reasons=(
                        blocking_reasons
                    ),
                    review_reasons=(
                        review_reasons
                    ),
                    funding_round=(
                        funding_round
                    ),
                )
            )

    attached_rows = [
        row
        for row in rows
        if row["round_id"]
        is not None
    ]

    automatic_repair_rows = [
        row
        for row in attached_rows
        if row[
            "recommended_action"
        ]
        == "automatic_repair_candidate"
    ]

    review_only_rows = [
        row
        for row in attached_rows
        if row[
            "recommended_action"
        ]
        == "review_only"
    ]

    manual_review_rows = [
        row
        for row in attached_rows
        if row[
            "recommended_action"
        ]
        == "manual_review"
    ]

    return {
        "source":
            source_name,
        "suspect_articles":
            len(
                suspect_articles
            ),
        "attached_rounds":
            len(
                attached_rows
            ),
        "automatic_repair_candidates":
            len(
                automatic_repair_rows
            ),
        "review_only_candidates":
            len(
                review_only_rows
            ),
        "manual_review_candidates":
            len(
                manual_review_rows
            ),
        "rows":
            rows,
    }


def plan_multi_round_repair(
    article_id,
    confirmed_invalid=False,
):
    """
    Build a repair plan for one reviewed article.

    Automatic application is allowed when either:

    - the article has a high-confidence blocking reason; or
    - the caller explicitly confirms that a review-only article
      has been manually verified as invalid.

    In both cases every attached canonical round must be supported
    solely by the suspect article. Multi-source events are never
    automatically deleted by this service.
    """

    article = db.session.get(
        Article,
        article_id,
    )

    if article is None:
        raise ValueError(
            f"Article not found: {article_id}"
        )

    blocking_reasons = (
        get_compound_funding_reasons(
            article
        )
    )

    review_reasons = (
        get_multi_round_review_reasons(
            article
        )
    )

    if not review_reasons:
        raise ValueError(
            "Article has no multi-round integrity signal."
        )

    rounds = (
        _unique_rounds_for_article(
            article
        )
    )

    rows = [
        _round_audit_row(
            article=article,
            blocking_reasons=(
                blocking_reasons
            ),
            review_reasons=(
                review_reasons
            ),
            funding_round=(
                funding_round
            ),
        )
        for funding_round in rounds
    ]

    has_shared_support = any(
        row[
            "other_evidence_count"
        ]
        > 0
        for row in rows
    )

    if not rounds:
        can_apply = False
        reason = (
            "No canonical FundingRound is attached to this article."
        )

    elif has_shared_support:
        can_apply = False
        reason = (
            "At least one attached FundingRound has independent "
            "supporting evidence. Automatic deletion is refused."
        )

    elif blocking_reasons:
        can_apply = True
        reason = None

    elif confirmed_invalid:
        can_apply = True
        reason = None

    else:
        can_apply = False
        reason = (
            "This is a review-only signal, not proof of an invalid "
            "event. Re-run only after human verification with "
            "--confirmed-invalid."
        )

    return {
        "article":
            article,
        "blocking_reasons":
            blocking_reasons,
        "review_reasons":
            review_reasons,
        "rounds":
            rounds,
        "rows":
            rows,
        "confirmed_invalid":
            bool(
                confirmed_invalid
            ),
        "can_apply":
            can_apply,
        "reason":
            reason,
    }


def repair_multi_round_article(
    article_id,
    apply=False,
    confirmed_invalid=False,
):
    """
    Delete sole-supported canonical rounds only after the repair
    plan establishes an explicit safe basis for doing so.

    Dry-run is the default. Transaction ownership belongs to the
    caller; this function deliberately does not commit.
    """

    plan = plan_multi_round_repair(
        article_id=article_id,
        confirmed_invalid=(
            confirmed_invalid
        ),
    )

    article = plan[
        "article"
    ]

    if not apply:
        return {
            **plan,
            "applied":
                False,
            "rounds_deleted":
                0,
        }

    if not plan[
        "can_apply"
    ]:
        raise ValueError(
            plan[
                "reason"
            ]
        )

    deleted = 0

    for funding_round in plan[
        "rounds"
    ]:
        funding_round.investors.clear()
        funding_round.lead_investors.clear()
        funding_round.articles.clear()
        funding_round.article = None

        db.session.delete(
            funding_round
        )

        deleted += 1

    article.llm_processed_at = None
    article.llm_is_funding_round = None

    db.session.flush()

    return {
        **plan,
        "applied":
            True,
        "rounds_deleted":
            deleted,
    }