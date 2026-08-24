import os

from dotenv import load_dotenv

from source_registry import (
    get_discovery_sources,
)


# ---------------------------------------------------------
# Local environment
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Application configuration
# ---------------------------------------------------------

DEFAULT_DATABASE_URL = (
    "sqlite:///vc_news.db"
)


def get_database_url():
    """
    Return the configured Vantage database URL.

    Local development preserves the existing SQLite
    database location unless DATABASE_URL is explicitly
    provided.
    """
    return (
        os.getenv("DATABASE_URL")
        or DEFAULT_DATABASE_URL
    )


# ---------------------------------------------------------
# Incremental source compatibility view
# ---------------------------------------------------------
#
# Existing Vantage services currently import:
#
#     from config import SOURCES
#
# Preserve that contract while the underlying source model
# moves to the unified source registry.
# ---------------------------------------------------------

SOURCES = get_discovery_sources(
    mode="incremental",
)


CACHE_DURATION_MINUTES = 5