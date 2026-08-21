from unittest.mock import patch

from app import app


def _report():
    return {
        "filters": {
            "source": None,
            "event_type": None,
            "extractor_version": None,
        },

        "extraction_attempts": 10,

        "validation": {
            "pending": {
                "count": 1,
                "percentage": 10.0,
            },

            "promote": {
                "count": 6,
                "percentage": 60.0,
            },

            "review": {
                "count": 2,
                "percentage": 20.0,
            },

            "reject": {
                "count": 1,
                "percentage": 10.0,
            },
        },

        "quarantined": {
            "count": 3,
            "percentage": 30.0,
        },

        "promotion": {
            "eligible_for_promotion": 6,
            "promoted": 5,
            "unpromoted_promote": 1,
            "promotion_rate": 83.3,
        },

        "replay": {
            "unique_evidence_event_pairs": 8,
            "replayed_evidence_event_pairs": 2,
            "replay_attempts": 2,
        },

        "by_event_type": [
            {
                "event_type": "funding_round",
                "count": 7,
            },
            {
                "event_type": "fund_close",
                "count": 3,
            },
        ],

        "by_extractor_version": [
            {
                "extractor_version": "funding-v1",
                "count": 7,
            },
            {
                "extractor_version": "fund-close-v1",
                "count": 3,
            },
        ],

        "by_model": [
            {
                "model": "gpt-5.6-luna",
                "count": 10,
            },
        ],

        "validation_flags": [
            {
                "flag": "missing_company_name",
                "count": 2,
            },
            {
                "flag": "not_fund_close",
                "count": 1,
            },
        ],

        "by_source": [
            {
                "source": "Source A",
                "attempts": 6,
                "promote": 4,
                "review": 1,
                "reject": 1,
                "pending": 0,
                "promoted": 4,
                "unpromoted_promote": 0,
                "promotion_rate": 100.0,
            },
            {
                "source": "Source B",
                "attempts": 4,
                "promote": 2,
                "review": 1,
                "reject": 0,
                "pending": 1,
                "promoted": 1,
                "unpromoted_promote": 1,
                "promotion_rate": 50.0,
            },
        ],
    }


def test_pipeline_report_command_is_registered():
    runner = app.test_cli_runner()

    result = runner.invoke(
        args=[
            "vantage",
            "--help",
        ]
    )

    assert result.exit_code == 0

    assert (
        "pipeline-report"
        in result.output
    )


def test_pipeline_report_renders_measurements():
    runner = app.test_cli_runner()

    with patch(
        (
            "services.corpus_cli."
            "get_extraction_measurements"
        ),
        return_value=_report(),
    ) as measurement_mock:
        result = runner.invoke(
            args=[
                "vantage",
                "pipeline-report",
            ]
        )

    assert result.exit_code == 0

    measurement_mock.assert_called_once_with(
        source=None,
        event_type=None,
        extractor_version=None,
    )

    assert (
        "Vantage Knowledge Pipeline"
        in result.output
    )

    assert (
        "Extraction attempts:     10"
        in result.output
    )

    assert (
        "Successfully promoted:   5"
        in result.output
    )

    assert (
        "Unpromoted PROMOTE:      1"
        in result.output
    )

    assert (
        "Replay attempts:         2"
        in result.output
    )

    assert (
        "missing_company_name"
        in result.output
    )

    assert (
        "Source A"
        in result.output
    )


def test_pipeline_report_passes_filters():
    runner = app.test_cli_runner()

    report = _report()

    report[
        "filters"
    ] = {
        "source": "Source A",
        "event_type": "funding_round",
        "extractor_version": "funding-v2",
    }

    with patch(
        (
            "services.corpus_cli."
            "get_extraction_measurements"
        ),
        return_value=report,
    ) as measurement_mock:
        result = runner.invoke(
            args=[
                "vantage",
                "pipeline-report",
                "--source",
                "Source A",
                "--event-type",
                "funding_round",
                "--extractor-version",
                "funding-v2",
            ]
        )

    assert result.exit_code == 0

    measurement_mock.assert_called_once_with(
        source="Source A",
        event_type="funding_round",
        extractor_version="funding-v2",
    )

    assert (
        "Source:                  Source A"
        in result.output
    )

    assert (
        "Event type:              funding_round"
        in result.output
    )

    assert (
        "Extractor version:       funding-v2"
        in result.output
    )


def test_pipeline_report_handles_empty_database():
    runner = app.test_cli_runner()

    empty_report = {
        "filters": {
            "source": None,
            "event_type": None,
            "extractor_version": None,
        },

        "extraction_attempts": 0,

        "validation": {
            "pending": {
                "count": 0,
                "percentage": 0.0,
            },
            "promote": {
                "count": 0,
                "percentage": 0.0,
            },
            "review": {
                "count": 0,
                "percentage": 0.0,
            },
            "reject": {
                "count": 0,
                "percentage": 0.0,
            },
        },

        "quarantined": {
            "count": 0,
            "percentage": 0.0,
        },

        "promotion": {
            "eligible_for_promotion": 0,
            "promoted": 0,
            "unpromoted_promote": 0,
            "promotion_rate": 0.0,
        },

        "replay": {
            "unique_evidence_event_pairs": 0,
            "replayed_evidence_event_pairs": 0,
            "replay_attempts": 0,
        },

        "by_event_type": [],
        "by_extractor_version": [],
        "by_model": [],
        "validation_flags": [],
        "by_source": [],
    }

    with patch(
        (
            "services.corpus_cli."
            "get_extraction_measurements"
        ),
        return_value=empty_report,
    ):
        result = runner.invoke(
            args=[
                "vantage",
                "pipeline-report",
            ]
        )

    assert result.exit_code == 0

    assert (
        "Extraction attempts:     0"
        in result.output
    )

    assert (
        "No extraction records."
        in result.output
    )

    assert (
        "No validation flags."
        in result.output
    )

    assert (
        "No source measurements."
        in result.output
    )