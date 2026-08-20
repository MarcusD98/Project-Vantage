# Project Vantage

**Project Vantage** is a Python/Flask venture intelligence application that transforms public venture information into a structured, accumulating knowledge base of companies, investors, funds, financing events, relationships, evidence, and market activity.

Vantage began as a simple VC news aggregator.

It is evolving into a lightweight **venture intelligence system**:

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
Behavioural analysis
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
How is that changing?
        ↓
What does it mean?
```

Vantage increasingly treats **news as one source of evidence rather than the entire observable market**.

The long-term information universe should combine:

* Independent editorial reporting
* Investor / VC first-party content
* Accelerator and ecosystem signals
* Select company first-party evidence
* Targeted structured or official sources where they add clear value

The objective is not simply to ingest more URLs.

It is to build a broader, more representative and more evidence-rich historical model of venture-market activity.

---

# Product Vision

Vantage has three connected product layers.

## 1. Venture Discovery Engine

Understand:

> **What is happening?**

Vantage discovers relevant venture information, filters signal from noise, retrieves underlying content, preserves source provenance, and stores usable evidence.

The discovery universe can include:

* Editorial publications
* VC firms
* Investor blogs
* Investment announcements
* Accelerators
* Venture programs
* Ecosystem sources
* Select company sources
* Selected structured or official sources

The Discovery Engine does not need to understand the full meaning of every document.

Its job is to reliably identify and preserve potentially useful evidence.

---

## 2. Venture Knowledge Base

Understand:

> **Who did what?**

Evidence is transformed into structured:

* Companies
* Investors
* Funds
* Financing events
* Fund-close events
* Relationships
* Supporting source evidence
* Canonical identities
* Historical activity

The Knowledge Base should represent real-world organizations and events rather than merely storing isolated articles.

---

## 3. Venture Intelligence

Understand:

> **How is activity changing, and what does it mean?**

As the knowledge base grows, Vantage can increasingly analyze:

* Investor activity
* Lead-investor behaviour
* Stage exposure
* Sector exposure
* Geographic exposure
* Co-investment relationships
* Capital formation
* Funding patterns
* Emerging sectors
* Investor strategy changes
* Ecosystem concentration
* Historical changes in behaviour

These are not separate applications.

They are progressively richer layers of the same system.

```text
                VENTURE INTELLIGENCE
             "What is changing and why?"
                         ▲
                         │
                 historical analysis
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

# Strategic Thesis

Vantage operates in an established private-market and venture-intelligence landscape.

Major platforms already provide substantial company, investor, funding, fund, market, and research data.

Relevant platforms include:

* PitchBook
* Dealroom
* Tracxn
* CB Insights
* Harmonic

Vantage should therefore **not** attempt to win by simply becoming another startup database.

It should not position itself primarily as:

```text
A cheaper PitchBook
```

or:

```text
Another funding database
```

or:

```text
An AI news aggregator
```

The more interesting product thesis is:

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

The system begins less from:

```text
"What information exists about this company?"
```

and increasingly from:

```text
"What are important venture-market participants doing?"
```

and ultimately:

```text
"How is that behaviour changing,
who is driving the change,
and what might that tell us?"
```

---

# Strategic Wedge: Investor Behaviour

The initial wedge should remain narrower than the ultimate product vision.

Vantage should first become exceptionally good at answering:

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

This is why investor / VC first-party sources are strategically important.

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

# Current State

Vantage has progressed substantially beyond its original RSS-aggregator prototype.

The application now has a functioning end-to-end knowledge-building architecture:

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

Current capabilities include:

* Multi-source editorial RSS ingestion
* Configurable source registry
* Persistent evidence storage
* Full-article retrieval
* Funding-round extraction
* Fund-close extraction
* Company entities
* Investor entities
* Fund entities
* Funding-round entities
* Fund-close entities
* Entity aliases
* Stable entity identity
* Conservative entity resolution
* Human review of uncertain resolutions
* Canonical funding-round matching
* Multi-source funding-round evidence
* Historical funding-round reconciliation
* Sector taxonomy normalization
* Funding-stage taxonomy normalization
* Company profiles
* Investor profiles
* Structured funding views
* Data-quality monitoring
* Market-intelligence dashboard
* Unified intelligence pipeline
* Flask management CLI
* Database migrations
* Automated regression tests

Vantage is therefore no longer simply a news application.

It is an early **venture intelligence system**.

---

# Current Implementation Reality

The target architecture has intentionally moved ahead of parts of the implementation.

That distinction should remain explicit.

Today, the source registry already describes sources using fields conceptually similar to:

```text
name
type
region
method
url
enabled
```

However, the current acquisition implementation remains primarily RSS-centric.

The practical architecture today is closer to:

```text
config.py
    ↓
SOURCES
    ↓
news_service.py
    ↓
feedparser
    ↓
RSS normalization
    ↓
title relevance filtering
    ↓
headline categorization
    ↓
Article
    ↓
Existing intelligence pipeline
```

The next architectural step is therefore not a rewrite.

It is to replace the RSS-specific discovery boundary with a small generic discovery boundary while preserving the downstream pipeline.

The application should remain recognizably the same system.

---

# 1. Source Discovery & Ingestion

