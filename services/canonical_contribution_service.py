from models.article import (
    Article,
)


def _funding_events_for_article(
    article,
):
    """
    Return every canonical funding event supported by one
    evidence document.

    Include both:

    - the modern multi-source evidence relationship
    - the legacy primary-article relationship
    """

    events = {}

    for funding_round in (
        article.supported_funding_rounds
    ):
        events[
            funding_round.id
        ] = funding_round

    for funding_round in (
        article.primary_funding_rounds
    ):
        events[
            funding_round.id
        ] = funding_round

    return list(
        events.values()
    )


def _event_source_names(
    event,
):
    """
    Return all distinct evidence sources supporting one
    canonical funding event.
    """

    source_names = set()

    for article in event.articles:
        if article.source:
            source_names.add(
                article.source
            )

    primary_article = (
        event.article
    )

    if (
        primary_article is not None
        and primary_article.source
    ):
        source_names.add(
            primary_article.source
        )

    return source_names


def _safe_ratio(
    numerator,
    denominator,
):
    if not denominator:
        return None

    return (
        numerator
        / denominator
    )


def measure_canonical_funding_contribution(
    source_name,
):
    """
    Measure all canonical funding knowledge supported by the
    persisted Vantage corpus for one source.

    Unlike current source-operating measurements, this metric
    deliberately does NOT apply:

    - publication recency policy
    - current eligibility policy
    - legacy LLM processing selectors

    If historical evidence supports a canonical event, that
    event belongs in the Phase 8 observation measurement.

    This answers:

        What canonical funding knowledge has this source
        contributed to the observed Vantage corpus?
    """

    if not source_name:
        raise ValueError(
            "source_name is required."
        )

    articles = (
        Article.query
        .filter_by(
            source=source_name
        )
        .all()
    )

    funding_events = {}

    for article in articles:
        for funding_round in (
            _funding_events_for_article(
                article
            )
        ):
            funding_events[
                funding_round.id
            ] = funding_round

    unique_funding_events = []

    multi_source_funding_events = []

    for event in (
        funding_events.values()
    ):
        source_names = (
            _event_source_names(
                event
            )
        )

        if source_names == {
            source_name
        }:
            unique_funding_events.append(
                event
            )

        if len(
            source_names
        ) > 1:
            multi_source_funding_events.append(
                event
            )

    return {
        "supported_funding_events":
            len(
                funding_events
            ),

        "unique_funding_events":
            len(
                unique_funding_events
            ),

        "multi_source_funding_events":
            len(
                multi_source_funding_events
            ),

        "funding_overlap_rate":
            _safe_ratio(
                len(
                    multi_source_funding_events
                ),
                len(
                    funding_events
                ),
            ),
    }