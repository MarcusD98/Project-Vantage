from datetime import (
    datetime,
    timedelta,
    timezone,
)

from config import SOURCES

from models.article import Article

from services.compound_evidence_service import (
    is_compound_funding_evidence,
)

# ---------------------------------------------------------
# Date handling
# ---------------------------------------------------------

def _normalize_datetime(value):
    """
    Normalize datetimes to timezone-aware UTC for safe
    comparison.

    SQLite commonly returns timezone-naive datetimes.
    """

    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc
        )

    return value.astimezone(
        timezone.utc
    )


def _article_is_known_stale(
    article,
    source,
    now=None,
):
    """
    Return True only when an evidence document has a known
    publication date and is outside the source's configured
    publication-age window.

    Undated evidence is not called stale because its age is
    unknown.
    """

    max_age_days = source.get(
        "max_published_age_days"
    )

    if max_age_days is None:
        return False

    published_at = _normalize_datetime(
        article.published_at
    )

    if published_at is None:
        return False

    if now is None:
        now = datetime.now(
            timezone.utc
        )
    else:
        now = _normalize_datetime(
            now
        )

    cutoff = (
        now
        - timedelta(
            days=max_age_days
        )
    )

    return published_at < cutoff


# ---------------------------------------------------------
# Event relationships
# ---------------------------------------------------------