The ingestion layer provides the evidence foundation for the entire application.

Vantage began with RSS-based editorial news ingestion.

That remains useful, but the source model is evolving from a:

> **news-feed architecture**

toward a:

> **venture-source discovery architecture**

Current capabilities include:

* Multiple configurable editorial sources
* RSS parsing with `feedparser`
* URL-based deduplication
* Basic evidence normalization
* HTML cleaning with BeautifulSoup
* VC relevance filtering
* Headline categorization
* Persistent storage
* Source-health monitoring

Current article categories include:

* Funding Round
* Fund News
* M&A
* IPO
* Other

The objective is not simply to collect more headlines.

The source network should optimize for:

* Coverage
* Relevance
* Reliability
* Evidence diversity
* Classification quality
* Source provenance
* Signal quality
* Maintainability

---

## Current Source Universe

The existing source network is primarily composed of venture and technology publications accessed through RSS.

This provides useful broad discovery, but it introduces an important limitation:

> **Editorial coverage is not the same thing as market coverage.**

Media coverage is influenced by:

* Geography
* Company visibility
* PR activity
* Publication focus
* Funding-round size
* Editorial selection
* Syndication patterns

Vantage should therefore distinguish:

> **Observed activity**

from:

> **Total market activity**

until source coverage is broad and representative enough to support stronger claims.

---

# 2. Source Network V2

The next source architecture should combine multiple evidence classes.

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
Registries
Regulatory sources
where a specific use case justifies them
```

Different source types provide different forms of evidence.

```text
Publication
    ↓
Independent discovery / reporting

Investor
    ↓
Investment confirmation / strategy / thesis

Company
    ↓
First-party financing / operating announcement

Ecosystem
    ↓
Early or specialist market signal

Structured source
    ↓
Validation / enrichment
```

Over time, multiple sources should converge on the same canonical event.

```text
                    EVENT
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
    Publication   Investor Post   Company PR
```

The objective is:

```text
3 evidence documents
        ↓
1 real-world event
```

rather than:

```text
3 documents
        ↓
3 duplicated events
```

---

# 3. Source Discovery Architecture

Vantage should avoid creating a bespoke scraper or service for every external website.

The target discovery architecture is:

```text
                         SOURCE REGISTRY
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
               RSS         Sitemap       HTML Index
                 │             │             │
                 └─────────────┼─────────────┘
                               ▼
                    NORMALIZED EVIDENCE
                               │
                               ▼
                    EXISTING VANTAGE PIPELINE
```

A source should primarily describe **how content can be discovered** rather than requiring its own Python implementation.

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
│
├── acquisition_method
│      ├── rss
│      ├── sitemap
│      ├── html
│      └── api
│
├── region
├── discovery URL / configuration
└── enabled
```

The first reusable adapters should remain deliberately small:

* RSS
* Sitemap
* Generic HTML listing

Do not attempt to anticipate every possible website architecture.

Adapters should be added only when they generalize across multiple useful sources.

---

## Normalized Evidence Contract

Every discovery adapter should produce the same logical evidence shape.

Conceptually:

```text
title
url
published_at
summary
source
source_type
discovery_method
```

A normalized evidence object should behave approximately like:

```python
{
    "title": str,
    "url": str,
    "published_at": datetime | None,
    "summary": str | None,
    "source": str,
    "source_type": str,
    "discovery_method": str,
}
```

Important principles:

### 1. Normalize dates inside the discovery adapter

RSS feeds, sitemaps, and HTML pages express dates differently.

Examples include:

```text
RSS:
RFC-style publication dates

Sitemap:
ISO-8601 <lastmod>

HTML:
<time datetime="...">

HTML:
human-readable text

Some pages:
no usable date
```

Each adapter should therefore return either:

```text
datetime
```

or:

```text
None
```

The downstream pipeline should not need to understand RSS-specific date formats.

### 2. Missing dates should not automatically discard useful evidence

An undated investor announcement may still be valuable evidence.

Missing dates should reduce confidence or affect sorting where appropriate, but should not necessarily remove the document from the observable universe.

### 3. Preserve provenance

Evidence should retain enough information to distinguish:

```text
TechCrunch publication article
```

from:

```text
Accel investor announcement
```

from:

```text
Company newsroom post
```

This will matter increasingly for confidence, coverage, and product intelligence.

---

# 4. Evidence Provenance

The long-term product depends on inspectable intelligence.

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

The current `Article` model increasingly represents an **evidence document**, even though the class remains named `Article`.

For Source Network V2, provenance should eventually include at least:

```text
source
source_type
discovery_method
```

For example:

```text
source = Accel
source_type = investor
discovery_method = sitemap
```

This makes future questions possible:

```text
How many funding events have first-party investor confirmation?

Which tracked investors are being directly observed?

What proportion of evidence comes from editorial reporting?

Which sources are generating high-value events?

Which sources repeatedly fail?
```

A dedicated database-backed `Source` entity may eventually become useful.

It is **not required immediately**.

For the current stage:

```text
config.py
      ↓
source registry

Article
      ↓
persisted provenance
```

is sufficient.

---

# 5. Source-Aware Relevance & Classification

The current relevance model was designed for editorial news.

