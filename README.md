# Project Vantage

**Project Vantage** is a Python/Flask venture intelligence application that continuously observes public venture-market activity, converts it into structured historical knowledge, and uses that history to understand how investors, companies, sectors, stages, and markets are changing over time.

Vantage began as a simple VC news aggregator.

It is evolving into a lightweight **venture intelligence system**.

```text
Public venture ecosystem
        ↓
Source discovery
        ↓
Evidence documents
        ↓
Structured events
        ↓
Canonical entities
        ↓
Relationships
        ↓
Historical activity
        ↓
Behavioural analysis
        ↓
Market intelligence
```

The core philosophy is:

> **Information acquisition → structure → intelligence**

From the user's perspective:

```text
What is happening?
        ↓
Who is doing what?
        ↓
How is that changing?
        ↓
What does it mean?
```

News is therefore not the product.

News, investor announcements, company posts, fund announcements, ecosystem publications, and other public information are **evidence** from which Vantage builds a structured model of the venture ecosystem.

---

# Product Thesis

The private-market data landscape already contains major platforms such as:

- PitchBook
- Dealroom
- Tracxn
- CB Insights
- Harmonic

Vantage should not attempt to compete primarily by becoming another static company database.

The more interesting thesis is:

> **Continuously observe what important participants in the venture ecosystem are actually doing, convert that activity into structured historical knowledge, and identify meaningful changes in behaviour over time.**

Conceptually:

```text
LIVE PUBLIC INFORMATION

Publications
Investor / VC websites
Investment announcements
Fund announcements
Company newsrooms
Accelerators
Ecosystem sources
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

The system increasingly begins from:

> **What are important venture-market participants doing?**

and ultimately aims to answer:

> **How is that behaviour changing, who is driving the change, and what might that tell us?**

---

# Strategic Wedge: Investor Behaviour

The initial intelligence wedge is:

> **What are important venture investors actually doing?**

Vantage should increasingly answer questions such as:

```text
What are they investing in?

What are they leading?

Which sectors are they entering?

Which stages are they targeting?

Where are they investing?

Who are they investing alongside?

What funds are they raising?

How is their activity changing?
```

Editorial publications remain important because they provide broad independent discovery.

Investor first-party sources add something different:

```text
Editorial source
    ↓
"What became news?"

Investor source
    ↓
"What did this investor choose to do?"
```

Together, these can produce a richer historical picture:

```text
Editorial evidence
        +
Investor first-party evidence
        +
Company / ecosystem evidence
        +
Historical structured events
        ↓
Venture intelligence
```

---

# Product Layers

Vantage has three connected layers.

## 1. Venture Observation

Understand:

> **What is happening?**

Responsibilities include:

- discovering public venture information
- normalizing evidence from different source types
- filtering obvious noise
- preserving provenance
- retrieving underlying content
- maintaining source health
- building historical coverage

The objective is not simply to ingest more URLs.

It is to build a broad and useful **observable venture universe**.

---

## 2. Venture Knowledge Base

Understand:

> **Who did what?**

Evidence is transformed into structured:

- Companies
- Investors
- Funds
- Funding rounds
- Fund closes
- Investor participation
- Lead-investor relationships
- Supporting evidence
- Canonical entity identities
- Historical activity

The knowledge base represents real-world entities and events rather than isolated articles.

Example:

```text
TechCrunch article
        +
Sequoia announcement
        +
Company press release
        ↓
1 canonical financing event
        ↓
