import pytest

from source_registry import (
    get_discovery_config,
    get_discovery_sources,
    get_source,
    get_source_names,
    validate_source_registry,
)


def test_source_registry_is_valid():
    assert (
        validate_source_registry()
        is True
    )


def test_source_can_be_found_by_name():
    source = get_source(
        "TechCrunch"
    )

    assert source is not None

    assert (
        source["key"]
        == "techcrunch"
    )


def test_source_can_be_found_by_key():
    source = get_source(
        "techcrunch"
    )

    assert source is not None

    assert (
        source["name"]
        == "TechCrunch"
    )


def test_techcrunch_has_incremental_strategy():
    config = (
        get_discovery_config(
            "TechCrunch",
            mode="incremental",
        )
    )

    assert config is not None

    assert (
        config["method"]
        == "rss"
    )

    assert (
        config["url"]
        == "https://techcrunch.com/feed"
    )


def test_techcrunch_has_historical_strategy():
    config = (
        get_discovery_config(
            "TechCrunch",
            mode="historical",
        )
    )

    assert config is not None

    assert (
        config["method"]
        == "html"
    )

    assert (
        config[
            "max_discovery_items"
        ]
        == 500
    )


def test_source_without_historical_strategy_returns_none():
    config = (
        get_discovery_config(
            "Sifted",
            mode="historical",
        )
    )

    assert config is None


def test_historical_fleet_contains_configured_sources():
    configs = (
        get_discovery_sources(
            mode="historical",
            enabled_only=True,
        )
    )

    names = [
        config["name"]
        for config in configs
    ]

    assert names == [
        "TechCrunch",
        "Accel",
        "Index Ventures",
        "Sequoia Capital",
        "Bessemer Venture Partners",
        "Greylock",
    ]


def test_historical_investor_fleet():
    configs = (
        get_discovery_sources(
            mode="historical",
            source_type="investor",
            enabled_only=True,
        )
    )

    names = {
        config["name"]
        for config in configs
    }

    assert names == {
        "Accel",
        "Index Ventures",
        "Sequoia Capital",
        "Bessemer Venture Partners",
        "Greylock",
    }


def test_historical_investor_strategies_remove_recency_limits():
    for name in [
        "Accel",
        "Index Ventures",
        "Sequoia Capital",
        "Bessemer Venture Partners",
        "Greylock",
    ]:
        config = (
            get_discovery_config(
                name,
                mode="historical",
            )
        )

        assert config is not None

        assert (
            config[
                "max_discovery_items"
            ]
            == 250
        )

        assert (
            "max_age_days"
            not in config
        )

        assert (
            "max_published_age_days"
            not in config
        )


def test_historical_html_cohort_reuses_generic_adapter():
    bessemer = (
        get_discovery_config(
            "Bessemer Venture Partners",
            mode="historical",
        )
    )

    greylock = (
        get_discovery_config(
            "Greylock",
            mode="historical",
        )
    )

    assert (
        bessemer["method"]
        == "html"
    )

    assert (
        bessemer[
            "max_discovery_pages"
        ]
        == 1
    )

    assert (
        "pagination_url_pattern"
        not in bessemer
    )

    assert (
        greylock["method"]
        == "html"
    )

    assert (
        greylock[
            "pagination_url_pattern"
        ]
        == (
            "https://greylock.com/"
            "blog/portfolio-news/"
            "page/{page}/"
        )
    )

    assert (
        greylock[
            "max_discovery_pages"
        ]
        == 20
    )


def test_general_catalyst_is_not_historical_capable():
    config = (
        get_discovery_config(
            "General Catalyst",
            mode="historical",
        )
    )

    assert config is None


def test_incremental_investor_fleet():
    configs = (
        get_discovery_sources(
            mode="incremental",
            source_type="investor",
            enabled_only=True,
        )
    )

    names = {
        config["name"]
        for config in configs
    }

    assert names == {
        "Accel",
        "Index Ventures",
        "Sequoia Capital",
        "Andreessen Horowitz",
        "General Catalyst",
        "Bessemer Venture Partners",
        "Greylock",
        "NEA",
        "Balderton Capital",
        "Insight Partners",
    }


def test_scale_cohort_has_ten_enabled_investors():
    names = get_source_names(
        source_type="investor",
        enabled_only=True,
    )

    assert len(
        names
    ) == 10


def test_new_scale_cohort_uses_existing_html_adapter():
    names = [
        "Andreessen Horowitz",
        "General Catalyst",
        "Bessemer Venture Partners",
        "Greylock",
        "NEA",
        "Balderton Capital",
        "Insight Partners",
    ]

    for name in names:
        config = (
            get_discovery_config(
                name,
                mode="incremental",
            )
        )

        assert config is not None

        assert (
            config["method"]
            == "html"
        )


def test_general_catalyst_story_boundary():
    config = (
        get_discovery_config(
            "General Catalyst",
            mode="incremental",
        )
    )

    assert (
        "generalcatalyst.com/stories/"
        in config[
            "include_url_patterns"
        ]
    )


def test_bessemer_atlas_boundary():
    config = (
        get_discovery_config(
            "Bessemer Venture Partners",
            mode="incremental",
        )
    )

    assert (
        "bvp.com/atlas/"
        in config[
            "include_url_patterns"
        ]
    )


def test_enabled_source_names_exclude_disabled_sources():
    names = get_source_names(
        enabled_only=True,
    )

    assert "TechCrunch" in names
    assert "Accel" in names

    assert (
        "Silicon Canals"
        not in names
    )


def test_source_lookup_returns_defensive_copy():
    source = get_source(
        "TechCrunch"
    )

    source["name"] = (
        "Changed"
    )

    source_again = get_source(
        "TechCrunch"
    )

    assert (
        source_again["name"]
        == "TechCrunch"
    )


def test_invalid_mode_raises():
    with pytest.raises(
        ValueError
    ):
        get_discovery_sources(
            mode="something-else"
        )


def test_registry_rejects_duplicate_source_keys():
    registry = [
        {
            "key": "duplicate",
            "name": "Source One",
            "type": "publication",
            "region": "Global",
            "enabled": True,
            "discovery": {
                "incremental": {
                    "method": "rss",
                    "url": (
                        "https://example.com/"
                        "one.xml"
                    ),
                },
            },
        },
        {
            "key": "duplicate",
            "name": "Source Two",
            "type": "publication",
            "region": "Global",
            "enabled": True,
            "discovery": {
                "incremental": {
                    "method": "rss",
                    "url": (
                        "https://example.com/"
                        "two.xml"
                    ),
                },
            },
        },
    ]

    with pytest.raises(
        ValueError
    ):
        validate_source_registry(
            registry
        )