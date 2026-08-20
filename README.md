# Project Vantage

A Python/Flask venture intelligence application that transforms public venture information into a structured, accumulating knowledge base of companies, investors, funds, financing events, relationships, and market activity.

Vantage began as a simple VC news aggregator.

It is evolving into a lightweight venture-market intelligence system:

```text
Public venture ecosystem
        ↓
Multi-source discovery
        ↓
Evidence documents
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

Vantage increasingly treats **news as one source of evidence rather than the entire observable market**.

The long-term information universe should combine:

- Independent editorial reporting
- Investor / VC first-party content
- Accelerator and ecosystem signals
- Select company first-party evidence
- Targeted structured or official sources where they add clear value

The objective is not simply to ingest more URLs.

It is to build a broader, more representative and more evidence-rich view of venture-market activity.

---

# Product Vision

Vantage has three connected layers.

## 1. Venture Discovery Engine

Understand **what is happening** across the venture ecosystem.

Vantage discovers relevant venture information, filters signal from noise, retrieves source content, and stores the resulting evidence.

The discovery universe can include:

- Editorial publications
- VC firms
- Investor blogs
- Accelerator and ecosystem sources
- Select company sources
- Targeted structured sources

## 2. Venture Knowledge Base

Understand **who is doing what**.

Relevant evidence is transformed into structured companies, investors, funds, financing events, relationships, and supporting source material.

## 3. Venture Intelligence

Understand **what the accumulated activity means**.

As the knowledge base grows, Vantage can analyze investor activity, sector momentum, capital formation, funding patterns, geographies, relationships, strategic themes, and changes over time.

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
                 DISCOVERY ENGINE
               "What is happening?"
                         ▲
                         │
                  source discovery
                         │
              ─────────────────────
                 PUBLIC ECOSYSTEM
              ─────────────────────
```

---

# Current State

Vantage has progressed substantially beyond its original RSS-aggregator prototype.

The application now has a working end-to-end architecture:

```text
Source discovery
      ↓
Evidence normalization
      ↓
Deduplication & classification
      ↓
Full-content retrieval
      ↓
LLM structured extraction
      ↓
Entity normalization & resolution
      ↓
Event resolution
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

- Multi-source editorial ingestion
- Persistent evidence storage
- Improved full-article extraction
- Funding-round extraction
- Fund-close extraction
- Company and investor entities
- Fund entities
- Entity aliases
- Stable entity identity
- Entity resolution
- Human review of uncertain resolutions
- Canonical funding-event matching
- Multi-source funding-event evidence
- Historical funding-event reconciliation
- Sector taxonomy normalization
- Funding-stage taxonomy normalization
- Data-quality monitoring
- Company profiles
- Investor profiles
- Structured funding views
- Market-intelligence dashboard
- Unified intelligence pipeline
- Automated tests

Vantage is therefore no longer simply a news application.

It is an early **venture intelligence system**.

---

# 1. Source Discovery & Ingestion

The ingestion layer provides the evidence foundation for the entire application.

Vantage began with RSS-based editorial news ingestion. That remains useful, but the source model is evolving from a **news-feed architecture** toward a broader **venture-source discovery architecture**.

Current capabilities include:

- Multiple configurable editorial sources
- RSS parsing with `feedparser`
- Evidence normalization
- URL-based deduplication
- HTML cleaning with BeautifulSoup
- VC relevance filtering
- Article categorization
- Persistent storage
- Source-health monitoring

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
- Evidence diversity
- Classification quality
- Source provenance
- Signal quality

## Current Source Universe

The current source network is primarily composed of venture and technology publications accessed through RSS.

This provides useful broad discovery, but it introduces an important limitation:

> **Editorial coverage is not the same thing as market coverage.**

Media coverage is influenced by:

- Geography
- Company visibility
- PR activity
- Publication focus
- Funding-round size
- Editorial selection
- Syndication patterns

Vantage should therefore avoid treating its observed dataset as a complete representation of the venture market.

## Source Network V2

The next source architecture should combine several evidence classes:

```text
EDITORIAL SOURCES
TechCrunch
Sifted
Tech.eu
TechCabal
Inc42
etc.

        +

INVESTOR / VC FIRST-PARTY SOURCES
Accel
Sequoia
Andreessen Horowitz
Index Ventures
Atomico
Balderton
etc.

        +

