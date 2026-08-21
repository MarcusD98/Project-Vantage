from unittest.mock import patch

from app import app


def test_replay_command_is_registered():
    runner = app.test_cli_runner()

    result = runner.invoke(
        args=[
            "vantage",
            "--help",
        ]
    )

    assert result.exit_code == 0

    assert (
        "replay"
        in result.output
    )


def test_replay_command_calls_replay_service():
    runner = app.test_cli_runner()

    replay_result = {
        "article_id": 123,
        "event_type": "funding_round",
        "record_id": 456,
        "extractor_version": "funding-v2",
        "model": "gpt-5.6-luna",
        "validation_state": "promote",
        "validation_flags": [],
        "promoted": True,
        "promoted_at": None,
    }

    with patch(
        (
            "services.corpus_cli."
            "replay_article_by_id"
        ),
        return_value=replay_result,
    ) as replay_mock:
        result = runner.invoke(
            args=[
                "vantage",
                "replay",
                "--article-id",
                "123",
                "--event-type",
                "funding_round",
            ]
        )

    assert result.exit_code == 0

    replay_mock.assert_called_once_with(
        article_id=123,
        event_type="funding_round",
    )

    assert (
        "Extraction record:       #456"
        in result.output
    )

    assert (
        "Validation state:        PROMOTE"
        in result.output
    )

    assert (
        "Promoted:                yes"
        in result.output
    )


def test_replay_command_reports_quarantine():
    runner = app.test_cli_runner()

    replay_result = {
        "article_id": 123,
        "event_type": "funding_round",
        "record_id": 789,
        "extractor_version": "funding-v2",
        "model": "gpt-5.6-luna",
        "validation_state": "review",
        "validation_flags": [
            "missing_company_name",
        ],
        "promoted": False,
        "promoted_at": None,
    }

    with patch(
        (
            "services.corpus_cli."
            "replay_article_by_id"
        ),
        return_value=replay_result,
    ):
        result = runner.invoke(
            args=[
                "vantage",
                "replay",
                "--article-id",
                "123",
                "--event-type",
                "funding_round",
            ]
        )

    assert result.exit_code == 0

    assert (
        "Validation state:        REVIEW"
        in result.output
    )

    assert (
        "missing_company_name"
        in result.output
    )

    assert (
        "Promoted:                no"
        in result.output
    )

    assert (
        "quarantined from canonical knowledge"
        in result.output
    )


def test_replay_command_reports_missing_article():
    runner = app.test_cli_runner()

    with patch(
        (
            "services.corpus_cli."
            "replay_article_by_id"
        ),
        side_effect=ValueError(
            "Article not found: 999"
        ),
    ):
        result = runner.invoke(
            args=[
                "vantage",
                "replay",
                "--article-id",
                "999",
                "--event-type",
                "funding_round",
            ]
        )

    assert result.exit_code != 0

    assert (
        "Article not found: 999"
        in result.output
    )