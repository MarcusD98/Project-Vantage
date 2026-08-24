import os
import subprocess
import sys


def test_llm_extractor_import_does_not_require_openai_credentials():
    """
    Importing Vantage's LLM extraction module must not require
    live OpenAI credentials.

    Credentials are an execution-time dependency for real LLM
    calls, not an import-time dependency for the application or
    test suite.
    """

    environment = os.environ.copy()

    environment.pop(
        "OPENAI_API_KEY",
        None,
    )

    environment.pop(
        "OPENAI_ADMIN_KEY",
        None,
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import services.llm_extractor; "
                "print('LLM extractor import OK')"
            ),
        ],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    assert (
        "LLM extractor import OK"
        in result.stdout
    )