ECOSYSTEM SIGNALS
Accelerators
Venture programs
Demo days
Specialist investor publications
Founder / investor ecosystems

        +

SELECTIVE COMPANY SOURCES
Newsrooms
Press releases
Blogs

        +

TARGETED STRUCTURED / OFFICIAL SOURCES
Selected APIs
Public datasets
Regulatory or registry information
where a specific use case justifies them
```

Different source types provide different kinds of evidence:

```text
Publication
    ↓
Independent discovery / reporting

Investor
    ↓
Investment confirmation / strategy / thesis

Company
    ↓
First-party financing or company announcement

Structured source
    ↓
Validation / enrichment
```

Over time, multiple sources should converge on the same canonical event:

```text
                    EVENT
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
    Publication   Investor Post   Company PR
```

This improves both coverage and confidence.

---

# 2. Full-Article Processing

Titles and summaries are often insufficient for reliable structured extraction.

Vantage can therefore retrieve and persist the underlying source content.

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
Discovered URL
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

# 3. Source Discovery Architecture

Vantage should avoid creating a bespoke scraper or service for every external website.

The scalable model is:

```text
                         SOURCE REGISTRY
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
               RSS         Sitemap       HTML Index
                 │             │             │
                 └─────────────┼─────────────┘
                               ▼
                       DISCOVERY ITEM
                               │
                               ▼
                    EXISTING VANTAGE PIPELINE
```

A source should primarily describe **how content can be discovered**, rather than requiring its own Python implementation.

Conceptually:

```text
Source
├── name
├── source_type
│      ├── publication
│      ├── investor
│      ├── ecosystem
│      ├── company
│      └── structured
├── acquisition_method
│      ├── rss
│      ├── sitemap
│      ├── html
│      └── api
├── region
├── URL / discovery configuration
└── enabled
```

The initial reusable discovery adapters should remain deliberately small:

- RSS
- Sitemap
- Generic HTML listing

Each adapter should emit the same normalized evidence object:

```text
title
url
published_at
summary
source
source_type
```

Everything downstream should remain source-agnostic.

This creates an important architectural boundary:

```text
DISCOVERY
    ↓
NORMALIZED EVIDENCE
    ↓
CONTENT EXTRACTION
    ↓
INTELLIGENCE PIPELINE
```

A new VC firm should therefore usually require **configuration**, not a new service file.

This keeps the source network lean, adaptable and scalable.

---

# 4. AI-Assisted Event Extraction

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
Evidence document
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

# 5. Structured Knowledge Base

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

The `Article` model increasingly represents an **evidence document**, rather than only a traditional news article.

An evidence document may ultimately originate from:

- An independent publication
- An investor investment announcement
- A VC thesis or portfolio update
- An accelerator announcement
- A company newsroom
- Another selected public source

This allows the downstream knowledge architecture to remain largely unchanged even as the upstream source universe expands.

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
- First-party investment announcements
- Potential strategic or thesis signals

This is the foundation of the Vantage ecosystem map.

---

# 6. Entity Resolution

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

Aliases now use stable database-backed entity identity rather than relying solely on mutable name strings.

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

# 7. Event Resolution & Multi-Source Evidence

Multiple sources frequently describe the same underlying venture event.

For example:

```text
Tech publication:
Acme raises $40M Series B

Investor:
Why we invested in Acme

Company:
Acme closes Series B led by Sequoia
```

should ultimately become:

```text
3 source documents
        ↓
1 canonical funding event
        ↓
Acme
$40M
Series B
Sequoia
```

rather than three independent funding rounds.

Vantage now includes:

- Canonical funding-event matching
- Multi-source article relationships
- Historical duplicate auditing
- Generic historical reconciliation
- Safe canonical event selection
- Preservation of supporting evidence across merges

This allows the knowledge base to increasingly represent **real-world events**, rather than merely individual articles.

---

# 8. Human Review & Data Quality

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

Review candidates are linked to stable entity identities.

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

# 9. Taxonomy & Analytical Consistency

Free-form source-derived descriptions are useful for fidelity, but aggregated intelligence requires consistent analytical categories.

Vantage therefore preserves source-derived descriptions while introducing canonical analytical taxonomies.

Current examples include:

```text
raw_sector
     ↓
canonical_sector
```

and:

```text
raw_round_type
     ↓
canonical_round_type
```

Examples:

```text
Healthtech
Health technology
Digital health
        ↓
Health Tech
```

and:

```text
pre-seed
Pre Seed
pre-Seed
        ↓
