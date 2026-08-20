from copy import deepcopy


# ---------------------------------------------------------
# Source platform constants
# ---------------------------------------------------------

SUPPORTED_SOURCE_TYPES = {
    "publication",
    "investor",
    "ecosystem",
    "company",
    "structured",
}


SUPPORTED_DISCOVERY_METHODS = {
    "rss",
    "sitemap",
    "html",
}


SUPPORTED_DISCOVERY_MODES = {
    "incremental",
    "historical",
}


# ---------------------------------------------------------
# Canonical source registry
# ---------------------------------------------------------

SOURCE_REGISTRY = [
    # -----------------------------------------------------
    # Editorial publications
    # -----------------------------------------------------

    {
        "key": "techcrunch",
        "name": "TechCrunch",
        "type": "publication",
        "region": "Global",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": "https://techcrunch.com/feed",
            },

            "historical": {
                "method": "html",
                "url": "https://techcrunch.com/2026/",

                "link_selector": "h3 a",

                "pagination_url_pattern": (
                    "https://techcrunch.com/"
                    "2026/page/{page}/"
                ),

                "include_url_patterns": [
                    "techcrunch.com/2026/",
                ],

                "exclude_url_patterns": [
                    "/page/",
                ],

                "max_discovery_pages": 20,
                "max_discovery_items": 500,
            },
        },
    },

    {
        "key": "sifted",
        "name": "Sifted",
        "type": "publication",
        "region": "Europe",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": "https://sifted.eu/feed",
            },
        },
    },

    {
        "key": "crunchbase-news",
        "name": "Crunchbase News",
        "type": "publication",
        "region": "Global",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": (
                    "https://news.crunchbase.com/feed/"
                ),
            },
        },
    },

    {
        "key": "tech-eu",
        "name": "Tech.eu",
        "type": "publication",
        "region": "Europe",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": "https://tech.eu/feed/",
            },
        },
    },

    {
        "key": "eu-startups",
        "name": "EU-Startups",
        "type": "publication",
        "region": "Europe",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": (
                    "https://www.eu-startups.com/feed/"
                ),
            },
        },
    },

    {
        "key": "venturebeat",
        "name": "VentureBeat",
        "type": "publication",
        "region": "Global",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": "https://venturebeat.com/feed/",
            },
        },
    },

    {
        "key": "silicon-canals",
        "name": "Silicon Canals",
        "type": "publication",
        "region": "Europe",
        "enabled": False,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": (
                    "https://siliconcanals.com/"
                    "news/startups/feed/"
                ),
            },
        },
    },

    {
        "key": "latamlist",
        "name": "LatAmList",
        "type": "publication",
        "region": "Latin America",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": "https://latamlist.com/feed",
            },
        },
    },

    {
        "key": "inc42",
        "name": "Inc42",
        "type": "publication",
        "region": "India",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": "https://inc42.com/feed/",
            },
        },
    },

    {
        "key": "techcabal",
        "name": "TechCabal",
        "type": "publication",
        "region": "Africa",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "rss",
                "url": "https://techcabal.com/feed/",
            },
        },
    },

    # -----------------------------------------------------
    # First-party investor sources
    # -----------------------------------------------------

    {
        "key": "accel",
        "name": "Accel",
        "type": "investor",
        "region": "Global",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "sitemap",
                "url": (
                    "https://www.accel.com/sitemap.xml"
                ),

                # Sitemap modification age is only a
                # discovery hint.
                "max_age_days": 180,

                # Actual publication date determines
                # eligibility for current intelligence.
                "max_published_age_days": 180,

                "include_url_patterns": [
                    "/news/",
                ],

                "exclude_url_patterns": [
                    "/news/insights",
                    "/news/portfolio",
                    "/news/podcasts",
                ],
            },
        },
    },

    {
        "key": "index-ventures",
        "name": "Index Ventures",
        "type": "investor",
        "region": "Global",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "sitemap",
                "url": (
                    "https://www.indexventures.com/"
                    "sitemap.xml"
                ),

                "sitemap_include_patterns": [
                    "sitemap-perspectives.xml",
                ],

                "include_url_patterns": [
                    "/perspectives/",
                ],

                "exclude_url_regex_patterns": [
                    r"/perspectives/$",
                    r"/perspectives/\d+/$",
                    (
                        r"/perspectives/"
                        r"news(?:/\d+)?/$"
                    ),
                    (
                        r"/perspectives/"
                        r"insights(?:/\d+)?/$"
                    ),
                    r"/perspectives/relationship/",
                    r"/perspectives/team-member/",
                ],

                "max_age_days": 180,
                "max_discovery_items": 100,

                "max_published_age_days": 180,
            },
        },
    },

    {
        "key": "sequoia-capital",
        "name": "Sequoia Capital",
        "type": "investor",
        "region": "Global",
        "enabled": True,

        "discovery": {
            "incremental": {
                "method": "sitemap",
                "url": (
                    "https://sequoiacap.com/"
                    "sitemap.xml"
                ),

                "include_url_patterns": [
                    "/article/",
                ],

                "exclude_url_regex_patterns": [
                    r"/article/tag/",
                ],

                "max_discovery_items": 100,

                "max_published_age_days": 180,
            },
        },
    },
]