Company
Investors
Amount
Stage
Date
Supporting evidence
```

---

## 3. Venture Intelligence

Understand:

> **How is activity changing, and what does it mean?**

The knowledge base can increasingly support:

- Investor activity
- Lead-investor behaviour
- Stage exposure
- Sector exposure
- Geographic exposure
- Co-investment relationships
- Fund formation
- Funding patterns
- Activity acceleration / deceleration
- Investor strategy changes
- Emerging sector activity
- Historical changes in behaviour

The long-term progression is:

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

---

# A Short History

Vantage has evolved through several distinct stages.

## Stage 1 — VC News Aggregator

The original application was a simple Python / Flask project that:

- ingested venture news through RSS
- stored articles
- displayed a searchable news feed

The primary object was the article.

---

## Stage 2 — Structured Venture Data

LLM extraction was introduced to transform articles into:

- Companies
- Investors
- Funding rounds
- Funds
- Fund closes

The project began shifting from:

```text
news application
```

toward:

```text
structured venture database
```

---

## Stage 3 — Knowledge Integrity

As more structured data accumulated, the main challenge became identity and event integrity.

Vantage added:

- Entity normalization
- Entity aliases
- Conservative entity resolution
- Human review for uncertain matches
- Canonical funding-event matching
- Canonical fund-close matching
- Multi-source event evidence
- Funding-stage normalization
- Sector normalization
- Historical reconciliation

This moved the architecture from:

```text
1 article
→
1 database record
```

toward:

```text
many evidence documents
→
1 real-world event
```

---

## Stage 4 — Multi-Source Observation

The project then expanded beyond editorial RSS.

Generic discovery support was introduced for:

- RSS
- XML sitemaps
- Generic HTML listings

Investor first-party sources such as Accel, Index Ventures, and Sequoia were used to validate that the same knowledge-building pipeline could ingest fundamentally different evidence types.

Historical backfill and source measurement were also introduced.

This demonstrated that the acquisition layer could become source-agnostic without requiring a bespoke scraper for every website.

---

## Current Stage — From Pipeline to Platform

The core knowledge-building engine now works.

The next constraint is no longer whether Vantage can process another source.

It is whether Vantage can operate **many sources as a network** and turn the resulting history into genuine behavioural intelligence.

The project is therefore moving from:

```text
individual source integrations
```

toward:

```text
source platform
        +
venture activity graph
        +
behavioural intelligence
```

---

# Current Architecture

The current architectural core is:

```text
                    PUBLIC ECOSYSTEM
                          │
                          ▼
                    SOURCE CONFIG
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
            RSS        Sitemap        HTML
             │            │            │
             └────────────┼────────────┘
                          ▼
                 NORMALIZED EVIDENCE
                          │
                          ▼
                    DEDUPLICATION
                          │
                          ▼
                 RELEVANCE ROUTING
                          │
                          ▼
                  CONTENT RETRIEVAL
                          │
                          ▼
                   CATEGORIZATION
                          │
                          ▼
                  LLM EXTRACTION
                          │
                          ▼
                  ENTITY RESOLUTION
                          │
                          ▼
                   EVENT RESOLUTION
                          │
                          ▼
                   KNOWLEDGE BASE
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         Companies     Investors      Funds
             │            │            │
             └──── Events & Relationships
                          │
                          ▼
                    DATA QUALITY
                          │
                          ▼
                  HISTORICAL ACTIVITY
                          │
                          ▼
                     INTELLIGENCE
```

The application deliberately remains technically lightweight.

---

# Normalized Evidence

The historical `Article` model increasingly represents a generic **evidence document**.

Evidence may originate from:

- Publications
- Investor websites
- Company websites
- Ecosystem sources
- Accelerators
- Selected structured or official sources

The normalized discovery contract is conceptually:

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

The downstream knowledge-building pipeline should not need to know whether an item came from RSS, a sitemap, or an HTML listing.

---

# Source Discovery

Vantage follows a configuration-first source strategy.

Target pattern:

```text
Source configuration
        ↓
Discovery adapter
        ↓
Normalized evidence
        ↓
Shared processing pipeline
```

Reusable discovery adapters currently include:

```text
RSS
Sitemap
HTML listing
```

A new source should usually require configuration rather than a dedicated Python scraper.

The project should avoid evolving into:

```text
accel_scraper.py
sequoia_scraper.py
index_scraper.py
sifted_scraper.py
techcrunch_scraper.py
...
```

A new acquisition mechanism should normally be added only when it generalizes across multiple useful sources.

---

# Evidence Provenance

Vantage preserves where information came from.

Examples:

```text
source = TechCrunch
source_type = publication
discovery_method = rss
```

```text
source = Sequoia Capital
source_type = investor
discovery_method = sitemap
```

This makes future questions possible:

```text
Which events have first-party confirmation?

