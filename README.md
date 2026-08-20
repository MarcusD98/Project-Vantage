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


# Market Position & Differentiation

Vantage operates in an established private-market and venture-intelligence landscape.

Major platforms already provide substantial coverage of companies, investors, funds, financing events, markets, and private-company activity.

Relevant platforms include:

- PitchBook
- Dealroom
- Tracxn
- CB Insights
- Harmonic

These products demonstrate that there is significant demand for structured private-market intelligence.

They also make an important strategic point clear:

> **Vantage should not attempt to win by simply becoming another startup or funding database.**

The individual components of Vantage are not unique in isolation.

Existing platforms already provide combinations of:

- Company databases
- Investor databases
- Funding-round data
- Fund data
- Market maps
- Startup discovery
- News and event monitoring
- Investor activity
- AI-assisted research
- Market analytics

The opportunity for Vantage therefore lies in how these components are combined and what question the product is designed to answer.

---

## The Traditional Private-Market Model

Many established private-market platforms can be simplified conceptually as:

```text
Large proprietary dataset
        ↓
Companies / investors / deals
        ↓
Search & filtering
        ↓
Profiles
        ↓
Analytics
        ↓
Research
```

These platforms are exceptionally strong at answering questions such as:

```text
Who invested in this company?

How much has this company raised?

Which investors invest in European fintech?

What funds has this VC firm raised?

Which companies raised Series A rounds this year?
```

This is valuable and Vantage will inevitably overlap with parts of this functionality.

However, reproducing the breadth and historical depth of large incumbent private-market databases is not the primary objective.

---

## The Vantage Thesis

Vantage is increasingly being designed around a different starting point:

> **Continuously observe what important participants in the venture ecosystem are actually doing, convert that activity into structured historical knowledge, and identify meaningful changes in behaviour over time.**

Conceptually:

```text
LIVE PUBLIC INFORMATION UNIVERSE

Editorial reporting
Investor / VC websites
Investment announcements
VC thesis content
Fund announcements
Accelerators
Ecosystem sources
Selected company sources
Selected structured sources
        ↓
Evidence acquisition
        ↓
AI understanding
        ↓
Entity resolution
        ↓
Event resolution
        ↓
Evidence-backed knowledge base
        ↓
Historical activity
        ↓
Behavioural change
        ↓
Venture intelligence
```

This creates a subtly different product orientation.

Rather than beginning with:

```text
"What information exists about this company?"
```

Vantage increasingly begins with:

```text
"What are important venture-market participants doing?"
```

and ultimately:

```text
"How is that behaviour changing,
and what might that tell us about the market?"
```

---

## Investor Behaviour as a First-Class Signal

This is why investor / VC intelligence is strategically important to Vantage.

A venture firm produces multiple observable signals.

### Investment Activity

```text
Investor
   ↓
Investment
   ↓
Company
```

Signals include:

- New investments
- Lead investments
- Follow-on investments
- Stage exposure
- Sector exposure
- Geographic exposure
- Co-investor relationships

### Capital Formation

```text
Investor
   ↓
Fund
   ↓
Fund Close
```

Signals include:

- New funds
- Fund size
- Strategy
- Geography
- Vintage
- Changes in capital formation

### Thesis Activity

```text
Investor
   ↓
Public writing
   ↓
Themes / sectors / technologies
```

Signals may eventually include:

- Repeated discussion of a technology
- New sector theses
- New specialist partners
- Changes in strategic language
- Increasing attention to particular markets

Individually, these observations are useful.

Combined historically, they become much more interesting.

For example:

```text
Several AI infrastructure investments
        +
multiple AI infrastructure essays
        +
new specialist partner
        +
increasing lead-investment activity
        ↓
possible emerging investor conviction
```

Vantage should not immediately turn these observations into opaque AI-generated scores.

The first objective is to build the underlying evidence and historical record reliably.

---

## From Investor Profiles to Investor Intelligence

A conventional investor profile might answer:

```text
Accel

Founded: ...
Headquarters: ...
Investments: ...
Funds: ...
Portfolio: ...
```

A mature Vantage investor profile could increasingly answer:

```text
ACCEL

Observed activity
─────────────────

Recent investments
Lead investments
Follow-on investments

Stage exposure
Sector exposure
Geographic exposure

Frequent co-investors

Recent fund activity

Recent thesis activity

Changes in activity over time

Underlying evidence
```

Eventually this could evolve toward questions such as:

```text
Which sectors is Accel increasing exposure to?

Which investors are becoming more active
in European defence technology?

Which firms are increasingly leading
AI infrastructure rounds?

Which investors are moving earlier
or later in funding stage?

Which VC firms are repeatedly investing
and publishing around the same emerging theme?
```

