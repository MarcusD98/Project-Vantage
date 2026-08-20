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


def is_compound_funding_evidence(
    article,
):
    """
    Return True when a Funding Round evidence document is an
    obvious multi-company or multi-event collection that should
    not be sent through Vantage's single-event funding extractor.

    V1 is deliberately conservative and title-based.

    Objects without funding-category metadata are treated as
    non-compound rather than raising an exception. This keeps
    the helper safe for lightweight test doubles and callers
    that only provide partial Article-like objects.
    """

    if article is None:
        return False

    category = getattr(
        article,
        "category",
        None,
    )

    if (
        category
        != "Funding Round"
    ):
        return False

    title = (
        getattr(
            article,
            "title",
            "",
        )
        or ""
    ).strip()

    if not title:
        return False

    return any(
        pattern.search(
            title
        )
        is not None
        for pattern
        in COMPOUND_FUNDING_TITLE_PATTERNS
    )