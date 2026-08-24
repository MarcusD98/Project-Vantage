from config import (
    DEFAULT_DATABASE_URL,
    get_database_url,
)


def test_database_url_defaults_to_local_sqlite(
    monkeypatch,
):
    monkeypatch.delenv(
        "DATABASE_URL",
        raising=False,
    )

    assert (
        get_database_url()
        == DEFAULT_DATABASE_URL
    )


def test_database_url_can_be_overridden(
    monkeypatch,
):
    database_url = (
        "sqlite:///:memory:"
    )

    monkeypatch.setenv(
        "DATABASE_URL",
        database_url,
    )

    assert (
        get_database_url()
        == database_url
    )

def test_blank_database_url_uses_local_sqlite(
    monkeypatch,
):
    monkeypatch.setenv(
        "DATABASE_URL",
        "",
    )

    assert (
        get_database_url()
        == DEFAULT_DATABASE_URL
    )