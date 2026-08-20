from source_registry import (
    get_discovery_sources,
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
#
# Phase 5 will progressively migrate services to interact
# directly with the registry / fleet runner.
# ---------------------------------------------------------

SOURCES = get_discovery_sources(
    mode="incremental",
)


CACHE_DURATION_MINUTES = 5