Which tracked investors are directly observed?

Which events rely only on editorial evidence?

Which sources contribute genuinely unique events?

Which sources mostly corroborate events found elsewhere?
```

The principle is:

> **Intelligence should remain traceable to evidence.**

---

# Structured Knowledge Model

Core entities currently include:

```text
Article / Evidence

Company
Investor
FundingRound

Fund
FundClose

EntityAlias
EntityResolutionReview
```

Core relationships increasingly resemble:

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
                   └── Evidence ──┘
```

---

# Entity Resolution

Real-world organizations often appear under multiple names.

Example:

```text
Andreessen Horowitz
a16z
Andreessen Horowitz (a16z)
```

These should resolve to one canonical entity.

Vantage therefore applies:

```text
Raw extracted name
        ↓
Normalization
        ↓
Known aliases
        ↓
Exact matching
        ↓
Conservative similarity
        ↓
Canonical entity
        │
        └── uncertain → human review
```

The system deliberately prefers unresolved ambiguity over confidently incorrect identity.

Poor entity resolution would corrupt all downstream intelligence.

---

# Event Resolution

Multiple evidence documents often describe the same real-world event.

For example:

```text
Publication:
Acme raises $40M Series B

Investor:
Why we invested in Acme

Company:
Acme closes Series B
```

should become:

```text
3 evidence documents
        ↓
1 canonical funding event
```

Funding rounds and fund closes support multi-source evidence.

The objective is not:

```text
3 documents
→
3 duplicated events
```

but:

```text
3 observations
→
1 real-world event
```

---

# Integrity Guardrails

Vantage now includes several reusable integrity protections.

These include:

- Conservative entity resolution
- Canonical funding-event resolution
- Canonical fund-close resolution
- Multi-source evidence
- Publication recency controls
- Taxonomy normalization
- Historical reconciliation
- Source measurement
- Processing idempotency
- Human resolution review
- Multi-event safety

## Multi-Event Safety

Some documents describe several financing events at once.

Examples include:

```text
The week's 10 biggest funding rounds
```

or:

```text
These startups raised...
```

The current funding extractor models one funding event per evidence document.

Rather than silently creating incomplete structured data, obvious compound evidence is currently preserved but excluded from single-event processing.

This is intentionally a safety guardrail rather than a full multi-event extraction subsystem.

---

# Source Measurement

Vantage measures the operating state and contribution of each source.

Current funding metrics include:

```text
Stored
Eligible
Processed
Backlog
Processing %
Confirmed
Confirmation %
Canonical events
Event conversion %
Unique events
Multi-source events
Overlap %
```

This allows source expansion to become evidence-driven.

The goal is not:

> support every source

The goal is:

> identify which sources materially improve the observable venture universe.

---

# Current Product Surfaces

The Flask application currently includes several product surfaces.

## News / Evidence

Search and filtering of discovered public evidence.

This remains useful for transparency and source inspection, but it is no longer the final product.

## Funding

Structured company financing activity including:

- Company
- Amount
- Currency
- Round type
- Investors
- Lead investors
- Evidence

## Companies

Company profiles can expose:

- Sector
- Geography
- Founding year
- Funding history
- Investors
- Lead investors
- Supporting evidence

## Investors

Investor profiles can increasingly expose:

- Investment activity
- Portfolio companies
- Lead investments
- Funds
- Stage exposure
- Sector exposure
- Geographic exposure
- Co-investors
- First-party evidence

## Funds

Structured fund and fund-close information.

## Data Quality

Visibility into:

- Entity resolution
- Potential duplicates
- Missing metadata
- Canonicalization
- Review queues