That assumption should not be carried unchanged into investor first-party ingestion.

Publication headlines commonly look like:

```text
Acme raises $40M Series B led by Index Ventures
```

Deterministic keyword filtering works reasonably well for this type of source.

Investor first-party content may instead use language such as:

```text
Why we're investing in Acme

Partnering with Acme

Welcome Acme

Building the future of robotics with Acme

Our investment in Acme

Introducing Fund VII

Our conviction in AI infrastructure
```

A title-only editorial filter can therefore create dangerous false negatives.

The filtering strategy should become **source-aware**.

---

## Publication Sources

Editorial publications operate across a large content universe.

Relatively aggressive deterministic relevance filtering remains useful.

```text
Large publication feed
        ↓
VC relevance filtering
        ↓
Potential evidence
```

---

## Investor Sources

Investor websites already have a high prior probability of venture relevance.

Filtering should therefore favour recall.

```text
Investor website
        ↓
Broad evidence capture
        ↓
Classification
        ↓
Structured extraction where appropriate
```

Initially, it is better to retain some low-value investor content than to silently discard important investment announcements.

The LLM extraction layer should remain conservative and decide whether a document genuinely describes:

* Company financing
* Fund formation
* Another event
* No structured event

---

# 6. Full-Content Processing

Titles and summaries are often insufficient for reliable structured extraction.

Vantage therefore retrieves and persists underlying source content.

The existing article-content service:

* Makes direct HTTP requests
* Uses realistic request headers
* Validates HTML responses
* Removes obvious non-content elements
* Prefers semantic article containers
* Extracts substantive paragraphs
* Removes duplicate and low-value fragments
* Falls back to broader page extraction
* Rejects insufficient content

Conceptually:

```text
Discovered URL
   ↓
HTML retrieval
   ↓
Content extraction
   ↓
Clean source text
   ↓
Persistent Article.content
```

The current generic extractor should remain the default.

Investor websites will expose new failures.

Those failures should be used to improve the generic extractor where possible.

Vantage should avoid an architecture such as:

```text
accel_scraper.py
sequoia_scraper.py
index_scraper.py
a16z_scraper.py
...
```

unless a genuinely high-value source cannot be supported through reusable methods and its value clearly justifies an exception.

---

# 7. AI-Assisted Event Extraction

Vantage uses the OpenAI API with validated structured outputs to transform unstructured evidence into machine-readable venture events.

The governing principle is:

> **Extract only information supported by the source. Do not guess missing facts.**

LLMs are used where semantic understanding is useful.

Deterministic code remains responsible for:

* Persistence
* Constraints
* State management
* Exact matching
* Canonical identity
* Idempotency
* Event reconciliation
* Aggregation
* Business rules

---

## Company Funding Rounds

For company financing events, Vantage can currently extract:

* Whether the evidence represents a genuine funding round
* Event evidence
* Company
* Funding amount
* Currency
* Round type
* Participating investors
* Lead investors
* Sector
* Company city
* Company country
* Founding year

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
Supporting evidence
```

---

## VC Fund Closes

Vantage distinguishes VC fund formation from operating-company financing.

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

* Whether the evidence represents a fund close
* Supporting event evidence
* Investor / VC firm
* Fund name
* Fund size
* Currency
* Close type
* Investment strategy
* Geography
* Vintage year where supported

This distinction prevents fund managers raising investment vehicles from being represented as startups raising company financing.

---

# 8. Structured Knowledge Base

The core value of Vantage increasingly resides in the structured knowledge base rather than the article feed.

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

The `Article` model increasingly represents an evidence document.

Evidence may originate from:

* Independent publications
* Investor investment announcements
* VC essays
* Portfolio updates
* Accelerator announcements
* Company newsrooms
* Other selected public sources

This allows downstream knowledge-building logic to remain largely source-agnostic.

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
                └──── Evidence ┘
```

---

## Company History

A company can accumulate:

* Financing events
* Investors
* Lead investors
* Sector metadata
* Geographic metadata
* Founding metadata
* Supporting source evidence
* Historical relationships

---

## Investor History

An investor can accumulate:

* Portfolio activity
* Lead investments
* Follow-on investments
* Funds
* Fund-close activity
* Co-investor relationships
* Stage exposure
* Sector exposure
* Geographic exposure
* First-party investment announcements
* Strategic and thesis signals

This forms the foundation of the Vantage ecosystem map.

---

# 9. Entity Resolution

Reliable intelligence requires reliable entity identity.

Real-world organizations frequently appear under different names.

For example:

```text
Andreessen Horowitz
a16z
Andreessen Horowitz (a16z)
```

should represent one investor.

Vantage has a dedicated entity-resolution layer.

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

Aliases use stable database-backed entity identity rather than relying only on mutable names.

Entity matching is intentionally conservative.

Generic venture-industry terms such as:

```text
Capital
Ventures
Partners
Fund
```

must not produce false similarity matches between unrelated organizations.

Poor entity resolution would corrupt:

* Investor activity metrics
* Portfolio histories
* Co-investment relationships
* Funding histories
* Sector analysis
* Geographic analysis
* Market intelligence

Vantage should prefer unresolved ambiguity over confidently wrong identity.

---

# 10. Event Resolution & Multi-Source Evidence