Pre-Seed
```

The objective is not to build an enormous taxonomy.

It is to make aggregated intelligence trustworthy.

Future taxonomy areas may include:

- Geography
- Investor type
- Fund strategy
- Investment theme

---

# 10. Product Interface

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
- Supporting source documents

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

Investor pages can increasingly expose:

- Recorded investment activity
- Portfolio companies
- Financing events
- Lead-investor activity
- Fund activity
- Stage exposure
- Sector exposure
- Geographic exposure
- Frequent co-investors
- Activity over time
- First-party investment announcements
- Emerging investment themes

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

Vantage does not yet present misleading aggregate market totals where the underlying dataset or source coverage cannot support them reliably.

---

# 11. Investor Intelligence

Investor intelligence is strategically important because leading VC firms provide two different classes of signal.

## Investment Signals

```text
Investor
   ↓
backs Company
   ↓
Funding Round
```

Examples include:

- New investment
- Lead / co-lead investment
- Follow-on investment
- New fund
- New geography
- New sector exposure

## Thesis Signals

Investor publications can also reveal what firms are increasingly focused on before those themes are fully visible in market-wide funding statistics.

Potential future signals include:

- Repeated writing on a technology theme
- New specialist partners
- New sector theses
- Changes in investment strategy
- Clusters of new investments in a theme

For example:

```text
Several AI-infrastructure investments
        +
multiple AI-infrastructure essays
        +
new specialist partner
        ↓
possible emerging investor conviction
```

Vantage should initially focus on capturing investor first-party content reliably before attempting sophisticated thesis inference.

---

# Architecture & Data Integrity Hardening v1

Vantage completed an initial architecture and data-integrity hardening phase before expanding the source universe further.

Key improvements include:

- Unified intelligence-pipeline orchestration
- Explicit transaction ownership
- Idempotent processing behavior
- Canonical funding-event matching
- Multi-source funding-event evidence
- Historical funding-event reconciliation
- Sector taxonomy normalization
- Funding-stage taxonomy normalization
- Stable entity identity
- Scoped entity aliases
- Foreign-key-backed alias resolution
- Human review backed by stable entity references
- Expanded automated test coverage

This phase was intentionally completed before aggressively scaling the dataset.

The principle is:

> **Scaling a weak data model creates larger data-quality problems.**

The objective was therefore to establish a trustworthy foundation before expanding coverage.

---

# Current Architecture

At the current checkpoint:

```text
                     PUBLIC ECOSYSTEM
                           │
                           ▼
                      SOURCE REGISTRY
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Publications    Investors     Ecosystem
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    SOURCE DISCOVERY
                           │
                           ▼
                  NORMALIZED EVIDENCE
                           │
                           ▼
                 CONTENT EXTRACTION
                           │
                           ▼
                    CLASSIFICATION
                           │
                           ▼
                   LLM EXTRACTION
                           │
                           ▼
                  ENTITY RESOLUTION
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       CONFIDENT RECORD           REVIEW REQUIRED
              │                         │
              └────────────┬────────────┘
                           ▼
                    EVENT RESOLUTION
                           │
                           ▼
                    KNOWLEDGE BASE
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
       Companies        Investors         Funds
           │               │               │
           └──────── Events & Relationships
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

Articles and other public documents are source material from which structured ecosystem knowledge is created.

## 3. Reliability precedes sophisticated analytics

A beautiful dashboard built on fragmented entities, duplicated events or weak source coverage produces misleading intelligence.

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
- Transaction ownership
- Event reconciliation rules

## 6. Keep human review for genuinely ambiguous cases

Not every uncertain entity or event should be automatically resolved.

## 7. Prefer configuration over bespoke source code

A new source should usually require source configuration rather than a dedicated scraper or service.

## 8. Measure the observed universe

Vantage should distinguish:

> **Observed activity**

from:

> **Total market activity**

until source coverage is broad enough to support stronger claims.

## 9. Build progressively

