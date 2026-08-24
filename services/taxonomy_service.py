import re


CANONICAL_SECTORS = {
    "Artificial Intelligence": [
        "ai",
        "artificial intelligence",
        "machine learning",
        "generative ai",
        "genai",
        "enterprise ai",
        "ai infrastructure",
        "ai hardware",
        "foundation models",
    ],

    "Fintech": [
        "fintech",
        "financial technology",
        "payments",
        "payment technology",
        "embedded finance",
        "banking technology",
        "insurtech",
        "wealthtech",
        "accounting software",
        "ai accounting software",
        "debt collection technology",
        "debt collection software",
        "collections technology",
    ],

    "Enterprise Software": [
        "enterprise software",
        "b2b software",
        "business software",
        "saas",
        "enterprise saas",
        "workflow software",
        "employee experience software",
        "employee software",
        "b2b marketing technology",
        "marketing technology",
        "data platform",
        "logistics technology",
        "logistics software",
    ],

    "Legal Tech": [
        "legal tech",
        "legal technology",
        "legal software",
        "legal ai",
        "law technology",
    ],

    "Cybersecurity": [
        "cybersecurity",
        "cyber security",
        "information security",
        "cloud security",
        "application security",
    ],

    "Defence": [
        "defence",
        "defense",
        "defence technology",
        "defense technology",
        "defence tech",
        "defense tech",
        "military technology",
        "security and resilience",
    ],

    "Deep Tech": [
        "deep tech",
        "deeptech",
        "quantum",
        "quantum computing",
        "semiconductors",
        "semiconductor",
        "advanced materials",
        "photonics",
        "fiber optic technology",
        "fibre optic technology",
        "optical networking",
    ],

    "Climate Tech": [
        "climate tech",
        "climate technology",
        "climatetech",
        "clean tech",
        "cleantech",
        "clean energy",
        "renewable energy",
        "carbon removal",
        "decarbonization",
        "decarbonisation",
        "waste to energy",
    ],

    "Health Tech": [
        "health tech",
        "health technology",
        "healthtech",
        "digital health",
        "healthcare technology",
        "medical technology",
        "medtech",
        "fitness and wellness",
        "fitness technology",
        "wellness technology",
    ],

    "Biotech": [
        "biotech",
        "biotechnology",
        "life sciences",
        "drug discovery",
        "therapeutics",
    ],

    "Agritech": [
        "agritech",
        "agri tech",
        "agricultural technology",
        "agriculture technology",
        "precision agriculture",
        "agricultural biotechnology",
    ],

    "Edtech": [
        "edtech",
        "education technology",
        "educational technology",
        "learning technology",
    ],

    "Consumer": [
        "consumer",
        "consumer technology",
        "consumer tech",
        "consumer internet",
        "consumer food",
        "food technology",
        "food tech",
        "foodtech",
        "consumer app",
        "consumer application",
    ],

    "Marketplaces": [
        "marketplace",
        "marketplaces",
        "online marketplace",
        "digital marketplace",
        "b2b marketplace",
    ],

    "Mobility": [
        "mobility",
        "transportation",
        "transport technology",
        "automotive technology",
        "autonomous vehicles",
        "electric vehicles",
    ],

    "Space": [
        "space",
        "space tech",
        "space technology",
        "spacetech",
        "satellite",
        "satellites",
    ],

    "Robotics": [
        "robotics",
        "robot",
        "industrial robotics",
        "autonomous robotics",
    ],
}


# These vertical categories should outrank broad enabling technologies.
PRIORITY_SECTORS = [
    "Fintech",
    "Legal Tech",
    "Health Tech",
    "Biotech",
    "Agritech",
    "Edtech",
    "Cybersecurity",
    "Defence",
    "Climate Tech",
    "Consumer",
    "Marketplaces",
    "Mobility",
    "Space",
    "Robotics",
    "Enterprise Software",
    "Deep Tech",
    "Artificial Intelligence",
]


def normalize_sector_text(sector):
    if not sector:
        return None

    normalized = sector.strip().lower()

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

    normalized = normalized.strip()

    return normalized or None


def _contains_alias(
    normalized,
    alias,
):
    pattern = (
        r"(?<!\w)"
        + re.escape(alias)
        + r"(?!\w)"
    )

    return bool(
        re.search(
            pattern,
            normalized,
        )
    )


def canonicalize_sector(sector):
    normalized = normalize_sector_text(
        sector
    )

    if not normalized:
        return None

    # First check exact matches according to taxonomy priority.
    for canonical_sector in PRIORITY_SECTORS:
        aliases = CANONICAL_SECTORS[
            canonical_sector
        ]

        if normalized in aliases:
            return canonical_sector

    # Then inspect longer descriptions.
    #
    # Sector priority matters here. A phrase such as
    # "AI accounting software" should map to Fintech rather
    # than Artificial Intelligence.
    for canonical_sector in PRIORITY_SECTORS:
        aliases = sorted(
            CANONICAL_SECTORS[
                canonical_sector
            ],
            key=len,
            reverse=True,
        )

        for alias in aliases:
            if _contains_alias(
                normalized,
                alias,
            ):
                return canonical_sector

    return "Other"