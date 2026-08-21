import re


COMPOUND_FUNDING_TITLE_PATTERNS = [
    re.compile(
        r"\bfunding rounds\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:top\s+)?\d+\s+"
        r"(?:biggest|largest|top)?\s*"
        r"funding rounds\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:week(?:'s|’s)?|weekly)\b"
        r".*\bfunding\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bfunding\b.*"
        r"\b(?:week(?:'s|’s)?|weekly)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bfunding roundup\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdeals of the week\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:these|those|\d+)\b"
        r".{0,60}\bstartups\b"
        r".{0,40}\brais(?:e|ed|ing)\b",
        re.IGNORECASE,
    ),
]


# These patterns are intentionally REVIEW signals, not automatic
# quarantine rules. Venture articles routinely mention historical
# rounds while clearly announcing one new financing event.
EXPLICIT_MULTI_ROUND_REVIEW_PATTERNS = [
    re.compile(
        r"\b(?:two|three|four|five|six|seven|eight|nine|"
        r"multiple|several|both)\b"
        r".{0,45}\b(?:funding|financing|investment)?\s*rounds\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b[2-9]\s+(?:separate\s+)?"
        r"(?:funding|financing|investment)?\s*rounds\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:first|initial)\s+(?:funding|financing|investment)\b"
        r".{0,140}\b(?:second|subsequent|later|follow-on)\s+"
        r"(?:funding|financing|investment)\b",
        re.IGNORECASE | re.DOTALL,
    ),
]


ROUND_STAGE_PATTERN = re.compile(
    r"\b("
    r"pre[-\s]?seed"
    r"|seed"
    r"|series\s+[a-h]"
    r"|series\s+[a-h]\d?"
    r")\b",
    re.IGNORECASE,
)


ROUND_CONTEXT_PATTERN = re.compile(
    r"\b("
    r"round(?:s)?"
    r"|financ(?:e|ed|ing|ings)"
    r"|fund(?:ing|ed|s)?"
    r"|rais(?:e|ed|ing)"
    r"|led"
    r"|lead(?:ing)?"
    r"|co[-\s]?led"
    r"|invest(?:ment|ed|ing)?"
    r"|backed"
    r")\b",
    re.IGNORECASE,
)


ROUND_PAIR_CONNECTOR_PATTERN = re.compile(
    r"\b("
    r"and"
    r"|then"
    r"|later"
    r"|subsequent(?:ly)?"
    r"|followed\s+by"
    r"|following"
    r"|as\s+well\s+as"
    r"|both"
    r")\b",
    re.IGNORECASE,
)


MAX_STAGE_PAIR_DISTANCE = 220
ROUND_CONTEXT_RADIUS = 90


def _article_text(article):
    parts = []

    for attribute in (
        "title",
        "summary",
        "content",
    ):
        value = (
            getattr(
                article,
                attribute,
                None,
            )
            or ""
        ).strip()

        if value:
            parts.append(
                value
            )

    return "\n".join(
        parts
    )


def _normalize_stage(value):
    value = (
        value
        .casefold()
        .replace("-", " ")
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    ).strip()

    return value


def _stage_mentions_with_financing_context(text):
    mentions = []

    for match in ROUND_STAGE_PATTERN.finditer(
        text
    ):
        start = max(
            0,
            match.start()
            - ROUND_CONTEXT_RADIUS,
        )

        end = min(
            len(text),
            match.end()
            + ROUND_CONTEXT_RADIUS,
        )

        context = text[
            start:end
        ]

        if (
            ROUND_CONTEXT_PATTERN.search(
                context
            )
            is None
        ):
            continue

        mentions.append(
            {
                "stage":
                    _normalize_stage(
                        match.group(1)
                    ),
                "start":
                    match.start(),
                "end":
                    match.end(),
            }
        )

    return mentions


def _has_distinct_connected_stage_pair(text):
    mentions = (
        _stage_mentions_with_financing_context(
            text
        )
    )

    for index, first in enumerate(
        mentions
    ):
        for second in mentions[
            index + 1:
        ]:
            if (
                first["stage"]
                == second["stage"]
            ):
                continue

            distance = (
                second["start"]
                - first["end"]
            )

            if distance < 0:
                continue

            if (
                distance
                > MAX_STAGE_PAIR_DISTANCE
            ):
                break

            between = text[
                first["end"]:
                second["start"]
            ]

            if (
                ROUND_PAIR_CONNECTOR_PATTERN.search(
                    between
                )
                is not None
            ):
                return True

    return False


def get_compound_funding_reasons(article):
    """
    Return HIGH-PRECISION reasons why Funding Round evidence
    must be blocked from the single-event extractor.

    V2 deliberately restricts automatic quarantine to obvious
    multi-company / roundup evidence. Mentioning more than one
    financing stage is not enough: legitimate current-round
    articles frequently describe historical financing context.
    """

    if article is None:
        return []

    category = getattr(
        article,
        "category",
        None,
    )

    if (
        category
        != "Funding Round"
    ):
        return []

    title = (
        getattr(
            article,
            "title",
            "",
        )
        or ""
    ).strip()

    if not title:
        return []

    if any(
        pattern.search(
            title
        )
        is not None
        for pattern
        in COMPOUND_FUNDING_TITLE_PATTERNS
    ):
        return [
            "collection"
        ]

    return []


def get_multi_round_review_reasons(article):
    """
    Return reasons why an article deserves multi-round review.

    Review reasons are intentionally broader than automatic
    blocking reasons. They are diagnostic signals only and must
    never, by themselves, authorize event deletion.
    """

    blocking_reasons = (
        get_compound_funding_reasons(
            article
        )
    )

    if article is None:
        return blocking_reasons

    category = getattr(
        article,
        "category",
        None,
    )

    if (
        category
        != "Funding Round"
    ):
        return blocking_reasons

    reasons = list(
        blocking_reasons
    )

    text = _article_text(
        article
    )

    if not text:
        return reasons

    if any(
        pattern.search(
            text
        )
        is not None
        for pattern
        in EXPLICIT_MULTI_ROUND_REVIEW_PATTERNS
    ):
        reasons.append(
            "explicit_multiple_rounds"
        )

    if _has_distinct_connected_stage_pair(
        text
    ):
        reasons.append(
            "multiple_financing_stages"
        )

    return list(
        dict.fromkeys(
            reasons
        )
    )


def is_compound_funding_evidence(article):
    """
    Return True only for evidence Vantage can safely quarantine
    without semantic interpretation.

    Single-company articles that merely mention multiple rounds
    remain eligible for extraction. The extractor is responsible
    for isolating one focal financing event and refusing ambiguous
    documents rather than blending facts across rounds.
    """

    return bool(
        get_compound_funding_reasons(
            article
        )
    )