Multiple documents frequently describe the same real-world event.

Example:

```text
Tech publication:
Acme raises $40M Series B

Investor:
Why we invested in Acme

Company:
Acme closes Series B led by Sequoia
```

should become:

```text
3 evidence documents
        ↓
1 canonical funding event
        ↓
Acme
$40M
Series B
Sequoia
```

rather than:

```text
3 documents
        ↓
3 funding rounds
```

---

## Funding-Round Resolution

Funding rounds now support:

* Canonical funding-event matching
* Multi-source evidence
* Historical duplicate auditing
* Historical reconciliation
* Safe canonical event selection
* Preservation of evidence across merges
* Canonical stage taxonomy
* Stable company identity

This represents a major part of Architecture / Data Integrity Hardening v1.

---

## Known Gap: Fund-Close Resolution

Fund-close events do not yet have equivalent multi-source canonicalization.

The current implementation is still largely article-centric.

Conceptually, this means:

```text
Editorial article:
"Firm closes $500M Fund III"

Investor announcement:
"Introducing Fund III"

        ↓

Potential duplicate FundClose records
```

The desired architecture is:

```text
2 evidence documents
        ↓
1 canonical FundClose
        ↓
Firm
Fund III
$500M
```

This gap becomes materially more important once Source Network V2 begins ingesting investor first-party fund announcements.

Fund-close event integrity should therefore be hardened before aggressive investor-source expansion.

---

# 11. Architecture & Data Integrity Hardening

## Hardening v1 — Complete

Vantage completed an initial architecture and data-integrity hardening phase before aggressively expanding the source universe.

Delivered:

* Unified intelligence-pipeline orchestration
* Explicit transaction ownership across the main funding path
* Idempotent intelligence processing
* Canonical funding-round matching
* Multi-source funding-round evidence
* Historical funding-round reconciliation
* Sector taxonomy normalization
* Funding-stage taxonomy normalization
* Stable entity identity
* Scoped entity aliases
* Foreign-key-backed alias resolution
* Human review backed by stable entity references
* Expanded automated regression coverage

The governing principle was:

> **Scaling a weak data model creates larger data-quality problems.**

The objective was to establish a trustworthy knowledge-building foundation before increasing coverage.

---

## Hardening v1.1 — Immediate

Before investor first-party ingestion scales materially, the remaining fund-event integrity gap should be closed.

Target:

```text
FundClose event resolution
        +
multi-source evidence
        +
caller-owned transaction handling
```

The desired behaviour is:

```text
Investor fund announcement
        +
Editorial fund announcement
        ↓
Canonical FundClose
        ↓
Multiple supporting evidence documents
```

This should be a narrow hardening step, not a broader redesign.

---

# 12. Human Review & Data Quality

Vantage does not automatically force uncertain entity matches.

Potential resolutions can instead be persisted as review records.

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

The Data Quality surface provides visibility into knowledge-base integrity.

Current monitoring includes:

* Company count
* Investor count
* Funding-round count
* Canonical aliases
* Missing company metadata
* Missing funding-event metadata
* Potential duplicate entities
* Entity-resolution reviews
* Canonicalization state

The broader principle remains:

> **A smaller trustworthy dataset is preferable to a larger misleading dataset.**

---

# 13. Taxonomy & Analytical Consistency

Source-derived descriptions preserve fidelity, but aggregated intelligence requires consistent categories.

Vantage therefore preserves raw values while introducing canonical analytical taxonomies.

Examples:

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

Example sector normalization:

```text
Healthtech
Health technology
Digital health
        ↓
Health Tech
```

Example stage normalization:

```text
pre-seed
Pre Seed
pre-Seed
        ↓
Pre-Seed
```

The objective is not to build an enormous ontology.

It is to make aggregated intelligence trustworthy.

Potential future taxonomy areas include:

* Geography
* Investor type
* Fund strategy
* Investment theme
* Evidence type

---

# 14. Product Interface

The original article feed has evolved into a shared Vantage product interface.

Current product surfaces include:

---

## News

Searchable and filterable venture-news monitoring.

This remains useful as an evidence-discovery interface, but it is no longer the final product.

---

## Funding

Structured company financing activity including:

* Company
* Amount
* Currency
* Round type
* Investors
* Lead investors
* Evidence
* Supporting source documents

---

## Company Profiles

Company pages can expose:

* Sector
* Geography
* Founding year
* Funding history
* Investors
* Lead investors
* Supporting event evidence

Future extensions can include:

* Funding velocity
* Capital raised
* Event timelines
* Investor changes
* Historical activity

---

## Investor Profiles

Investor pages can increasingly expose:

* Recorded investment activity
* Portfolio companies
* Financing events
* Lead-investor activity
* Fund activity
* Stage exposure
* Sector exposure
* Geographic exposure
* Frequent co-investors
* Activity over time
* First-party announcements
* Strategic themes

---

## Sources

Monitoring of:

* Configured sources
* Enabled sources
* Source health
* Discovery success
* Source failures

Source Network V2 should progressively evolve this into a true coverage and source-performance surface.

---

## Data Quality

Monitoring and review of:

* Canonicalization
* Completeness
* Potential duplicates
* Entity-resolution reviews
* Knowledge-base quality

