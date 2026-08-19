# Project Vantage

A Python/Flask venture intelligence application that transforms public venture news into a structured, accumulating knowledge base of companies, investors, funds, financing events, and market activity.

Vantage began as a simple VC news aggregator.

It is evolving into a lightweight venture-market intelligence system:

```text
Public information
        ↓
News & articles
        ↓
Structured events
        ↓
Canonical entities
        ↓
Relationships
        ↓
Historical knowledge base
        ↓
Market intelligence
```

The central development philosophy is:

> **Information acquisition → structure → intelligence**

Or, from the user's perspective:

```text
What is happening?
        ↓
Who is doing what?
        ↓
What does it mean?
```

---

# Product Vision

Vantage has three connected layers.

## 1. Venture News Engine

Understand **what is happening** across the venture ecosystem.

Vantage ingests venture and startup news, filters signal from noise, categorizes articles, retrieves source content, and stores the resulting evidence.

## 2. Venture Knowledge Base

Understand **who is doing what**.

Relevant articles are transformed into structured companies, investors, funds, financing events, relationships, and supporting evidence.

## 3. Venture Intelligence

Understand **what the accumulated activity means**.

As the knowledge base grows, Vantage can analyze investor activity, sector momentum, capital formation, funding patterns, geographies, relationships, and changes over time.

These are not separate applications.

They are progressively richer layers of the same system.

```text
                VENTURE INTELLIGENCE
                "What does it mean?"
                         ▲
                         │
                    analysis
                         │
                 KNOWLEDGE BASE
                 "Who did what?"
                         ▲
                         │
              entities + relationships
                         │
                    NEWS ENGINE
               "What is happening?"
                         ▲
                         │
                     ingestion
                         │
              ─────────────────────
                 PUBLIC SOURCES
              ─────────────────────
```

---

# Current State

Vantage has progressed substantially beyond its original RSS-aggregator prototype.

The application now has a working end-to-end architecture:

```text
News ingestion
      ↓
Article normalization
      ↓
Deduplication & classification
      ↓
Full-content retrieval
      ↓
LLM structured extraction
      ↓
Entity normalization & resolution
      ↓
Human review where uncertain
      ↓
Structured persistence
      ↓
Data-quality monitoring
      ↓
Profiles & market intelligence
```

The current system includes:

- Multi-source news ingestion
- Persistent article storage
- Improved full-article extraction
- Funding-round extraction
- Fund-close extraction
- Company and investor entities
- Fund entities
- Entity aliases
- Entity resolution
- Human review of uncertain resolutions
- Data-quality monitoring
- Company profiles
- Investor profiles
- Structured funding views
- Market-intelligence dashboard
- Automated tests

Vantage is therefore no longer simply a news application.

It is an early **venture intelligence system**.

---

# 1. News & Ingestion

The ingestion layer provides the evidence foundation for the entire application.

Current capabilities include:

- Multiple configurable RSS sources
- RSS parsing with `feedparser`
- Article normalization
- URL-based deduplication
- HTML cleaning with BeautifulSoup
- VC relevance filtering
- Article categorization
- Persistent storage
- Source-health monitoring
- In-memory feed caching

Current article categories include:

- Funding Round
- Fund News
- M&A
- IPO
- Other

The objective is not simply to collect more headlines.

The objective is to maximize:

- Coverage
- Relevance
- Reliability
- Classification quality
- Evidence quality

Over time, the source network can expand beyond RSS to include VC websites, company announcements, selected APIs, regulatory information, and other useful public sources.

---

# 2. Full-Article Processing

RSS titles and summaries are often insufficient for reliable structured extraction.

Vantage can therefore retrieve and persist the underlying article content.

The article-content service:

- Makes direct HTTP requests
- Uses realistic request headers
- Validates HTML responses
- Removes obvious non-content elements
- Prefers semantic article containers
- Extracts substantive paragraphs
- Removes duplicate and low-value fragments
- Falls back to broader page extraction when necessary
- Rejects insufficient content

Conceptually:

```text
RSS item
   ↓
Article URL
   ↓
HTML retrieval
   ↓
Article-body extraction
   ↓
Clean source text
   ↓
Persistent Article.content
```

Articles also maintain intelligence-processing state so that successfully processed records do not need to be repeatedly sent through the LLM pipeline.

---

# 3. AI-Assisted Event Extraction

Vantage uses the OpenAI API with validated structured outputs to transform unstructured reporting into machine-readable venture events.

The principle is deliberately conservative:

> **Extract only information supported by the source article. Do not guess missing facts.**

## Company Funding Rounds