## Intelligence

The current intelligence layer provides early aggregate views such as:

- Knowledge-base counts
- Active investors
- Lead-investor activity
- Sector activity
- Recent funding
- Recent fund closes

This is only the beginning of the intended intelligence layer.

---

# Current Limitation

The acquisition architecture is increasingly generic, but the **operating model is still too source-by-source**.

Today:

- live sources and historical backfill are configured separately
- operations are commonly run for individual named sources
- source health is not yet fully generic across discovery methods
- historical coverage requires too much manual orchestration
- source-run telemetry is limited
- source-network expansion is not yet a first-class platform operation

This is the next major architectural constraint.

The solution is not more bespoke scraping.

The solution is a **Source Platform**.

---

# Target Source Platform

The next major architecture should be:

```text
                        SOURCE PLATFORM

                        Source Registry
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
                RSS        Sitemap        HTML
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                      Evidence Candidates
                              │
                              ▼
                       Source Runner
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
        discover            enrich            measure
           │                  │                  │
           └──────────────────┼──────────────────┘
                              ▼
                        Evidence Store
                              │
                              ▼
                       Event Pipeline
                              │
                              ▼
                       Knowledge Base
```

The desired operational principle is:

> **Adding source #37 should normally require configuration, not new application logic.**

---

# Unified Source Definition

The current distinction between:

```text
live source
```

and:

```text
backfill source
```

should progressively disappear.

A source may instead expose multiple discovery strategies.

Conceptually:

```text
Source

identity
├── key
├── name
├── type
└── region

discovery
├── incremental
└── historical

policies
├── relevance
├── URL rules
├── recency
└── enabled
```

Example:

```yaml
TechCrunch:

  type: publication
  region: Global

  discovery:

    incremental:
      method: rss
      url: ...

    historical:
      method: html
      url: ...
      pagination: ...
      selector: ...
```

This should remain a lightweight configuration model, not an elaborate scraping DSL.

---

# Fleet Operations

Source operations should evolve from:

```text
run one named source
```

toward:

```text
operate a source network
```

Conceptually:

```bash
vantage sync --all
```

```bash
vantage sync --type investor
```

```bash
vantage sync --mode historical
```

These commands are target architecture, not all implemented today.

The fleet runner should eventually support:

- source groups
- source types
- historical vs incremental modes
- isolated source failures
- idempotent operation
- consistent statistics
- controlled batch processing

A failing source should not stop the rest of the network.

---

# Source Operations & Telemetry

As the network grows, Vantage should persist operational information about source runs.

A lightweight model such as:

```text
SourceRun

source_key
mode
started_at
finished_at
status

documents_discovered
documents_retained
documents_saved

content_success
content_failure

events_created
events_confirmed

error
```

would allow the platform to answer:

```text
Which sources are healthy?

Which sources repeatedly fail?

Which sources discover lots of evidence but few events?

Which sources produce unique events?

Which sources mostly corroborate other sources?

Where should engineering effort be spent?
```

Configuration can remain in code initially.

The database needs to record **operations**, not necessarily become a full source-management CMS.

---

# Scaling Philosophy

Vantage should not onboard sources one at a time indefinitely.

Once the Source Platform exists, expansion should happen in batches.

Example:

```text
30 configured sources
        ↓
23 work generically
        ↓
4 partially work
        ↓
3 unsupported
```

That is a successful platform test.

The objective is not 30/30 compatibility.

The objective is to identify where reusable architecture provides the most value.

Engineering effort should be driven by measured contribution.

---

# Historical Coverage

Historical coverage is required because intelligence about behavioural change requires history.

Short backfills are useful for proving acquisition.

They are not sufficient for mature behavioural analysis.

For strategically important investors, the eventual target should be approximately:

```text
12 months minimum
        ↓
24 months where practical
```

Vantage does not need to create a perfect historical archive of every publication.

The more strategically valuable asset is:

> **A historical record of what important investors and venture-market participants actually did.**