---

## Intelligence

The first analytical layer derived directly from the structured knowledge base.

Current intelligence surfaces include:

* Knowledge-base counts
* Most active investors
* Lead-investor activity
* Financing activity by sector
* Recent VC fund closes
* Recent company financing events

The Intelligence page should remain evidence-driven.

Vantage should not display misleading aggregate market totals where source coverage cannot support them.

---

# 15. Investor Intelligence

Investor intelligence is strategically important because leading VC firms produce multiple classes of observable signal.

---

## Investment Activity

```text
Investor
   ↓
Investment
   ↓
Company
```

Signals include:

* New investments
* Lead investments
* Co-lead investments
* Follow-on investments
* Stage exposure
* Sector exposure
* Geographic exposure
* Co-investor relationships

---

## Capital Formation

```text
Investor
   ↓
Fund
   ↓
Fund Close
```

Signals include:

* New funds
* Fund size
* Strategy
* Geography
* Vintage
* Changes in fund size
* Capital formation over time

---

## Thesis Activity

```text
Investor
   ↓
Public writing
   ↓
Themes / sectors / technologies
```

Potential future signals include:

* Repeated discussion of a technology
* New sector theses
* New specialist partners
* Changes in strategic language
* Increasing attention to particular markets
* Alignment between published thesis and investments

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

The first objective is to reliably build the underlying evidence and historical record.

---

# From Investor Profiles to Investor Intelligence

A conventional profile might answer:

```text
Accel

Founded: ...
Headquarters: ...
Investments: ...
Funds: ...
Portfolio: ...
```

A mature Vantage investor profile could answer:

```text
ACCEL

OBSERVED ACTIVITY
────────────────────────

Recent investments
Lead investments
Follow-on investments

STAGE EXPOSURE
────────────────────────
Seed
Series A
Series B
Growth

SECTOR EXPOSURE
────────────────────────
AI
Fintech
Defence
Climate
etc.

GEOGRAPHIC EXPOSURE
────────────────────────
US
UK
Germany
France
etc.

RELATIONSHIPS
────────────────────────
Frequent co-investors

CAPITAL FORMATION
────────────────────────
Recent funds
Fund sizes
Fund strategy

FIRST-PARTY ACTIVITY
────────────────────────
Investment announcements
Thesis publications

CHANGE OVER TIME
────────────────────────
Sector exposure ↑ / ↓
Stage exposure ↑ / ↓
Geographic activity ↑ / ↓
Lead activity ↑ / ↓

EVIDENCE
────────────────────────
Underlying events
Supporting source documents
```

Eventually Vantage could answer questions such as:

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

This is where Vantage begins to become more than a database.

---

# From Records to Signals

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

Example:

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

A future Vantage surface might identify:

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

The important principle is that signals should remain traceable to underlying evidence.

---

# Evidence-Backed Intelligence

Evidence provenance is a potential product differentiator.

A user should increasingly be able to move from:

```text
"European defence investment appears to be accelerating."
```

to:

```text
Why?
```

and inspect:

* Which investors changed behaviour
* Which financing events contributed
* Which companies were involved
* Which time periods changed
* Which sources support the events
* Whether evidence is editorial or first-party

The objective is not merely to generate conclusions.

It is to build:

> **Inspectable intelligence**

---

# Current Architecture

The conceptual architectural core is:

```text
                     PUBLIC ECOSYSTEM
                           │
                           ▼
                      SOURCE REGISTRY
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
       Publications     Investors      Ecosystem
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                    SOURCE DISCOVERY
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
            RSS         Sitemap        HTML
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                  NORMALIZED EVIDENCE
                           │
                           ▼
                    DEDUPLICATION
                           │
                           ▼
                SOURCE-AWARE RELEVANCE
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
           └────── Events & Relationships ─┘
                           │
                           ▼
                     DATA QUALITY
                           │
                           ▼
               HISTORICAL ACTIVITY
                           │
                           ▼
               PROFILES / INTELLIGENCE
```

This architecture should remain technically lightweight.

---

# Current Technology

Vantage deliberately remains simple.

Current core technologies include:

* Python
* Flask
* Jinja
* SQLAlchemy
* SQLite
* Flask-Migrate / Alembic
* `feedparser`
* BeautifulSoup
* `requests`
* OpenAI API
* Pydantic
* `pytest`
* HTML / CSS

The application currently runs locally.

The main application interface remains Flask/Jinja.

The knowledge-building pipeline currently runs through the Flask CLI.

This simplicity is intentional.

Infrastructure should become more sophisticated only when real operating requirements justify it.

---

# Development Philosophy

## 1. Information acquisition → structure → intelligence

Every major capability should strengthen this progression.

---

## 2. News is evidence, not the final product

Articles and other public documents are source material from which structured ecosystem knowledge is created.

---

## 3. Reliability precedes sophisticated analytics

A sophisticated dashboard built on fragmented entities, duplicated events, or weak source coverage produces misleading intelligence.

---

## 4. Prefer useful capabilities over premature infrastructure

Technical sophistication should solve real constraints.

---

## 5. Use LLMs where semantic understanding matters

LLMs are valuable for interpreting messy natural-language evidence.