For company financing events, Vantage can currently extract:

- Whether the article represents a genuine funding round
- Evidence supporting the event
- Company
- Funding amount
- Currency
- Round type
- Participating investors
- Lead investors
- Sector
- Company city
- Company country
- Founding year

Conceptually:

```text
Article
   ↓
Funding-event extraction
   ↓
Company
Funding Round
Investors
Lead Investors
Evidence
```

## VC Fund Closes

Vantage also distinguishes **VC fund formation** from **company fundraising**.

This distinction is important:

```text
COMPANY FUNDING

Investor
   ↓ invests in
Company
   ↓
Funding Round
```

versus:

```text
VC FUND FORMATION

Investor / VC Firm
   ↓ manages
Fund
   ↓
Fund Close
```

For fund-close events, Vantage can extract:

- Whether the article represents a fund close
- Supporting event evidence
- Investor / VC firm
- Fund name
- Fund size
- Currency
- Close type
- Investment strategy
- Geography
- Vintage year where available

This prevents company financing and VC fund formation from being incorrectly represented as the same type of event.

---

# 4. Structured Knowledge Base

The core value of Vantage increasingly resides in its structured knowledge base rather than in the article feed itself.

Current core entities include:

```text
Article

Company
Investor
FundingRound

Fund
FundClose

EntityAlias
EntityResolutionReview
```

The relationships increasingly resemble:

```text
                    Investor
                   /        \
                  /          \
           invests in       manages
                ↓              ↓
         Funding Round       Fund
                ↓              ↓
             Company       Fund Close

                ↑              ↑
                └──── Article ─┘
                     evidence
```

This allows entities to accumulate history.

A company can accumulate:

- Financing events
- Investors
- Lead investors
- Sector and geographic metadata
- Supporting source evidence

An investor can accumulate:

- Portfolio activity
- Lead investments
- Funds
- Fund-close activity
- Relationships with companies and other investors

This is the foundation of the Vantage ecosystem map.

---

# 5. Entity Resolution

Reliable intelligence requires reliable entity identity.

Real-world organizations frequently appear under different names.

For example:

```text
Andreessen Horowitz
a16z
Andreessen Horowitz (a16z)
```

should represent one investor, not three.

Vantage therefore has a dedicated entity-resolution layer.

Conceptually:

```text
Raw extracted name
        ↓
Normalization
        ↓
Known alias lookup
        ↓
Exact entity matching
        ↓
Conservative similarity analysis
        ↓
Canonical entity
        ↓
Review if uncertain
```

The system supports persistent aliases such as:

```text
a16z
   ↓
Andreessen Horowitz
```

and:

```text
Defence tech investor and builder Gallos
   ↓
Gallos Technologies
```

Entity matching is intentionally conservative.

Generic venture-industry terms such as:

```text
Capital
Ventures
Partners
Fund
```

must not create misleading similarity matches between unrelated organizations.

This matters because poor entity resolution would corrupt:

- Investor activity metrics
- Portfolio histories
- Co-investment relationships
- Funding histories
- Sector analysis
- Market intelligence

---

# 6. Human Review & Data Quality

Vantage does not automatically force uncertain entity matches.

Potential resolutions can instead be persisted as review records.

This creates a human-in-the-loop workflow:

```text
Extracted entity
      ↓
Resolution engine
      ↓
Confident match ──────→ Canonical entity
      │
      └── uncertain ──→ Review queue
                              ↓
                         Human decision
```

The Data Quality dashboard provides visibility into the health of the knowledge base.

Current monitoring includes:

- Company count
- Investor count
- Funding-round count
- Canonical aliases
- Missing company metadata
- Missing funding-event metadata
- Potential duplicate entities
- Entity-resolution reviews
- Canonicalization state

This layer exists because Vantage should prefer a smaller trustworthy dataset over a larger misleading one.

---

# 7. Product Interface

The original article feed has evolved into a shared Vantage product interface.

Current product surfaces include:

## News

Searchable and filterable venture-news monitoring.

## Funding

Structured company financing activity including:

- Company
- Amount
- Currency
- Round type
- Investors
- Lead investors
- Evidence
- Source article

## Company Profiles

Company pages can expose:

- Sector
- Geography
- Founding year
- Funding history
- Investors
- Lead investors
- Event evidence

## Investor Profiles

Investor pages can expose:

- Recorded investment activity
- Portfolio companies
- Financing events
- Lead-investor activity
- Fund activity where available

## Sources

Monitoring of the ingestion network and source health.

## Data Quality

Monitoring and review of structured-data quality, canonicalization, completeness, and entity resolution.

## Intelligence