---

# Investor Intelligence

The next major product milestone after Source Platform V1 is **Investor Behaviour V1**.

For each investor, Vantage should increasingly calculate:

## Investment Activity

```text
Investments
Lead investments
Follow-on investments
Capital deployed where disclosed
```

## Stage Exposure

```text
Pre-Seed
Seed
Series A
Series B
Series C
Growth
```

## Sector Exposure

```text
AI
Fintech
Climate
Defence
Health
Enterprise
etc.
```

## Geographic Exposure

```text
US
UK
Germany
France
India
etc.
```

## Relationships

```text
Frequent co-investors
Repeated syndicates
Portfolio relationships
```

---

# Behaviour Over Time

Static profiles are useful.

Behavioural intelligence is more valuable.

Vantage should progressively support transparent time windows such as:

```text
30 days
90 days
180 days
365 days
```

and compare periods:

```text
Current 90 days
        vs
Previous 90 days
```

Example:

```text
ACCEL

CURRENT 90D        PREVIOUS 90D

12 investments     7 investments
5 AI               2 AI
4 Seed             1 Seed
6 lead rounds      2 lead rounds
```

This can support evidence-backed observations such as:

> Observed Accel investment activity increased during the current period, with a larger share of recent activity concentrated in AI and Seed rounds.

The user should always be able to inspect the events and evidence supporting the conclusion.

---

# From Investor Intelligence to Market Signals

Once sufficient historical depth exists, Vantage can aggregate behaviour across investors.

Examples:

```text
Multiple investors
increase European defence activity
        ↓
repeated financing events
        ↓
more lead investments
        ↓
increasing observed ecosystem activity
```

Potential signal categories include:

- Sector momentum
- Stage shifts
- Geographic momentum
- Investor strategy changes
- Funding acceleration
- Co-investment changes
- Increasing investor conviction
- Capital-formation cycles

Signals should begin as transparent metrics and period-over-period comparisons.

Vantage should avoid opaque composite AI scores until the underlying evidence and behaviour are well understood.

---

# Evidence-Backed Intelligence

Inspectability is central to the product.

A user should be able to move from:

```text
European defence investment activity
appears to be increasing.
```

to:

```text
Why?
```

and inspect:

- Which investors changed behaviour
- Which financing events contributed
- Which companies were involved
- Which periods changed
- Which sources support the events
- Which evidence was editorial
- Which evidence was first-party

The objective is:

> **Inspectable intelligence, not unexplained conclusions.**

---

# Roadmap

## Phase 1 — News & Ingestion Foundation

**Status: Complete**

Delivered:

- Multi-source RSS ingestion
- Evidence normalization
- URL deduplication
- Relevance filtering
- Categorization
- Full-content retrieval
- Persistence
- Search / filtering
- Regression tests

---

## Phase 2 — Structured Knowledge Layer

**Status: Complete**

Delivered:

- Company entities
- Investor entities
- Funding rounds
- Funds
- Fund closes
- Investor participation
- Lead investors
- LLM structured extraction
- Entity aliases
- Entity resolution
- Human review
- Data-quality monitoring

---

## Phase 3 — Entity & Event Integrity

**Status: Complete**

Delivered:

- Canonical funding-event resolution
- Canonical fund-close resolution
- Multi-source evidence
- Historical reconciliation
- Stable entity identity
- Sector normalization
- Stage normalization
- Idempotent processing
- Transaction ownership
- Expanded regression coverage

---

## Phase 4 — Source Network V2

**Status: Complete**

Delivered:

- Generic discovery boundary
- RSS discovery
- Sitemap discovery
- HTML-listing discovery
- Normalized evidence contract
- Source provenance
- Source-aware relevance
- Investor first-party pilot
- Publication-date enrichment
- Recency controls
- Source Measurement V2
- First-party event convergence testing
- Historical corpus operations
- Multi-Event Safety V1

This phase demonstrated that Vantage can ingest materially different source types through reusable architecture.