Deterministic code remains preferable for:

* Database constraints
* Known aliases
* Exact matching
* State management
* Aggregation
* Business rules
* Idempotency
* Transaction ownership
* Event reconciliation

---

## 6. Keep human review for genuinely ambiguous cases

Not every uncertain entity or event should be automatically resolved.

---

## 7. Prefer configuration over bespoke source code

A new source should usually require configuration rather than a dedicated Python service.

---

## 8. Add discovery adapters only when they generalize

A new acquisition mechanism should normally support multiple useful sources.

---

## 9. Preserve provenance

First-party evidence and independent editorial evidence have different informational characteristics.

Both are useful.

They should remain distinguishable.

---

## 10. Measure the observed universe

Vantage should distinguish:

> **Observed activity**

from:

> **Total market activity**

until source coverage supports stronger conclusions.

---

## 11. Prefer high recall during first-party discovery

For a curated investor source, missing an important announcement may be more damaging than retaining some irrelevant content.

Classification can happen downstream.

---

## 12. Let real corpus growth expose the next problems

Do not solve hypothetical scale problems before the dataset demonstrates them.

---

## 13. Build progressively

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

* Multi-source RSS ingestion
* Article normalization
* URL deduplication
* Relevance filtering
* Categorization
* Persistent storage
* Search and filtering
* Source-health monitoring
* Full-article retrieval
* Automated tests

---

# Phase 2 — Structured Knowledge Layer

**Status: substantially achieved**

Delivered:

* Company model
* Investor model
* Funding-round model
* Fund model
* Fund-close model
* Company ↔ funding relationships
* Investor ↔ funding relationships
* Lead-investor relationships
* Investor ↔ fund relationships
* LLM structured extraction
* Event evidence
* Company metadata enrichment
* Entity normalization
* Entity aliases
* Entity resolution
* Human resolution review
* Data-quality monitoring

---

# Phase 3 — Pipeline, Event & Entity Integrity

**Status: v1 complete**

Delivered:

* Unified `vantage ingest` lifecycle
* Safe failure handling
* Idempotent intelligence processing
* Processing counters and operational reporting
* Canonical funding-round matching
* Multi-source funding-round evidence
* Historical funding-round reconciliation
* Stable entity identity
* Foreign-key-backed aliases
* Stable human-review references
* Sector taxonomy normalization
* Funding-stage taxonomy normalization
* Expanded regression testing

This established the first reliable Vantage knowledge-building engine.

---

# Phase 3.1 — Fund Event Integrity Hardening

**Status: immediate next engineering checkpoint**

Objective:

Bring fund-close event handling to the same architectural standard as funding rounds before investor first-party sources materially increase fund-announcement volume.

Target capabilities:

* Canonical FundClose matching
* Multi-source FundClose evidence
* Preservation of supporting articles
* Safe enrichment across repeated evidence
* Caller-owned transaction handling
* Idempotent fund-close processing
* Regression tests

Target behaviour:

```text
Editorial fund announcement
        +
Investor first-party announcement
        ↓
One canonical FundClose
        ↓
Multiple supporting evidence documents
```

This should remain a narrow hardening phase.

---

# Phase 4 — Source Network V2

**Status: current major development focus**

The next major constraint is no longer basic data structure.

It is:

> **Coverage**

The existing dataset is derived primarily from editorial RSS sources.

The next objective is to broaden the observable venture universe without creating a collection of bespoke scrapers.

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

Initial technical objectives:

* Generic discovery dispatcher
* RSS adapter
* Sitemap adapter
* Generic HTML-listing adapter
* Source-agnostic normalized evidence
* Normalized datetimes
* Support for undated evidence
* Persisted source provenance
* Source-aware relevance rules
* Existing RSS behaviour preserved

The first success criterion is:

> **Existing editorial RSS ingestion continues to work materially as before through the new abstraction.**

Only then should investor sources be enabled.

---

# Phase 4.1 — Investor Source Network Pilot

**Status: follows discovery abstraction**

Do not begin with 100 firms.

Start with approximately **6–10 structurally diverse investor websites**.

The pilot should deliberately include different acquisition patterns:

```text
Investor A → RSS
Investor B → sitemap
Investor C → simple HTML newsroom
Investor D → investment posts
Investor E → essays + investments mixed
Investor F → fund announcements
Investor G → pagination or unusual structure
Investor H → international / different site conventions
```

The purpose of the pilot is architectural.

The key question is:

> **Can a small set of reusable adapters support materially different VC websites primarily through configuration?**

A successful pilot might look like:

```text
8 diverse VC websites
        ↓
7 supported generically
        ↓
1 exposes a genuine architectural limitation
```

That is more valuable than prematurely claiming support for dozens of firms.

---

# Phase 4.2 — Source Measurement

Basic source measurement should begin during the pilot rather than waiting for a large corpus.

Potential per-source metrics:

```text
Documents discovered
Documents retained
New documents
Content retrieval success
Content retrieval failures
Funding events extracted
Fund closes extracted
Processing failures
```

Example:

```text
ACCEL

Documents discovered       42
Documents retained         31
New documents               8
Content retrieved           7
Content failures            1
Funding events              3
Fund closes                 1
```

Network-level metrics can include:

```text
Configured sources
Enabled sources
Healthy sources
Failed sources

Publications
Investors
Ecosystem sources
Companies
```

This creates a feedback loop for deciding which sources actually improve Vantage.

---

# Phase 4.3 — First-Party Integrity Stress Test

Investor evidence will expose edge cases that editorial-heavy ingestion may not.

Examples include:

```text
Investor post names company
but omits financing amount
```

or:

```text
Investor post confirms investment
but omits round stage
```

or:

```text
Investor announcement appears
several days after editorial reporting
```

The current funding-event matcher is intentionally conservative.

Do not pre-emptively weaken it.

Instead:

1. Run the investor pilot.
2. Collect real failure cases.
3. Measure how often first-party evidence fails to converge on existing canonical events.
4. Introduce conservative fallback matching only when justified by real examples.

Possible future fallback signals might include:

```text
same canonical company
+
compatible date
+
compatible stage
+
investor relationship
+
exactly one plausible canonical event
```

Any such rule should prioritize precision over convenience.

---

# Phase 5 — Corpus Expansion & Coverage Intelligence

**Status: follows successful Source Network V2 pilot**

Once the acquisition architecture has been proven:

```text
8 investor sources
      ↓
20
      ↓
50
      ↓
100+
```

Potential expansion categories:

* Global multi-stage VC
* US venture
* European venture
* Seed investors
* Growth investors
* AI specialists
* Fintech specialists
* Climate investors
* Deep-tech investors
* Defence investors
* Important regional firms

Then selectively add:

* Accelerators
* Demo-day sources
* Specialist ecosystems
* Founder communities
* Sector-specific venture publications

Company first-party monitoring should remain selective.

Candidates could include:

* Watchlisted companies
* Companies backed by tracked investors
* High-momentum companies
* Companies already prominent in the Vantage graph

Scale should expose remaining weaknesses in:

* Entity resolution
* Event resolution
* Fund resolution
* Content extraction
* Classification
* Taxonomy
* Source reliability
* Geographic coverage
* Source-type coverage

Those problems should then be fixed because the corpus demonstrates them.

---

# Coverage Intelligence

Coverage should become measurable.

Potential metrics include:

```text
Tracked publication sources
Tracked investor sources
Tracked ecosystem sources
Tracked company sources

Evidence by source type

Funding events by source type

Fund closes by source type

Events with:
1 supporting source
2 supporting sources
3+ supporting sources

Editorial-only events
Investor-confirmed events
Company-confirmed events
Multi-source events

Geographic source coverage
Sector source coverage
Investor-source coverage
```

These metrics should help Vantage answer:

```text
What can we observe well?

Where is coverage weak?

Which investors are directly monitored?

Which geographies are underrepresented?

How much confidence should we place
in a particular aggregate pattern?
```

---

# Phase 6 — Product Intelligence V2

**Status: foundation exists; deepen after corpus expansion**

Once coverage and historical volume are materially broader, deepen the intelligence layer.

---

## Investor Intelligence

Investor profiles should increasingly answer:

* How active is this investor?
* Which companies has it backed?
* How often does it lead?
* Which sectors does it target?
* Which stages does it target?
* Which geographies does it cover?
* Which investors does it frequently co-invest with?
* Which funds has it raised?
* How is its activity changing?
* What themes is it increasingly discussing?
* Where do public thesis and investment behaviour overlap?

---

## Company Intelligence

Potential capabilities:

* Financing history
* Funding velocity
* Investor history
* Lead investors
* Sector
* Geography
* Event timeline
* Capital raised from disclosed rounds
* Evidence history

---

## Fund Intelligence

Potential capabilities:

* Fund history by investor
* Fund sizes
* Fund strategies
* Geography
* Vintage
* Capital formation over time
* Changes in fund size
* Changes in stated strategy

---

## Market Intelligence

Potential analysis:

* Investor activity
* Lead-investor activity
* Sector activity
* Stage activity
* Geographic activity
* Fund formation
* Co-investment relationships
* Ecosystem concentration
* Emerging themes

---

# Phase 7 — Time-Series & Signal Intelligence

A mature intelligence platform should understand change, not merely state.

```text
Current activity
        +
Historical activity
        +
Change over time
        =
Market signal
```

Potential signals include:

* Trending sectors
* Emerging investors
* Investor strategy changes
* Funding acceleration
* Stage shifts
* Geographic momentum
* Fundraising cycles
* Co-investment changes
* Increasing investor conviction

Vantage should initially expose transparent period-over-period metrics before creating opaque composite scores.

---

# Phase 8 — Search & Ecosystem Discovery

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

Investors leading European AI infrastructure rounds

Investors whose thesis activity and portfolio activity
are converging around the same sector
```

Potential product navigation:

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

Search sophistication should grow with the quality and breadth of the underlying knowledge base.

---

# Phase 9 — Productionization

**Status: intentionally deferred**

The current stack is sufficient for the present stage.

A future transition may evolve from:

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

Potential future capabilities include:

* PostgreSQL
* Scheduled ingestion
* Background workers
* Production WSGI server
* Docker
* Cloud deployment
* CI/CD
* Secret management
* Logging
* Monitoring
* Automated backups

These should be introduced when real operating constraints justify them.

The first component Vantage is likely to outgrow is SQLite or manual pipeline execution—not Flask itself.

---

# Near-Term Execution Plan

From the current checkpoint:

```text
CURRENT CHECKPOINT