The first market-intelligence layer derived directly from the structured knowledge base.

Current intelligence surfaces include:

- Knowledge-base counts
- Most active investors
- Lead-investor activity
- Financing activity by sector
- Recent VC fund closes
- Recent company financing events

The Intelligence page is deliberately evidence-driven.

Vantage does not yet present misleading aggregate market totals where the underlying dataset or currency normalization cannot support them reliably.

---

# Current Architecture

At the current checkpoint:

```text
                    PUBLIC SOURCES
                         │
                         ▼
                   NEWS INGESTION
                         │
                         ▼
              NORMALIZE / DEDUPLICATE
                         │
                         ▼
                    CLASSIFICATION
                         │
                         ▼
                ARTICLE EXTRACTION
                         │
                         ▼
                  LLM EXTRACTION
                         │
                         ▼
                  ENTITY RESOLUTION
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
       CONFIDENT RECORD       REVIEW REQUIRED
              │                     │
              └──────────┬──────────┘
                         ▼
                  KNOWLEDGE BASE
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Companies       Investors        Funds
          │              │              │
          └─────── Events & Relationships
                         │
                         ▼
                   DATA QUALITY
                         │
                         ▼
             PROFILES / INTELLIGENCE
```

This is the architectural core of Vantage.

---

# Current Technology

Vantage deliberately remains technically lightweight.

Current core technologies include:

- Python
- Flask
- Jinja
- SQLAlchemy
- SQLite
- Flask-Migrate / Alembic
- `feedparser`
- BeautifulSoup
- `requests`
- OpenAI API
- Pydantic
- `pytest`
- HTML / CSS

The application currently runs locally.

This simplicity is intentional.

Infrastructure should become more sophisticated only when product or engineering requirements justify it.

---

# Development Philosophy

## 1. Information acquisition → structure → intelligence

Every major capability should strengthen this progression.

## 2. News is evidence, not the final product

Articles are source material from which structured ecosystem knowledge is created.

## 3. Reliability precedes sophisticated analytics

A beautiful dashboard built on fragmented entities or duplicated events produces misleading intelligence.

## 4. Prefer useful product capabilities over premature infrastructure

Technical sophistication should solve real constraints.

## 5. Use LLMs where semantic understanding matters

LLMs are valuable for interpreting messy natural-language reporting.

Deterministic code remains preferable for:

- Database constraints
- Known aliases
- Exact matching
- State management
- Aggregation
- Business rules
- Idempotency

## 6. Keep human review for genuinely ambiguous cases

Not every uncertain entity or event should be automatically resolved.

## 7. Build progressively

```text
Source
  ↓
Article
  ↓
Event
  ↓
Entity
  ↓
Relationship
  ↓
Historical Dataset
  ↓
Metric
  ↓
Pattern
  ↓
Insight
```

Each layer should make the next one possible.

---

# Roadmap

## Phase 1 — News & Ingestion Foundation

**Status: largely achieved**

Delivered:

- Multi-source RSS ingestion
- Article normalization
- Deduplication
- Relevance filtering
- Categorization
- Persistent storage
- Search and filtering
- Source-health monitoring
- Full-article retrieval
- Automated tests

---

## Phase 2 — Knowledge Layer

**Status: substantially achieved**

Delivered:

- Company model
- Investor model
- Funding-round model
- Fund model
- Fund-close model
- Company ↔ funding relationships
- Investor ↔ funding relationships
- Lead-investor relationships
- Investor ↔ fund relationships
- LLM structured extraction
- Event evidence
- Company metadata enrichment
- Entity normalization
- Entity aliases
- Entity resolution
- Conservative duplicate detection
- Entity merge tooling
- Human resolution review
- Data-quality dashboard
- Batch intelligence processing

This phase established the first trustworthy structured VC knowledge layer.

---

## Phase 3 — Intelligence Engine

**Status: current development focus**

The highest-impact next objective is to turn the existing collection of working services into a systematic intelligence pipeline.

Today, individual pipeline stages work.

The next step is to orchestrate them.

Target flow:

```text
Fetch sources
      ↓
Discover new articles
      ↓
Normalize & deduplicate
      ↓
Classify
      ↓
Retrieve article content
      ↓
Extract structured intelligence
      ↓
Resolve entities
      ↓
Resolve events
      ↓
Persist
      ↓
Create reviews where necessary
      ↓
Report pipeline results
```

The desired developer experience is eventually something conceptually similar to:

```bash
flask ingest
```

producing a summary such as:

```text
Vantage ingestion complete

Articles discovered:       143
New articles:               28
Content retrieved:          24
Funding events:             11
Fund closes:                 2
Reviews created:             3
Failures:                     4
```

