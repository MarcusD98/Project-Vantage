from models.article import db
from models.funding_round import FundingRound


def _unique_evidence_articles(
    funding_round,
):
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


def _evidence_sort_key(article):
    return (
        article.published_at is None,
        (
            -article.published_at.timestamp()
            if article.published_at is not None
            else 0
        ),
        article.id or 0,
    )


def get_funding_event_detail(
    funding_round_id,
):
    """
    Build a product-facing view of one canonical financing
    event and every evidence document currently supporting it.

    This service is read-only.
    """

    funding_round = (
        db.session.get(
            FundingRound,
            funding_round_id,
        )
    )

    if funding_round is None:
        return None

    primary_article_id = (
        funding_round.article.id
        if funding_round.article is not None
        else None
    )

    evidence_articles = (
        _unique_evidence_articles(
            funding_round
        )
    )

    evidence_articles.sort(
        key=_evidence_sort_key
    )

    evidence = [
        {
            "article":
                article,

            "is_primary":
                (
                    article.id
                    == primary_article_id
                ),
        }
        for article
        in evidence_articles
    ]

    lead_ids = {
        investor.id
        for investor
        in funding_round.lead_investors
        if investor.id is not None
    }

    participants = [
        {
            "investor":
                investor,

            "is_lead":
                investor.id in lead_ids,
        }
        for investor
        in sorted(
            funding_round.investors,
            key=lambda item:
                item.name.casefold(),
        )
    ]

    return {
        "funding_round":
            funding_round,

        "company":
            funding_round.company,

        "participants":
            participants,

        "evidence":
            evidence,

        "evidence_count":
            len(evidence),
    }