This is the direction in which Vantage becomes more than a database.

---

## From Records to Signals

The long-term analytical progression is:

```text
Evidence
   ↓
Event
   ↓
Entity
   ↓
Relationship
   ↓
Historical activity
   ↓
Change over time
   ↓
Signal
```

For example:

```text
Accel invests in Company A
Index invests in Company B
Lightspeed invests in Company C
        ↓
All three companies are European defence software
        ↓
Additional related investments appear
        ↓
Investor activity increases over multiple periods
        ↓
Potential ecosystem signal
```

A future Vantage intelligence surface might therefore identify:

```text
VANTAGE SIGNAL

Observed investment activity among tracked
venture firms in European defence technology
has increased materially over recent periods.

Active investors:
Accel
Index Ventures
Lightspeed
...

Supporting events:
...

Supporting evidence:
...
```

The important principle is that the signal should remain traceable back to the underlying evidence.

---

## Evidence-Backed Intelligence

Evidence provenance is therefore an important potential differentiator.

Vantage should preserve the chain:

```text
Intelligence
     ↓
Metric / pattern
     ↓
Canonical events
     ↓
Entities
     ↓
Supporting evidence
     ↓
Original public sources
```

This means users should increasingly be able to move from:

```text
"European defence investment appears to be accelerating."
```

to:

```text
Why?
```

and inspect:

- Which investors changed behaviour
- Which financing events contributed
- Which companies were involved
- Which source documents support those events

The objective is not merely to generate conclusions.

It is to build **inspectable intelligence**.

---

## Competitive Positioning

Vantage should therefore avoid positioning itself simply as:

```text
A cheaper PitchBook
```

or:

```text
Another startup database
```

or:

```text
An AI news aggregator
```

The more interesting long-term positioning is:

> **An evidence-backed venture intelligence system that continuously observes companies, investors and ecosystems, builds a historical model of their activity, and identifies meaningful changes in venture behaviour.**

This positioning will continue to evolve as the product and dataset mature.

Existing platforms already provide increasingly sophisticated real-time signals, AI research and investor intelligence.

Vantage should therefore assume that this is a competitive market rather than claim an entirely new category.

Its differentiation must ultimately come from execution:

- Source coverage
- Evidence quality
- Entity and event integrity
- Investor-centric intelligence
- Historical behavioural analysis
- Transparency of underlying evidence
- Speed of detecting meaningful changes

---

## Strategic Wedge

The initial wedge should remain narrower than the ultimate product vision.

Vantage should first become exceptionally good at understanding:

> **What are important venture investors actually doing?**

This includes:

```text
What are they investing in?

What are they leading?

What sectors are they entering?

What stages are they targeting?

Where are they investing?

Who are they investing alongside?

What funds are they raising?

What are they writing about?

How is all of this changing?
```

This is why Source Network V2 prioritizes direct investor / VC sources.

Editorial reporting tells Vantage:

```text
"What became news?"
```

Investor first-party sources additionally tell Vantage:

```text
"What did this investor choose to do?"
```

Ecosystem sources can increasingly tell Vantage:

```text
"What may be emerging before it becomes major news?"
```

Together:

```text
Editorial evidence
        +
Investor behaviour
        +
Ecosystem signals
        +
Historical structured data
        ↓
Venture intelligence
```

That is the strategic direction Vantage should test.

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

The longer-term ambition is:

```text
"Tell me what is changing across the venture ecosystem,
who is driving that change, and where meaningful
new signals are beginning to emerge."
```

That creates the progression:

```text
NEWS AGGREGATOR
      ↓
KNOWLEDGE BASE
      ↓
VENTURE INTELLIGENCE SYSTEM
      ↓
VENTURE SIGNAL PLATFORM
```

Vantage is not attempting simply to recreate an incumbent private-market database.

The objective is to build a system that continuously converts a broad public evidence universe into structured historical knowledge and then uses that history to understand **behaviour and change**.

The central strategic question becomes:

> **What are important venture-market participants doing, how is that behaviour changing, and what can those changes tell us?**

The immediate focus is deliberately narrower:

> **Build the best possible observable model of investor / VC behaviour using editorial reporting, investor first-party evidence, ecosystem signals, and structured historical activity.**

If that foundation becomes sufficiently broad and trustworthy, increasingly valuable intelligence follows naturally:

```text
Source coverage
      ↓
Evidence
      ↓
Canonical entities & events
      ↓
Historical behaviour
      ↓
Metrics
      ↓
Change
      ↓
Signals
      ↓
Intelligence
```

The objective is not merely to collect venture information.

It is to build a trustworthy, evidence-backed system for understanding how the venture ecosystem is moving.