### Immediate priorities

1. Unified ingestion/intelligence orchestration
2. Safe failure isolation
3. Idempotent processing
4. Useful processing counters and logging
5. Larger-scale corpus processing
6. Extraction observability

The objective is to move from:

> Vantage **can** generate intelligence.

to:

> Vantage **systematically builds its own knowledge base**.

---

## Phase 4 — Scale, Taxonomy & Event Quality

**Status: next**

Once the pipeline is operational, the priority becomes dataset depth and analytical consistency.

### Dataset expansion

Vantage needs to move from dozens of structured events toward hundreds and eventually thousands.

Scale is important not merely for coverage.

It exposes problems that small test datasets cannot:

- Entity duplication
- Event duplication
- Classification errors
- Extraction failures
- Weak article retrieval
- Sector fragmentation
- Naming inconsistencies
- Currency inconsistencies
- Repeated syndicated reporting

### Event resolution

Multiple articles may describe the same underlying event.

For example:

```text
Tech publication:
Acme raises $40M Series B

Another publication:
Acme bags $40M in new funding

Company announcement:
Acme closes Series B led by Sequoia
```

should ultimately become:

```text
3 source articles
        ↓
1 canonical funding event
        ↓
Acme
$40M
Series B
Sequoia
```

rather than three independent funding rounds.

### Taxonomy normalization

Free-form extracted metadata eventually needs controlled analytical categories.

Priority taxonomies include:

- Sector
- Stage / round type
- Geography
- Investor type
- Fund strategy

For example:

```text
Generative AI
AI infrastructure
Enterprise AI
Machine Learning
AI applications
```

may need to roll up into a canonical analytical hierarchy while preserving the raw source-derived description.

Conceptually:

```text
raw_sector
     ↓
canonical_sector
```

The objective is not to create an enormous taxonomy.

It is to make aggregated intelligence trustworthy.

---

## Phase 5 — Product Intelligence

**Status: early foundation built**

The first `/intelligence` dashboard now exists.

The next stage is to deepen intelligence once dataset scale supports it.

### Investor Intelligence

Investor profiles should increasingly answer:

- How active is this investor?
- Which companies has it backed?
- How frequently does it lead?
- Which sectors does it invest in?
- Which stages does it target?
- Which geographies does it cover?
- Which investors does it frequently co-invest with?
- Which funds has it raised?
- How is its activity changing over time?

Potential future profile:

```text
SEQUOIA CAPITAL

Tracked investments       18
Lead investments           6

Stage activity
Seed                      7
Series A                  5
Series B                  3

Sector exposure
AI                       38%
Fintech                  21%
Enterprise Software      17%

Frequent co-investors
Andreessen Horowitz       6
Accel                     4
Index Ventures            3
```

### Company Intelligence

Company profiles can evolve toward:

- Financing history
- Funding velocity
- Investor history
- Lead investors
- Sector and geography
- Event timeline
- Capital raised from disclosed rounds

### Fund Intelligence

Fund intelligence can include:

- Fund history by VC firm
- Fund sizes
- Fund strategy
- Geography
- Vintage
- Capital-formation activity over time

### Market Intelligence

Potential analysis areas include:

- Investor activity
- Sector momentum
- Geography activity
- Funding-stage trends
- Fund formation
- Co-investment relationships
- Company funding velocity
- Ecosystem concentration
- Emerging market signals

---

## Phase 6 — Time-Series Intelligence

A market-intelligence system needs to understand not only state, but change.

The analytical model should eventually become:

```text
Current state
      +
Historical state
      +
Change over time
      =
Market signal
```

This can unlock:

- Trending sectors
- Emerging investors
- Funding acceleration
- Stage shifts
- Geographic momentum
- Fundraising cycles
- Investor activity changes

For example, the useful question is not merely:

> How many AI funding rounds has Vantage tracked?

but eventually:

> Is AI financing activity accelerating relative to the previous period?

This is an important transition from database aggregation toward actual market intelligence.

---

## Phase 7 — Search & Ecosystem Discovery

As the knowledge base grows, the ecosystem should become directly searchable and browseable.

Potential navigation:

```text
VANTAGE

News
Funding
Intelligence
Companies
Investors
Funds
Sources
Data Quality
```

### Companies

Search and filter by:

- Sector
- Geography
- Funding stage
- Investors
- Recent activity

### Investors

Search and filter by:

- Sector activity
- Geography
- Stage
- Portfolio
- Lead activity
- Fund activity

### Funds

Search and filter by:

- Manager
- Strategy
- Geography
- Vintage
- Size

Eventually Vantage should support questions such as:

```text
European defence startups

AI companies in Germany

Seed rounds above $5M

Fintech investors active at Series A

VC funds closed in 2026

Companies backed by both Accel and Sequoia
```

---

## Phase 8 — Source Network V2

Source expansion should prioritize **quality and evidence diversity**, not simply the number of feeds.

Potential source network:

```text
EDITORIAL SOURCES
TechCrunch
Sifted
Tech.eu
TechCabal
Inc42
etc.

        +

VC FIRMS
Accel
Sequoia
Index Ventures
Andreessen Horowitz
Atomico
Balderton
etc.

        +

COMPANY SOURCES
Newsrooms
Press releases
Blogs

        +

STRUCTURED / PUBLIC SOURCES
Selected APIs
Regulatory information
Public datasets
```

The long-term goal is multi-source evidence:

```text
                    EVENT
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    Publication   Company PR   Investor Post
```

This can improve both coverage and confidence.

---

## Phase 9 — Productionization

**Status: intentionally deferred**

The current local architecture remains appropriate while product and data-model iteration are rapid.

Eventually Vantage may move from:

```text
Flask
SQLite
Local execution
Manual pipeline invocation
```

toward:

```text
Application server
PostgreSQL
Scheduled ingestion
Background processing
Cloud deployment
Monitoring
CI/CD
Containerization
Backups
```

Potential technologies and capabilities include:

- PostgreSQL
- Background workers
- Scheduled jobs
- Production WSGI server
- Docker
- Cloud deployment
- Logging and monitoring
- CI/CD
- Environment and secret management
- Database backups

These should be introduced when they solve real constraints rather than because they are conventional components of production software.

---

# Near-Term Execution Plan

From the current checkpoint, the highest-impact sequence is:

```text
CURRENT CHECKPOINT
Working Vantage knowledge + intelligence prototype
        │
        ▼
1. UNIFIED INTELLIGENCE PIPELINE
One orchestrated ingestion → intelligence lifecycle
        │
        ▼
2. SCALE THE CORPUS
Hundreds → thousands of structured observations
        │
        ▼
3. EVENT DEDUPLICATION
Multiple articles → one canonical event
        │
        ▼
4. TAXONOMY NORMALIZATION
Consistent sectors, stages, geographies and strategies
        │
        ▼
5. DEEPER PRODUCT INTELLIGENCE
Investors / companies / funds / sectors
        │
        ▼
6. TIME-SERIES INTELLIGENCE
Momentum, acceleration and changing activity
        │
        ▼
7. SEARCH & DISCOVERY
Cross-entity exploration and structured filtering
        │
        ▼
8. SOURCE NETWORK V2
Primary sources and richer evidence
        │
        ▼
9. PRODUCTIONIZATION
Postgres / jobs / Docker / deployment / monitoring
```

---

# Immediate Development Priority

The immediate engineering objective is:

> **Turn Vantage's existing ingestion, extraction, resolution, and persistence services into one reliable, repeatable intelligence pipeline.**

Most individual components already exist.

The next challenge is orchestration.

Vantage should be able to move systematically from:

```text
Fresh public information
        ↓
New article
        ↓
Retrieved evidence
        ↓
Structured event
        ↓
Resolved entities
        ↓
Canonical knowledge
        ↓
Updated intelligence
```

without manually invoking each stage.

This is the bridge between the current working prototype and an actual self-updating venture intelligence system.

---

# What We Are Deliberately Not Prioritizing Yet

Vantage should continue avoiding premature complexity.

Not current priorities:

- Kubernetes
- Microservices
- Complex distributed architecture
- Vector databases without a concrete requirement
- Embeddings simply because they are available
- Generic autonomous agents
- Authentication before user-specific workflows justify it
- Mobile applications
- Elaborate visualizations on small datasets
- Large numbers of low-quality sources
- Recommendation engines
- Premature cloud infrastructure
- Replacing Flask/Jinja without a genuine product constraint

The system should remain as simple as possible while the data, intelligence, and product model mature.

---

# Strategic Direction

Vantage started with:

```text
"Show me relevant VC news."
```

It has progressed to:

```text
"Turn venture news into structured companies,
investors, funds and financing events."
```

The next stage is:

```text
"Continuously build a trustworthy historical
model of venture-market activity."
```

And the longer-term product ambition is:

```text
"Use that model to tell me what is happening
across the venture ecosystem, who is driving it,
and how the market is changing."
```

That is the path from **news aggregator → knowledge base → venture intelligence platform**.