```text
Source
  ↓
Evidence
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

**Status: substantially achieved**

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

## Phase 2 — Structured Knowledge Layer

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
- Human resolution review
- Data-quality monitoring

---

## Phase 3 — Pipeline, Event & Entity Integrity

**Status: v1 complete**

Delivered:

- Unified `vantage ingest` lifecycle
- Safe failure handling
- Idempotent intelligence processing
- Processing counters and operational reporting
- Canonical funding-event matching
- Multi-source funding evidence
- Historical duplicate reconciliation
- Stable entity identity
- Foreign-key-backed aliases
- Stable human-review candidate references
- Sector taxonomy normalization
- Funding-stage taxonomy normalization
- Expanded regression testing

This established the first reliable Vantage knowledge-building engine.

---

## Phase 4 — Source Network V2

**Status: current development focus**

The next major constraint is no longer basic data structure.

It is **coverage**.

The existing dataset is derived primarily from editorial RSS sources.

The next objective is to broaden the observable venture universe without creating a large collection of bespoke scrapers.

Target architecture:

```text
SOURCE REGISTRY
      │
      ├── RSS
      ├── Sitemap
      └── HTML listing
              ↓
       Normalized evidence
              ↓
       Existing Vantage pipeline
```

### Priority Source Expansion

#### Investor / VC First-Party Sources

Highest priority.

Track strategically important firms across:

- Global multi-stage VC
- US venture
- European venture
- Seed investors
- Growth investors
- AI specialists
- Fintech specialists
- Climate investors
- Deep-tech investors
- Defence investors
- Important regional firms

Investor first-party sources can provide:

- Investment announcements
- Lead / co-lead confirmation
- Portfolio activity
- Fund announcements
- Investment theses
- Strategic themes

#### Ecosystem Signals

Potential sources include:

- Accelerators
- Venture programs
- Demo days
- Specialist investor publications
- Important founder and investor ecosystems
- Selected sector communities

These may provide earlier signals than mainstream editorial coverage.

#### Company Sources

Company first-party monitoring should remain selective rather than universal.

Possible future candidates include:

- Watchlisted companies
- High-momentum companies
- Companies backed by tracked investors
- Companies already prominent in the Vantage graph

#### Structured / Official Sources

Use selectively where they answer a concrete question.

Potential uses:

- Identity validation
- Legal names
- Corporate existence
- Specific financing signals
- Fund registration
- Structured enrichment

Vantage should not become a generic regulatory-document processing platform.

### Source Architecture Principles

1. Prefer configuration over bespoke source code.
2. Add acquisition adapters only when they generalize across multiple sources.
3. Preserve source provenance.
4. Treat first-party evidence as authoritative for certain facts, but not as unbiased commentary.
5. Measure observed coverage rather than pretending the dataset represents the entire market.

---

## Phase 5 — Corpus Expansion & Coverage Intelligence

**Status: follows Source Network V2**

The objective is to move from dozens of canonical observations toward hundreds and eventually thousands.

Scale should expose remaining weaknesses in:

- Entity resolution
- Event resolution
- Content extraction
- Classification
- Taxonomy
- Source reliability
- Geographic coverage
- Source-type coverage

Coverage itself should become measurable.

Potential future metrics:

```text
Tracked editorial sources
Tracked investor sources
Tracked ecosystem sources

Events by source type

Events with:
1 supporting source
2 supporting sources
3+ supporting sources

Geographic source coverage
Sector source coverage
Investor-source coverage
```

Vantage should distinguish:

> **Observed activity**

from:

> **Total market activity**

until dataset coverage supports stronger claims.

---

## Phase 6 — Product Intelligence V2

**Status: foundation exists**

Once the source universe and corpus are broader, deepen the intelligence layer.

### Investor Intelligence

Investor profiles should answer:

- How active is this investor?
- Which companies has it backed?
- How often does it lead?
- Which sectors does it target?
- Which stages does it target?
- Which geographies does it cover?
- Which investors does it frequently co-invest with?
- Which funds has it raised?
- How is its activity changing?
- What themes is it increasingly discussing or investing behind?

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

Potential analysis:

- Fund history by VC firm
- Fund sizes
- Strategies
- Geography
- Vintage
- Capital formation over time

### Market Intelligence

Potential analysis:

- Investor activity
- Sector activity
- Stage activity
- Geography activity
- Fund formation
- Co-investment relationships
- Ecosystem concentration
- Emerging themes

---

## Phase 7 — Time-Series & Signal Intelligence

A market-intelligence platform should understand change, not merely state.

```text
Current activity
        +
Historical activity
        +
Change over time
        =
