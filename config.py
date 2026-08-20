# Configure external evidence sources

SOURCES = [
    # -----------------------------------------------------
    # Editorial publications
    # -----------------------------------------------------

    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed",
        "type": "publication",
        "region": "Global",
        "method": "rss",
        "enabled": True,
    },
    {
        "name": "Sifted",
        "url": "https://sifted.eu/feed",
        "type": "publication",
        "region": "Europe",
        "method": "rss",
        "enabled": True,
    },
    {
        "name": "Crunchbase News",
        "url": "https://news.crunchbase.com/feed/",
        "type": "publication",
        "region": "Global",
        "method": "rss",
        "enabled": True,
    },
    {
        "name": "Tech.eu",
        "url": "https://tech.eu/feed/",
        "type": "publication",
        "region": "Europe",
        "method": "rss",
        "enabled": True,
    },
    {
        "name": "EU-Startups",
        "url": "https://www.eu-startups.com/feed/",
        "type": "publication",
        "region": "Europe",
        "method": "rss",
        "enabled": True,
    },
    {
        "name": "VentureBeat",
        "url": "https://venturebeat.com/feed/",
        "type": "publication",
        "region": "Global",
        "method": "rss",
        "enabled": True,
    },
    {
        "name": "Silicon Canals",
        "url": (
            "https://siliconcanals.com/"
            "news/startups/feed/"
        ),
        "type": "publication",
        "region": "Europe",
        "method": "rss",
        "enabled": False,
    },
    {
        "name": "LatAmList",
        "url": "https://latamlist.com/feed",
        "type": "publication",
        "region": "Latin America",
        "method": "rss",
        "enabled": True,
    },
    {
        "name": "Inc42",
        "url": "https://inc42.com/feed/",
        "type": "publication",
        "region": "India",
        "method": "rss",
        "enabled": True,
    },
    {
        "name": "TechCabal",
        "url": "https://techcabal.com/feed/",
        "type": "publication",
        "region": "Africa",
        "method": "rss",
        "enabled": True,
    },

    # -----------------------------------------------------
    # First-party investor sources
    # -----------------------------------------------------

    {
        "name": "Accel",
        "url": "https://www.accel.com/sitemap.xml",
        "type": "investor",
        "region": "Global",
        "method": "sitemap",
        "enabled": True,

        # Sitemap modification age is only a discovery hint.
        "max_age_days": 180,

        # Actual page publication date controls whether the
        # evidence is eligible for current intelligence.
        "max_published_age_days": 180,

        "include_url_patterns": [
            "/news/",
        ],

        "exclude_url_patterns": [
            "/news/insights",
            "/news/portfolio",
            "/news/podcasts",
        ],
    },

    {
        "name": "Index Ventures",
        "url": "https://www.indexventures.com/sitemap.xml",
        "type": "investor",
        "region": "Global",
        "method": "sitemap",
        "enabled": True,

        # Only traverse Index's Perspectives sitemap rather
        # than companies, team, jobs, guides, etc.
        "sitemap_include_patterns": [
            "sitemap-perspectives.xml",
        ],

        # Candidate pages must belong to the Perspectives
        # corpus.
        "include_url_patterns": [
            "/perspectives/",
        ],

        # Remove archive, taxonomy and relationship pages.
        "exclude_url_regex_patterns": [
            r"/perspectives/$",
            r"/perspectives/\d+/$",
            r"/perspectives/news(?:/\d+)?/$",
            r"/perspectives/insights(?:/\d+)?/$",
            r"/perspectives/relationship/",
            r"/perspectives/team-member/",
        ],

        # Sitemap lastmod is only a discovery-priority signal.
        "max_age_days": 180,

        # Bound very large or heavily rewritten sitemaps.
        "max_discovery_items": 100,

        # The actual HTML publication date determines whether
        # evidence is current enough for intelligence.
        "max_published_age_days": 180,
    },
    
    {
        "name": "Sequoia Capital",
        "url": "https://sequoiacap.com/sitemap.xml",
        "type": "investor",
        "region": "Global",
        "method": "sitemap",
        "enabled": True,

        "include_url_patterns": [
            "/article/",
        ],

        "exclude_url_regex_patterns": [
            r"/article/tag/",
        ],

        "max_discovery_items": 100,
        "max_published_age_days": 180,
    },
]


CACHE_DURATION_MINUTES = 5