---

# Phase 5 — Source Platform

**Status: Current major engineering focus**

The objective is to move from individual source operations to a scalable source network.

## 5.1 — Unified Source Registry

Targets:

- One canonical source definition
- Incremental discovery strategy
- Historical discovery strategy
- Source type / region
- URL rules
- Recency policies
- Relevance policies
- Configuration validation

The separate concepts of live source and backfill source should converge.

---

## 5.2 — Fleet Runner

Targets:

- Run groups of sources
- Run all sources
- Run by source type
- Run historical or incremental modes
- Isolate source failures
- Preserve idempotency
- Aggregate run statistics

Network operation becomes the primitive rather than single-source operation.

---

## 5.3 — Source Operations

Targets:

- Persistent `SourceRun` telemetry
- Generic source health
- Discovery statistics
- Content retrieval statistics
- Event-production statistics
- Failure tracking
- Historical run visibility

---

## 5.4 — Network Scale Test

Instead of onboarding one source at a time:

```text
~20–30 investor sources
+
~10 editorial / ecosystem sources
```

should be registered primarily through configuration.

The objective is to measure:

- Generic compatibility
- Source contribution
- Source reliability
- Unique-event contribution
- Evidence overlap

Unsupported sources should be tolerated rather than immediately engineered around.

---

## 5.5 — Historical Investor Corpus

Build meaningful historical depth for the most important tracked investors.

Target:

```text
~12 months initially
        ↓
toward 24 months where practical
```

The purpose is not archival completeness.

The purpose is behavioural history.

---

# Phase 6 — Investor Intelligence MVP

**Status: Foundation exists; major product development begins here**

## 6.1 — Investor Activity

Calculate:

- Investments
- Lead investments
- Stage exposure
- Sector exposure
- Geographic exposure
- Capital deployed where known

## 6.2 — Relationship Intelligence

Calculate:

- Co-investors
- Repeated syndicates
- Portfolio relationships

## 6.3 — Time Windows

Support:

- 30-day
- 90-day
- 180-day
- 365-day views

## 6.4 — Behaviour Change

Compare:

```text
current period
vs
previous period
```

across:

- investment count
- lead rate
- stage exposure
- sector exposure
- geography
- co-investors

## 6.5 — Evidence-Backed Investor Profiles

Every metric should remain drillable to:

```text
metric
→
canonical events
→
supporting evidence
```

---

# Phase 7 — Market & Signal Intelligence

Once sufficient historical breadth exists:

- Cross-investor sector trends
- Stage shifts
- Geographic momentum
- Funding acceleration
- Co-investment changes
- Investor strategy drift
- Capital formation trends
- Emerging themes

Signals should initially remain transparent and evidence-backed.

---

# Phase 8 — Search & Ecosystem Discovery

As the graph becomes richer, Vantage should become directly explorable.

Potential questions:

```text
European defence startups

AI companies in Germany

Seed rounds above $5M

Fintech investors active at Series A

Companies backed by both Accel and Sequoia

Investors increasingly active in robotics

Investors leading European AI infrastructure rounds

Investors whose sector exposure has changed materially
over the past six months
```

Search should exploit the structured graph rather than simply search article text.

---

# Phase 9 — Operating Scale & Productionization

**Status: Deferred until operating requirements justify it**

Current stack:

```text
Flask
SQLite
Local execution
CLI pipelines
```

Potential future evolution:

```text
PostgreSQL
Scheduled ingestion
Background workers
Cloud deployment
Production application server
Monitoring
CI/CD
Docker
Backups
Secret management
```

The first likely components to be outgrown are:

```text
manual execution
SQLite
```

not Flask itself.

Infrastructure should solve demonstrated operating constraints rather than anticipated ones.

---

# Current Technology

Vantage deliberately remains simple.

Core technologies include:

- Python
- Flask
- Jinja
- SQLAlchemy
- SQLite
- Flask-Migrate / Alembic
- feedparser
- BeautifulSoup
- requests
- OpenAI API
- Pydantic
- pytest
- HTML / CSS