Market signal
```

Potential signals:

- Trending sectors
- Emerging investors
- Investor strategy changes
- Funding acceleration
- Stage shifts
- Geographic momentum
- Fundraising cycles
- Co-investment changes

Vantage should initially expose transparent period-over-period data before creating opaque composite momentum scores.

---

## Phase 8 — Search & Ecosystem Discovery

As the knowledge base grows, Vantage should become directly explorable.

Potential queries:

```text
European defence startups

AI companies in Germany

Seed rounds above $5M

Fintech investors active at Series A

VC funds closed in 2026

Companies backed by both Accel and Sequoia

Investors increasing activity in robotics
```

Potential navigation:

```text
VANTAGE

News
Funding
Companies
Investors
Funds
Intelligence
Sources
Data Quality
```

---

## Phase 9 — Productionization

**Status: intentionally deferred**

Production infrastructure should be introduced only when operating requirements justify it.

Potential future transition:

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
Docker
Backups
```

Potential capabilities include:

- PostgreSQL
- Scheduled ingestion
- Background workers
- Production WSGI server
- Docker
- Cloud deployment
- CI/CD
- Secret management
- Logging and monitoring
- Automated backups

These should be introduced when they solve real constraints rather than because they are conventional components of production software.

---

# Near-Term Execution Plan

From the current checkpoint:

```text
CURRENT CHECKPOINT

Trustworthy Vantage knowledge-building engine
        │
        ▼
1. SOURCE DISCOVERY ABSTRACTION

Generic discovery interface
RSS + sitemap + HTML
        │
        ▼
2. INVESTOR SOURCE NETWORK

Add a focused first group of top VC firms
        │
        ▼
3. ECOSYSTEM SIGNAL SOURCES

Accelerators / specialist ecosystems
        │
        ▼
4. CORPUS EXPANSION

Dozens → hundreds → thousands
of canonical observations
        │
        ▼
5. COVERAGE MEASUREMENT

Understand what Vantage can and cannot observe
        │
        ▼
6. PRODUCT INTELLIGENCE V2

Investor / company / market intelligence
        │
        ▼
7. TIME-SERIES SIGNALS

Momentum and changing activity
        │
        ▼
8. SEARCH & DISCOVERY

Structured exploration across the ecosystem
        │
        ▼
9. PRODUCTIONIZATION

Only when continuous operation justifies it
```

---

# Immediate Development Priority

The immediate engineering objective is:

> **Expand Vantage from an RSS-centric news ingestion system into a generic multi-source venture discovery engine without materially increasing architectural complexity.**

The downstream intelligence architecture already largely exists.

The next challenge is upstream coverage.

Target:

```text
Source Registry
      ↓
Reusable Discovery Adapters
      ↓
Normalized Evidence
      ↓
Existing Vantage Intelligence Pipeline
```

The first implementation should remain deliberately narrow:

```text
RSS
Sitemap
Generic HTML listing
```

The objective is not to anticipate every possible website architecture.

It is to prove that a small number of reusable acquisition methods can support a materially broader venture-information universe.

The first major source expansion should prioritize **leading VC firms**, because they provide especially valuable information about:

- New investments
- Lead investments
- Portfolio formation
- Fund formation
- Sector conviction
- Emerging investment theses

Once this architecture is proven across a small but diverse set of investor websites, Vantage can expand the source registry primarily through configuration rather than source-specific code.

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
- Universal company-site crawling
- Generic regulatory-document processing
- Recommendation engines
- Premature cloud infrastructure
- Replacing Flask/Jinja without a genuine product constraint

The system should remain as simple as possible while the source universe, data, intelligence, and product model mature.

---

# Strategic Direction

Vantage started with:

```text
"Show me relevant VC news."
```

It progressed to:

```text
"Turn venture reporting into structured companies,
investors, funds and financing events."
```

The current stage is:

```text
"Continuously build a trustworthy historical
model of venture-market activity from a broader
and more diverse evidence universe."
```

The next product stage is:

```text
"Show me what the most important investors,
companies and ecosystems are actually doing."
```

And the longer-term ambition is:

```text
"Tell me what is changing across the venture ecosystem,
who is driving that change, and where meaningful
new signals are beginning to emerge."
```

That is the path from:

```text
NEWS AGGREGATOR
      ↓
KNOWLEDGE BASE
      ↓
VENTURE INTELLIGENCE SYSTEM
      ↓
VENTURE SIGNAL PLATFORM
```

The objective is not merely to collect venture information.

It is to build a trustworthy system that continuously converts a broad public evidence universe into structured market knowledge and increasingly useful signals.