Trustworthy funding/entity
knowledge-building engine
        │
        ▼
1. FUND EVENT HARDENING v1.1

Canonical FundClose resolution
Multi-source evidence
Transaction cleanup
        │
        ▼
2. SOURCE DISCOVERY V2

Generic dispatcher
RSS + sitemap + HTML
        │
        ▼
3. NORMALIZED EVIDENCE CONTRACT

datetime | None
source_type
discovery_method
provenance
        │
        ▼
4. SOURCE-AWARE INGESTION

Publication filtering
≠
Investor filtering
        │
        ▼
5. INVESTOR NETWORK PILOT

6–10 structurally diverse VC firms
        │
        ▼
6. SOURCE MEASUREMENT

Yield
Failures
Content success
Event production
        │
        ▼
7. INTEGRITY STRESS TEST

Incomplete first-party evidence
Event convergence
Fund naming
Entity resolution
        │
        ▼
8. SOURCE EXPANSION

10 → 25 → 50 → 100+
        │
        ▼
9. CORPUS & COVERAGE

Hundreds → thousands
of canonical observations
        │
        ▼
10. INVESTOR INTELLIGENCE V2

Behaviour
Change
Signals
Evidence
        │
        ▼
11. TIME-SERIES SIGNALS

Momentum
Behavioural change
        │
        ▼
12. SEARCH & DISCOVERY

Structured ecosystem exploration
        │
        ▼
13. PRODUCTIONIZATION

Only when continuous operation
and scale justify it
```

---

# Immediate Development Priority

The immediate engineering objective is:

> **Expand Vantage from an RSS-centric news ingestion system into a generic multi-source venture discovery engine without materially increasing architectural complexity—but first close the remaining FundClose multi-source integrity gap.**

The downstream intelligence architecture already largely exists.

The next major challenge is upstream coverage.

The sequence should therefore be:

```text
FundClose integrity
        ↓
Source Registry
        ↓
Reusable Discovery Adapters
        ↓
Normalized Evidence
        ↓
Source-Aware Relevance
        ↓
Existing Intelligence Pipeline
        ↓
Investor Pilot
```

The Source Network V2 implementation should remain deliberately narrow:

```text
RSS
Sitemap
Generic HTML listing
```

The objective is not to create a universal web crawler.

It is to prove that a small number of reusable acquisition methods can support a materially broader venture-information universe.

A new VC firm should usually require:

> **configuration**

rather than:

> **a new Python service**

---

# Source Network V2 Acceptance Criteria

The first implementation should be considered successful when:

1. Existing RSS sources continue working materially as before.
2. RSS acquisition is accessed through the generic discovery boundary.
3. At least one sitemap-based source works.
4. At least one HTML-listing source works.
5. All adapters emit the same normalized evidence shape.
6. Dates are normalized before downstream processing.
7. Undated useful evidence is not automatically discarded.
8. Source type and acquisition method remain available after persistence.
9. Investor sources can use broader relevance rules than publications.
10. Source failures do not prevent the rest of the network from processing.
11. Discovery remains configuration-driven.
12. Automated tests protect existing RSS behaviour.
13. No unnecessary infrastructure is introduced.

---

# Investor Pilot Acceptance Criteria

The investor pilot should answer an architectural question rather than merely increase a source count.

A successful pilot should demonstrate that:

* 6–10 structurally diverse investor sites can be ingested
* Most sources require configuration rather than bespoke code
* RSS, sitemap, and HTML discovery all work in practice
* First-party investment announcements reach the intelligence pipeline
* Fund announcements reach the intelligence pipeline
* Content extraction succeeds at an acceptable rate
* Source-level yield can be measured
* Existing entity and event integrity largely survives broader evidence
* New failure modes are observable and diagnosable
* No large scraper-maintenance burden has been created

---

# What We Are Deliberately Not Prioritizing Yet

Vantage should continue avoiding premature complexity.

Not current priorities:

* Kubernetes
* Microservices
* Complex distributed architecture
* Vector databases without a concrete requirement
* Embeddings simply because they are available
* Generic autonomous agents
* Authentication before user-specific workflows justify it
* Mobile applications
* Elaborate visualizations on small datasets
* Large numbers of low-quality sources
* Universal company-site crawling
* Generic regulatory-document processing
* Recommendation engines
* Premature cloud infrastructure
* Replacing Flask/Jinja without a genuine product constraint
* Rebuilding the frontend in a JavaScript framework
* Building a universal crawler
* Creating bespoke scrapers for every VC firm
* Adding infrastructure simply because mature companies commonly use it
* Creating opaque AI-generated market scores before the underlying evidence is trustworthy

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
"Show me what important investors,
companies and ecosystems are actually doing."
```

The longer-term ambition is:

```text
"Tell me what is changing across the venture ecosystem,
who is driving that change,
and where meaningful signals are emerging."
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

The objective is to continuously convert a broad public evidence universe into structured historical knowledge and use that history to understand:

> **behaviour and change**

The central strategic question is:

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
