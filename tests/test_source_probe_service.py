import pytest

from services.source_probe_service import (
    probe_source_candidate,
)


def test_productive_probe_reports_discovery(
    monkeypatch,
):
    def fake_discover_source(
        source,
    ):
        return [
            {
                "title":
                    "Investment announcement",

                "url":
                    (
                        "https://example.com/"
                        "investment-announcement"
                    ),

                "published_at":
                    None,

                "source":
                    source[
                        "name"
                    ],
            },
            {
                "title":
                    "Another investment",

                "url":
                    (
                        "https://example.com/"
                        "another-investment"
                    ),

                "published_at":
                    None,

                "source":
                    source[
                        "name"
                    ],
            },
        ]

    monkeypatch.setattr(
        (
            "services.source_probe_service."
            "discover_source"
        ),
        fake_discover_source,
    )

    result = (
        probe_source_candidate(
            name="Example Ventures",
            method="sitemap",
            url=(
                "https://example.com/"
                "sitemap.xml"
            ),
            include_url_patterns=[
                "/investment-",
                "/another-",
            ],
        )
    )

    assert (
        result[
            "status"
        ]
        == "productive"
    )

    assert (
        result[
            "discovered"
        ]
        == 2
    )

    assert (
        result[
            "dated"
        ]
        == 0
    )

    assert (
        result[
            "undated"
        ]
        == 2
    )

    assert (
        result[
            "source_config"
        ][
            "method"
        ]
        == "sitemap"
    )


def test_empty_probe_is_distinct_from_failure(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "services.source_probe_service."
            "discover_source"
        ),
        lambda source: [],
    )

    result = (
        probe_source_candidate(
            name="Example Ventures",
            method="html",
            url="https://example.com/news",
            link_selector="a[href]",
        )
    )

    assert (
        result[
            "status"
        ]
        == "empty"
    )

    assert (
        result[
            "discovered"
        ]
        == 0
    )


def test_failed_probe_is_reported(
    monkeypatch,
):
    monkeypatch.setattr(
        (
            "services.source_probe_service."
            "discover_source"
        ),
        lambda source: None,
    )

    result = (
        probe_source_candidate(
            name="Example Ventures",
            method="rss",
            url="https://example.com/feed",
        )
    )

    assert (
        result[
            "status"
        ]
        == "failed"
    )

    assert (
        result[
            "discovered"
        ]
        == 0
    )


def test_probe_rejects_unsupported_method():
    with pytest.raises(
        ValueError,
        match="Unsupported probe method",
    ):
        probe_source_candidate(
            name="Example Ventures",
            method="api",
            url="https://example.com/api",
        )


def test_probe_passes_generic_rules_to_discovery(
    monkeypatch,
):
    captured = {}

    def fake_discover_source(
        source,
    ):
        captured.update(
            source
        )

        return []

    monkeypatch.setattr(
        (
            "services.source_probe_service."
            "discover_source"
        ),
        fake_discover_source,
    )

    probe_source_candidate(
        name="Example Ventures",
        method="sitemap",
        url="https://example.com/sitemap.xml",
        include_url_patterns=[
            "/news/",
        ],
        exclude_url_patterns=[
            "/team/",
        ],
        exclude_url_regex_patterns=[
            r"/tag/",
        ],
        sitemap_include_patterns=[
            "post-sitemap",
        ],
        max_discovery_items=25,
    )

    assert (
        captured[
            "include_url_patterns"
        ]
        == [
            "/news/"
        ]
    )

    assert (
        captured[
            "exclude_url_patterns"
        ]
        == [
            "/team/"
        ]
    )

    assert (
        captured[
            "exclude_url_regex_patterns"
        ]
        == [
            r"/tag/"
        ]
    )

    assert (
        captured[
            "sitemap_include_patterns"
        ]
        == [
            "post-sitemap"
        ]
    )

    assert (
        captured[
            "max_discovery_items"
        ]
        == 25
    )