# ---------------------------------------------------------
# Registry validation
# ---------------------------------------------------------

def validate_source_registry(
    registry=None,
):
    """
    Validate the canonical source registry.

    Fail fast when source definitions contain structural
    errors that would otherwise become runtime ingestion
    failures.
    """

    if registry is None:
        registry = SOURCE_REGISTRY

    if not isinstance(
        registry,
        list,
    ):
        raise ValueError(
            "Source registry must be a list."
        )

    seen_keys = set()
    seen_names = set()

    for source in registry:
        if not isinstance(
            source,
            dict,
        ):
            raise ValueError(
                "Each source definition must "
                "be a dictionary."
            )

        required_fields = [
            "key",
            "name",
            "type",
            "region",
            "enabled",
            "discovery",
        ]

        for field in required_fields:
            if field not in source:
                raise ValueError(
                    "Source definition missing "
                    f"required field: {field}"
                )

        key = str(
            source["key"]
        ).strip()

        name = str(
            source["name"]
        ).strip()

        source_type = str(
            source["type"]
        ).strip().lower()

        if not key:
            raise ValueError(
                "Source key cannot be empty."
            )

        if not name:
            raise ValueError(
                "Source name cannot be empty."
            )

        normalized_key = (
            key.casefold()
        )

        normalized_name = (
            name.casefold()
        )

        if normalized_key in seen_keys:
            raise ValueError(
                f"Duplicate source key: {key}"
            )

        if normalized_name in seen_names:
            raise ValueError(
                f"Duplicate source name: {name}"
            )

        seen_keys.add(
            normalized_key
        )

        seen_names.add(
            normalized_name
        )

        if (
            source_type
            not in SUPPORTED_SOURCE_TYPES
        ):
            raise ValueError(
                "Unsupported source type "
                f"for {name}: {source_type}"
            )

        if not isinstance(
            source["enabled"],
            bool,
        ):
            raise ValueError(
                "Source enabled flag must "
                f"be boolean for {name}."
            )

        discovery = source[
            "discovery"
        ]

        if not isinstance(
            discovery,
            dict,
        ):
            raise ValueError(
                "Source discovery definition "
                f"must be a dictionary for {name}."
            )

        if not discovery:
            raise ValueError(
                "Source must define at least "
                f"one discovery strategy: {name}"
            )

        for mode, strategy in (
            discovery.items()
        ):
            normalized_mode = (
                str(mode)
                .strip()
                .lower()
            )

            if (
                normalized_mode
                not in SUPPORTED_DISCOVERY_MODES
            ):
                raise ValueError(
                    "Unsupported discovery mode "
                    f"for {name}: {mode}"
                )

            if not isinstance(
                strategy,
                dict,
            ):
                raise ValueError(
                    "Discovery strategy must "
                    f"be a dictionary for {name}."
                )

            method = (
                str(
                    strategy.get(
                        "method",
                        "",
                    )
                )
                .strip()
                .lower()
            )

            if (
                method
                not in
                SUPPORTED_DISCOVERY_METHODS
            ):
                raise ValueError(
                    "Unsupported discovery method "
                    f"for {name}: {method}"
                )

            url = (
                str(
                    strategy.get(
                        "url",
                        "",
                    )
                )
                .strip()
            )

            if not url:
                raise ValueError(
                    "Discovery strategy missing "
                    f"URL for {name} ({mode})."
                )

    return True


# ---------------------------------------------------------
# Registry lookup
# ---------------------------------------------------------

