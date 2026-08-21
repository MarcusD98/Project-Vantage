from unittest.mock import patch

from app import app


def _report():
    return {
        "filters": {
            "enabled_only": True,
            "source_type": None,
        },

        "summary": {
            "sources": 12,
            "incremental_capable": 12,
            "historical_capable": 3,
            "historical_capability_rate": 25.0,
            "sources_with_evidence": 8,
            "sources_with_12m_coverage": 2,
            "sources_with_24m_coverage": 1,
            "stored_evidence": 420,
            "extraction_attempts": 150,
            "promoted_extractions": 110,
            "unique_funding_events": 72,
        },

        "by_source_type": [
            {
                "source_type": "investor",
                "count": 8,
            },
            {
                "source_type": "publication",
                "count": 4,
            },
        ],

        "sources": [
            {
                "key": "index-ventures",
                "name": "Index Ventures",
                "source_type": "investor",
                "region": "Global",
                "enabled": True,
                "incremental_capable": True,
                "historical_capable": True,
                "incremental_method": "sitemap",
                "historical_method": "sitemap",
                "stored_evidence": 100,
                "dated_evidence": 95,
                "undated_evidence": 5,
                "oldest_evidence_at": None,
                "newest_evidence_at": None,
                "coverage_days": 500,
                "coverage_status": "12m_plus",
                "extraction_attempts": 40,
                "promote": 30,
                "review": 5,
                "reject": 5,
                "pending": 0,
                "promoted": 29,
                "promotion_rate": 96.7,
                "quarantine_rate": 25.0,
                "supported_funding_events": 25,
                "unique_funding_events": 12,
                "multi_source_funding_events": 13,
                "funding_overlap_rate": 0.52,
            },
        ],
    }


def test_observation_report_command_is_registered():
    runner = app.test_cli_runner()

    result = runner.invoke(
        args=[
            "vantage",
            "--help",
        ]
    )

    assert result.exit_code == 0

    assert (
        "observation-report"
        in result.output
    )


def test_observation_report_renders_baseline():
    runner = app.test_cli_runner()

    with patch(
        (
            "services.corpus_cli."
            "get_observation_scale_report"
        ),
        return_value=_report(),
    ) as report_mock:
        result = runner.invoke(
            args=[
                "vantage",
                "observation-report",
            ]
        )

    assert result.exit_code == 0

    report_mock.assert_called_once_with(
        enabled_only=True,
        source_type=None,
    )

    assert (
        "Vantage Observation Baseline"
        in result.output
    )

    assert (
        "Sources:                 12"
        in result.output
    )

    assert (
        "Historical-capable:      3"
        in result.output
    )

    assert (
        "Sources with >=12m span: 2"
        in result.output
    )

    assert (
        "Stored evidence:         420"
        in result.output
    )

    assert (
        "Unique funding events:   72"
        in result.output
    )

    assert (
        "Index Ventures"
        in result.output
    )

    assert (
        "Coverage class:        12m_plus"
        in result.output
    )


def test_observation_report_passes_source_type_filter():
    runner = app.test_cli_runner()

    report = _report()

    report[
        "filters"
    ][
        "source_type"
    ] = "investor"

    with patch(
        (
            "services.corpus_cli."
            "get_observation_scale_report"
        ),
        return_value=report,
    ) as report_mock:
        result = runner.invoke(
            args=[
                "vantage",
                "observation-report",
                "--source-type",
                "investor",
            ]
        )

    assert result.exit_code == 0

    report_mock.assert_called_once_with(
        enabled_only=True,
        source_type="investor",
    )

    assert (
        "Source type:             investor"
        in result.output
    )


def test_observation_report_can_include_disabled_sources():
    runner = app.test_cli_runner()

    with patch(
        (
            "services.corpus_cli."
            "get_observation_scale_report"
        ),
        return_value=_report(),
    ) as report_mock:
        result = runner.invoke(
            args=[
                "vantage",
                "observation-report",
                "--include-disabled",
            ]
        )

    assert result.exit_code == 0

    report_mock.assert_called_once_with(
        enabled_only=False,
        source_type=None,
    )

    assert (
        "Enabled only:            no"
        in result.output
    )


def test_observation_report_handles_empty_cohort():
    runner = app.test_cli_runner()

    empty_report = {
        "filters": {
            "enabled_only": True,
            "source_type": "company",
        },

        "summary": {
            "sources": 0,
            "incremental_capable": 0,
            "historical_capable": 0,
            "historical_capability_rate": 0.0,
            "sources_with_evidence": 0,
            "sources_with_12m_coverage": 0,
            "sources_with_24m_coverage": 0,
            "stored_evidence": 0,
            "extraction_attempts": 0,
            "promoted_extractions": 0,
            "unique_funding_events": 0,
        },

        "by_source_type": [],
        "sources": [],
    }

    with patch(
        (
            "services.corpus_cli."
            "get_observation_scale_report"
        ),
        return_value=empty_report,
    ):
        result = runner.invoke(
            args=[
                "vantage",
                "observation-report",
                "--source-type",
                "company",
            ]
        )

    assert result.exit_code == 0

    assert (
        "Sources:                 0"
        in result.output
    )

    assert (
        "No sources."
        in result.output
    )

    assert (
        "No sources match the selected filters."
        in result.output
    )