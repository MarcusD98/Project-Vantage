import re


CANONICAL_ROUND_TYPES = {
    "Pre-Seed": [
        "pre seed",
        "pre-seed",
        "preseed",
    ],

    "Seed": [
        "seed",
        "seed round",
        "seed funding",
        "seed financing",
    ],

    "Pre-Series A": [
        "pre series a",
        "pre-series a",
        "pre series a round",
        "pre-series a round",
    ],

    "Series A": [
        "series a",
        "series a round",
        "series a funding",
        "series a financing",
    ],

    "Pre-Series B": [
        "pre series b",
        "pre-series b",
        "pre series b round",
        "pre-series b round",
    ],

    "Series B": [
        "series b",
        "series b round",
        "series b funding",
        "series b financing",
    ],

    "Series C": [
        "series c",
        "series c round",
        "series c funding",
        "series c financing",
    ],

    "Series D": [
        "series d",
        "series d round",
        "series d funding",
        "series d financing",
    ],

    "Series E+": [
        "series e",
        "series f",
        "series g",
        "series h",
        "series i",
    ],

    "Growth": [
        "growth",
        "growth round",
        "growth funding",
        "growth financing",
        "growth investment",
        "growth equity",
        "late stage",
        "late-stage",
    ],

    "Bridge": [
        "bridge",
        "bridge round",
        "bridge financing",
        "extension round",
        "series extension",
    ],

    "Strategic": [
        "strategic investment",
        "strategic financing",
        "strategic round",
    ],

    "Debt": [
        "debt",
        "debt financing",
        "venture debt",
        "credit facility",
        "fidc",
    ],

    "Mixed": [
        "equity and debt",
        "debt and equity",
        "equity + debt",
        "debt + equity",
    ],

    "SAFE": [
        "safe",
        "safe note",
        "safe financing",
    ],
}


ROUND_TYPE_PRIORITY = [
    "Mixed",
    "Pre-Series A",
    "Pre-Series B",
    "Pre-Seed",
    "Series A",
    "Series B",
    "Series C",
    "Series D",
    "Series E+",
    "Seed",
    "Growth",
    "Bridge",
    "Strategic",
    "SAFE",
    "Debt",
]


def normalize_round_type_text(round_type):
    if not round_type:
        return None

    normalized = round_type.strip().lower()

    normalized = re.sub(
        r"[-_/]",
        " ",
        normalized,
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized


def canonicalize_round_type(round_type):
    normalized = normalize_round_type_text(
        round_type
    )

    if not normalized:
        return None

    # Exact matches first.
    for canonical_type in ROUND_TYPE_PRIORITY:
        aliases = CANONICAL_ROUND_TYPES[
            canonical_type
        ]

        normalized_aliases = [
            normalize_round_type_text(alias)
            for alias in aliases
        ]

        if normalized in normalized_aliases:
            return canonical_type

    # Then descriptive phrases.
    for canonical_type in ROUND_TYPE_PRIORITY:
        aliases = sorted(
            CANONICAL_ROUND_TYPES[
                canonical_type
            ],
            key=len,
            reverse=True,
        )

        for alias in aliases:
            normalized_alias = (
                normalize_round_type_text(
                    alias
                )
            )

            pattern = (
                r"(?<!\w)"
                + re.escape(normalized_alias)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                normalized,
            ):
                return canonical_type

    return "Other"