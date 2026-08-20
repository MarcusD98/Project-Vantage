BACKFILL_SOURCES = [
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/2026/",
        "type": "publication",
        "region": "Global",
        "method": "html",
        "enabled": True,

        "link_selector": "h3 a",

        "pagination_url_pattern": (
            "https://techcrunch.com/"
            "2026/page/{page}/"
        ),

        "include_url_patterns": [
            "techcrunch.com/2026/",
        ],

        "exclude_url_patterns": [
            "/page/",
        ],

        # Around one month of archive depth
        # based on the live pilot.
        "max_discovery_pages": 20,

        # Hard discovery safety bound.
        "max_discovery_items": 500,
    },
]