def _funding_events_for_article(article):
    """
    Return all canonical funding events supported by one
    evidence document.

    Include both the multi-source evidence relationship and
    the historical primary-article relationship.
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


def _fund_close_events_for_article(article):
    """
    Return all canonical fund-close events supported by one
    evidence document.
    """

    events = {}

    for fund_close in (
        article.supported_fund_closes
    ):
        events[
            fund_close.id
        ] = fund_close

    for fund_close in article.fund_closes:
        events[
            fund_close.id
        ] = fund_close

    return list(
        events.values()
    )


def _event_source_names(event):
    """
    Return the distinct source names supporting a canonical
    event.
    """

    source_names = set()

    for article in event.articles:
        if article.source:
            source_names.add(
                article.source
            )

    primary_article = event.article

    if (
        primary_article is not None
        and primary_article.source
    ):
        source_names.add(
            primary_article.source
        )

    return source_names


# ---------------------------------------------------------
# Ratios
# ---------------------------------------------------------

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


def _format_percentage(value):
    if value is None:
        return "-"

    return f"{value:.1%}"


# ---------------------------------------------------------
# Source measurement
# ---------------------------------------------------------

def measure_source(
    source,
    now=None,
):
    """
    Measure the persisted contribution and operating state of
    one configured source.

    Measurement V2 separates:

        coverage
        processing
        confirmation quality
        canonical event contribution
        source overlap

    Current event metrics are calculated from confirmed,
    eligible funding evidence so numerator and denominator
    describe the same operating corpus.

    Historical stale evidence remains persisted but does not
    distort current processing or event-conversion metrics.
    """

    source_name = source[
        "name"
    ]

    articles = (
        Article.query
        .filter_by(
            source=source_name
        )
        .all()
    )

    # ---------------------------------------------------------
    # Candidate classes
    # ---------------------------------------------------------

    funding_candidates = [
        article
        for article in articles
        if article.category
        == "Funding Round"
    ]

    fund_news_candidates = [
        article
        for article in articles
        if article.category
        == "Fund News"
    ]

    # ---------------------------------------------------------
    # Staleness
    # ---------------------------------------------------------

    stale_funding_candidates = [
        article
        for article in funding_candidates
        if _article_is_known_stale(
            article,
            source,
            now=now,
        )
    ]

    stale_fund_news_candidates = [
        article
        for article in fund_news_candidates
        if _article_is_known_stale(
            article,
            source,
            now=now,
        )
    ]

    stale_funding_ids = {
        article.id
        for article
        in stale_funding_candidates
    }

    compound_funding_candidates = [
        article
        for article in funding_candidates
        if is_compound_funding_evidence(
            article
        )
    ]

    compound_funding_ids = {
        article.id
        for article
        in compound_funding_candidates
    }

    # ---------------------------------------------------------
    # Eligible funding corpus
    # ---------------------------------------------------------

    eligible_funding_candidates = [
        article
        for article in funding_candidates
        if (
            article.id
            not in stale_funding_ids
            and article.id
            not in compound_funding_ids
        )
    ]

    processed_funding = [
        article
        for article
        in eligible_funding_candidates
        if article.llm_processed_at
        is not None
    ]

    funding_backlog = [
        article
        for article
        in eligible_funding_candidates
        if article.llm_processed_at
        is None
    ]

    confirmed_funding = [
        article
        for article in processed_funding
        if article.llm_is_funding_round
        is True
    ]

    processed_fund_news = [
        article
        for article in fund_news_candidates
        if article.llm_processed_at
        is not None
    ]

    # ---------------------------------------------------------
    # Current canonical funding-event contribution
    # ---------------------------------------------------------

    funding_events = {}

    for article in confirmed_funding:
        for funding_round in (
            _funding_events_for_article(
                article
            )
        ):
            funding_events[
                funding_round.id
            ] = funding_round

    multi_source_funding_events = [
        event
        for event
        in funding_events.values()
        if len(
            _event_source_names(
                event
            )
        ) > 1
    ]

    unique_funding_events = [
        event
        for event
        in funding_events.values()
        if (
            _event_source_names(
                event
            )
            == {
                source_name
            }
        )
    ]

    # ---------------------------------------------------------
    # Fund-close contribution
    # ---------------------------------------------------------

    fund_close_events = {}

    for article in articles:
        for fund_close in (
            _fund_close_events_for_article(
                article
            )
        ):
            fund_close_events[
                fund_close.id
            ] = fund_close

    multi_source_fund_close_events = [
        event
        for event
        in fund_close_events.values()
        if len(
            _event_source_names(
                event
            )
        ) > 1
    ]

    # ---------------------------------------------------------
    # Evidence completeness
    # ---------------------------------------------------------

    dated_evidence = sum(
        1
        for article in articles
        if article.published_at
        is not None
    )

    processed_intelligence = (
        len(processed_funding)
        + len(processed_fund_news)
    )

    # ---------------------------------------------------------
    # Measurement V2 ratios
    # ---------------------------------------------------------

    funding_processing_rate = (
        _safe_ratio(
            len(processed_funding),
            len(
                eligible_funding_candidates
            ),
        )
    )

    funding_confirmation_rate = (
        _safe_ratio(
            len(confirmed_funding),
            len(processed_funding),
        )
    )

    funding_event_conversion_rate = (
        _safe_ratio(
            len(funding_events),
            len(confirmed_funding),
        )
    )

    funding_overlap_rate = (
        _safe_ratio(
            len(
                multi_source_funding_events
            ),
            len(funding_events),
        )
    )

    # ---------------------------------------------------------
    # Report
    # ---------------------------------------------------------

    return {
        "name":
            source_name,

        "source_type":
            source.get(
                "type"
            ),

        "method":
            source.get(
                "method",
                "rss",
            ),

        "enabled":
            source.get(
                "enabled",
                True,
            ),

        "stored_evidence":
            len(articles),

        "dated_evidence":
            dated_evidence,

        "funding_candidates":
            len(
                funding_candidates
            ),

        "stale_funding_candidates":
            len(
                stale_funding_candidates
            ),

        "eligible_funding_candidates":
            len(
                eligible_funding_candidates
            ),

        "processed_funding":
            len(
                processed_funding
            ),

        "funding_backlog":
            len(
                funding_backlog
            ),

        "funding_processing_rate":
            funding_processing_rate,

        "compound_funding_candidates":
            len(
                compound_funding_candidates
            ),

        "confirmed_funding_evidence":
            len(
                confirmed_funding
            ),

        "funding_confirmation_rate":
            funding_confirmation_rate,

        "supported_funding_events":
            len(
                funding_events
            ),

        "funding_event_conversion_rate":
            funding_event_conversion_rate,

        "unique_funding_events":
            len(
                unique_funding_events
            ),

        "multi_source_funding_events":
            len(
                multi_source_funding_events
            ),

        "funding_overlap_rate":
            funding_overlap_rate,

        "fund_news_candidates":
            len(
                fund_news_candidates
            ),

        "stale_fund_news_candidates":
            len(
                stale_fund_news_candidates
            ),

        "processed_fund_news":
            len(
                processed_fund_news
            ),

        "supported_fund_close_events":
            len(
                fund_close_events
            ),

        "multi_source_fund_close_events":
            len(
                multi_source_fund_close_events
            ),

        "processed_intelligence":
            processed_intelligence,
    }


def get_source_measurements(
    now=None,
    sources=None,
):
    """
    Measure all configured Vantage sources.
    """

    if sources is None:
        sources = SOURCES

    return [
        measure_source(
            source,
            now=now,
        )
        for source in sources
    ]


# ---------------------------------------------------------
# Human-readable reporting
# ---------------------------------------------------------

def format_source_measurement_report(
    measurements,
):
    """
    Produce the Measurement V2 terminal report.

    The table emphasizes operational readiness, extraction
    quality, and differentiated canonical event contribution.
    """

    headers = [
        "Source",
        "Type",
        "Stored",
        "Eligible",
        "Proc",
        "Backlog",
        "Proc %",
        "Confirm",
        "Confirm %",
        "Events",
        "Event %",
        "Unique",
        "Multi",
        "Overlap %",
    ]

    rows = []

    for item in measurements:
        rows.append(
            [
                item[
                    "name"
                ],

                item[
                    "source_type"
                ]
                or "-",

                str(
                    item[
                        "stored_evidence"
                    ]
                ),

                str(
                    item[
                        "eligible_funding_candidates"
                    ]
                ),

                str(
                    item[
                        "processed_funding"
                    ]
                ),

                str(
                    item[
                        "funding_backlog"
                    ]
                ),

                _format_percentage(
                    item[
                        "funding_processing_rate"
                    ]
                ),

                str(
                    item[
                        "confirmed_funding_evidence"
                    ]
                ),

                _format_percentage(
                    item[
                        "funding_confirmation_rate"
                    ]
                ),

                str(
                    item[
                        "supported_funding_events"
                    ]
                ),

                _format_percentage(
                    item[
                        "funding_event_conversion_rate"
                    ]
                ),

                str(
                    item[
                        "unique_funding_events"
                    ]
                ),

                str(
                    item[
                        "multi_source_funding_events"
                    ]
                ),

                _format_percentage(
                    item[
                        "funding_overlap_rate"
                    ]
                ),
            ]
        )

    widths = [
        max(
            len(
                headers[index]
            ),
            max(
                (
                    len(
                        row[index]
                    )
                    for row in rows
                ),
                default=0,
            ),
        )
        for index
        in range(
            len(headers)
        )
    ]

    def format_row(row):
        return " | ".join(
            value.ljust(
                widths[index]
            )
            for index, value
            in enumerate(row)
        )

    separator = "-+-".join(
        "-" * width
        for width in widths
    )

    lines = [
        format_row(
            headers
        ),
        separator,
    ]

    lines.extend(
        format_row(
            row
        )
        for row in rows
    )

    return "\n".join(
        lines
    )