The application currently runs locally.

The knowledge-building pipeline is primarily operated through the Flask CLI.

---

# Current CLI

Current operational commands include capabilities such as:

```bash
flask --app app vantage ingest
```

Run the normal discovery and intelligence pipeline.

```bash
flask --app app vantage sources
```

Inspect source contribution and processing state.

```bash
flask --app app vantage backfill --source <SOURCE>
```

Recover historical evidence for a configured historical source.

```bash
flask --app app vantage process --source <SOURCE>
```

Process already stored evidence for a specific source.

```bash
flask --app app vantage reconcile
```

Run historical reconciliation tooling.

The Phase 5 Source Platform should progressively reduce the need to operate individual sources manually.

---

# Development Principles

## 1. Information acquisition → structure → intelligence

Every major capability should strengthen this progression.

---

## 2. News is evidence, not the final product

Evidence is raw material for structured ecosystem knowledge.

---

## 3. Build the machine, not individual integrations

A fix is most valuable when it improves the platform rather than only one source or one article.

---

## 4. Configuration before bespoke code

A new source should normally require configuration.

---

## 5. Add adapters only when they generalize

Do not create new acquisition mechanisms for isolated edge cases without strong value.

---

## 6. Use LLMs for semantic understanding

LLMs are useful for interpreting unstructured evidence.

Deterministic code remains responsible for:

- Persistence
- Identity
- Constraints
- State
- Matching
- Aggregation
- Business rules
- Event reconciliation

---

## 7. Prefer conservative identity and event resolution

Incorrect canonicalization damages every downstream metric.

Ambiguity is preferable to false certainty.

---

## 8. Preserve provenance

First-party and independent evidence have different informational characteristics.

Both should remain visible.

---

## 9. Measure the observed universe

Vantage observes a subset of the market.

It should distinguish:

```text
Observed activity
```

from:

```text
Total market activity
```

until coverage becomes sufficiently representative.

---

## 10. Let scale expose systemic problems

Do not continually hunt isolated data imperfections.

Fix problems when:

```text
they recur
+
they threaten integrity
+
the fix strengthens the platform
```

---

## 11. Accept imperfect source coverage

The goal is not to make every website work.

The goal is to build a source network whose combined observations produce useful intelligence.

---

## 12. Build intelligence before infrastructure theatre

Do not introduce:

- Microservices
- Kubernetes
- complex distributed systems
- vector databases
- agent frameworks

unless real requirements justify them.

Technical sophistication is not the product.

---

# What Not to Build Yet

Avoid premature work on:

- Perfect publication archives
- Bespoke scraper-per-site architecture
- Universal web crawling
- Opaque AI scores
- Complex recommendation systems
- React rewrites
- Microservices
- Kubernetes
- Large-scale distributed infrastructure
- Unnecessary ontology complexity

The highest-value progression remains:

```text
MORE OBSERVATION
        ↓
MORE CANONICAL ACTIVITY
        ↓
MORE HISTORY
        ↓
BEHAVIOURAL DATA
        ↓
CHANGE OVER TIME
        ↓
VENTURE INTELLIGENCE
```

---

# Current Priority

The immediate engineering objective is:

> **Turn the proven Vantage ingestion and knowledge-building components into a scalable Source Platform capable of operating a network of sources, while beginning to develop investor behavioural intelligence on top of the accumulating historical graph.**

The next major work is therefore:

```text
Unified Source Registry
        ↓
Fleet Runner
        ↓
SourceRun Telemetry
        ↓
Network Scale Test
        ↓
Historical Investor Corpus
        ↓
Investor Behaviour V1
```

The project should now optimize less for:

```text
"Can we clean this source?"
```

and increasingly for:

```text
"Can the system observe, structure, measure,
and learn from the venture ecosystem at scale?"
```

That is the path from Project Vantage's origins as a news aggregator toward a genuine venture intelligence platform.