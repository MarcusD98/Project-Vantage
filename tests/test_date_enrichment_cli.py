from unittest.mock import patch

from app import app


def _result(
    *,
    recovered=14,
    attempted=20,
    remaining=14,
):
    recovery_rate = (
        round(
            (
                recovered
                / attempted
            )
            * 100,
            1,
        )
        if attempted
        else 0.0
    )

    return {
        "source":
            "Andreessen Horowitz",

        "source_key":
            "a16z",

        "limit":
            20,

        "undated_before":
            28,

        "attempted":
            attempted,

        "dates_recovered":
            recovered,

        "remaining_undated":
            remaining,

        "recovery_rate":
            recovery_rate,
    }


def test_enrich_dates_command_is_registered():
    runner = app.test_cli_runner()

    result = runner.invoke(
        args=[
            "vantage",
            "--help",
        ]
    )

    assert result.exit_code == 0

    assert (
        "enrich-dates"
        in result.output
    )


def test_enrich_dates_command_calls_service():
    runner = app.test_cli_runner()

    with patch(
        (
            "services.corpus_cli."
            "run_date_enrichment"
        ),
        return_value=_result(),
    ) as enrichment_mock:
        result = runner.invoke(
            args=[
                "vantage",
                "enrich-dates",
                "--source",
                "Andreessen Horowitz",
                "--limit",
                "20",
            ]
        )

    assert result.exit_code == 0

    enrichment_mock.assert_called_once_with(
        source_name="Andreessen Horowitz",
        limit=20,
    )

    assert (
        "Vantage Date Enrichment"
        in result.output
    )

    assert (
        "Source:                  Andreessen Horowitz"
        in result.output
    )

    assert (
        "Undated before:          28"
        in result.output
    )

    assert (
        "Attempted:               20"
        in result.output
    )

    assert (
        "Dates recovered:         14"
        in result.output
    )

    assert (
        "Still undated:           14"
        in result.output
    )

    assert (
        "Recovery rate:           70.0%"
        in result.output
    )

    assert (
        "part of the attempted batch"
        in result.output
    )


def test_enrich_dates_command_reports_zero_recovery():
    runner = app.test_cli_runner()

    with patch(
        (
            "services.corpus_cli."
            "run_date_enrichment"
        ),
        return_value=_result(
            recovered=0,
            attempted=20,
            remaining=28,
        ),
    ):
        result = runner.invoke(
            args=[
                "vantage",
                "enrich-dates",
                "--source",
                "a16z",
                "--limit",
                "20",
            ]
        )

    assert result.exit_code == 0

    assert (
        "Dates recovered:         0"
        in result.output
    )

    assert (
        "Recovery rate:           0.0%"
        in result.output
    )

    assert (
        "No publication dates were recovered"
        in result.output
    )


def test_enrich_dates_command_reports_unknown_source():
    runner = app.test_cli_runner()

    with patch(
        (
            "services.corpus_cli."
            "run_date_enrichment"
        ),
        side_effect=ValueError(
            "Unknown source: Imaginary Capital"
        ),
    ):
        result = runner.invoke(
            args=[
                "vantage",
                "enrich-dates",
                "--source",
                "Imaginary Capital",
            ]
        )

    assert result.exit_code != 0

    assert (
        "Unknown source: Imaginary Capital"
        in result.output
    )