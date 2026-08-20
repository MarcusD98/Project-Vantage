from source_registry import (
    get_discovery_sources,
)


# ---------------------------------------------------------
# Historical source compatibility view
# ---------------------------------------------------------
#
# Existing corpus/backfill services currently expect a flat
# BACKFILL_SOURCES collection.
#
# Historical discovery is now defined on the same canonical
# source object as incremental discovery.
#
# This compatibility view can disappear once fleet operations
# consume the unified registry directly.
# ---------------------------------------------------------

BACKFILL_SOURCES = (
    get_discovery_sources(
        mode="historical",
    )
)