def get_source(
    identifier,
):
    """
    Return one canonical source definition.

    A source may be addressed by either:

        source key
        source display name

    Matching is case-insensitive.

    The returned object is a defensive copy so callers cannot
    accidentally mutate the canonical registry.
    """

    if identifier is None:
        return None

    normalized_identifier = (
        str(identifier)
        .strip()
        .casefold()
    )

    if not normalized_identifier:
        return None

    for source in SOURCE_REGISTRY:
        if (
            source["key"]
            .casefold()
            == normalized_identifier
        ):
            return deepcopy(
                source
            )

        if (
            source["name"]
            .casefold()
            == normalized_identifier
        ):
            return deepcopy(
                source
            )

    return None


# ---------------------------------------------------------
# Discovery configuration
# ---------------------------------------------------------

def _build_discovery_config(
    source,
    mode,
):
    """
    Flatten one canonical source definition into the existing
    Vantage discovery configuration shape.

    This compatibility boundary allows the current discovery
    and intelligence pipeline to continue operating unchanged
    while source configuration becomes unified.
    """

    if source is None:
        return None

    normalized_mode = (
        str(mode)
        .strip()
        .lower()
    )

    strategy = (
        source.get(
            "discovery",
            {},
        )
        .get(
            normalized_mode
        )
    )

    if strategy is None:
        return None

    config = {
        "key":
            source["key"],

        "name":
            source["name"],

        "type":
            source["type"],

        "region":
            source["region"],

        "enabled":
            source["enabled"],
    }

    config.update(
        deepcopy(
            strategy
        )
    )

    return config


def get_discovery_config(
    identifier,
    mode="incremental",
):
    """
    Return the discovery configuration for one source and
    operating mode.

    Returns None when either the source or requested strategy
    does not exist.
    """

    source = get_source(
        identifier
    )

    return _build_discovery_config(
        source,
        mode,
    )


def get_discovery_sources(
    mode="incremental",
    source_type=None,
    enabled_only=False,
):
    """
    Return flattened discovery configurations for a source
    fleet.

    Optional filters allow callers to select:

        incremental / historical mode
        source type
        enabled sources only

    Sources without the requested discovery strategy are
    omitted.
    """

    normalized_mode = (
        str(mode)
        .strip()
        .lower()
    )

    if (
        normalized_mode
        not in SUPPORTED_DISCOVERY_MODES
    ):
        raise ValueError(
            "Unsupported discovery mode: "
            f"{mode}"
        )

    normalized_source_type = None

    if source_type is not None:
        normalized_source_type = (
            str(source_type)
            .strip()
            .lower()
        )

        if (
            normalized_source_type
            not in SUPPORTED_SOURCE_TYPES
        ):
            raise ValueError(
                "Unsupported source type: "
                f"{source_type}"
            )

    configs = []

    for source in SOURCE_REGISTRY:
        if (
            normalized_source_type
            is not None
            and source["type"].lower()
            != normalized_source_type
        ):
            continue

        if (
            enabled_only
            and not source["enabled"]
        ):
            continue

        config = (
            _build_discovery_config(
                source,
                normalized_mode,
            )
        )

        if config is None:
            continue

        configs.append(
            config
        )

    return configs


def get_source_names(
    mode=None,
    source_type=None,
    enabled_only=True,
):
    """
    Return canonical source display names.

    When mode is supplied, only sources with that discovery
    strategy are returned.
    """

    if mode is not None:
        return [
            source["name"]
            for source
            in get_discovery_sources(
                mode=mode,
                source_type=source_type,
                enabled_only=enabled_only,
            )
        ]

    normalized_source_type = None

    if source_type is not None:
        normalized_source_type = (
            str(source_type)
            .strip()
            .lower()
        )

        if (
            normalized_source_type
            not in SUPPORTED_SOURCE_TYPES
        ):
            raise ValueError(
                "Unsupported source type: "
                f"{source_type}"
            )

    names = []

    for source in SOURCE_REGISTRY:
        if (
            enabled_only
            and not source["enabled"]
        ):
            continue

        if (
            normalized_source_type
            is not None
            and source["type"].lower()
            != normalized_source_type
        ):
            continue

        names.append(
            source["name"]
        )

    return names


# Validate configuration immediately when the registry is
# imported. Configuration errors should fail fast during
# development rather than appearing as mysterious ingestion
# failures later.
validate_source_registry()