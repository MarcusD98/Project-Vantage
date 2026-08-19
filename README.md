# Project Vantage

A Python/Flask application for monitoring venture capital news, extracting structured venture activity, and progressively building a lightweight VC ecosystem and intelligence platform.

Vantage began as a simple VC news aggregator. It is evolving into a system that turns public venture information into structured companies, investors, funding events, relationships, and eventually market intelligence.

---

# Product Vision

The project has three connected ambitions:

1. **Advanced VC News Aggregator** — understand *what is happening* across the venture ecosystem.
2. **VC Ecosystem Map** — understand *who is doing what* across companies, investors, funds, and financing events.
3. **Lightweight VC Intelligence Platform** — use accumulated structured data to understand *what it means*: trends, relationships, activity levels, sectors, geographies, funding patterns, and other market signals.

These are not intended to become three separate applications.

They are progressively richer layers of the same system.

```text
             VC INTELLIGENCE
        "What does it all mean?"
                  ▲
                  │ analysis
                  │
           ECOSYSTEM MAP
          "Who is doing what?"
                  ▲
                  │ entities + events
                  │
             NEWS ENGINE
          "What is happening?"
                  ▲
                  │ ingestion
                  │
       ─────────────────────
          EXTERNAL SOURCES
       ─────────────────────
       News / RSS / APIs
       VC websites
       Company announcements
       Public datasets
       etc.
```

The central development philosophy is therefore:

**information acquisition → structure → intelligence**

Or, from the user's perspective:

```text
What is happening?
        ↓
Who is doing what?
        ↓
What does it mean?
```

---

# 1. Advanced VC News Aggregator

The first layer is a high-quality signal filter for venture capital and startup activity.

The application ingests multiple RSS feeds, normalizes articles, removes duplicates, filters for VC relevance, categorizes articles, stores them in a persistent database, and presents them through a searchable and filterable Flask web application.

The objective is not simply to collect more headlines.

The objective is to improve:

- Coverage
- Relevance
- Classification
- Reliability
- Signal quality

Over time, ingestion can expand beyond RSS to include:

- News and startup publications
- VC firm websites and blogs
- Company announcements and press releases
- Selected APIs
- Public and regulatory datasets
- Other reliable public sources

The news layer serves as the evidence and ingestion foundation for everything built above it.

---

# 2. Structured VC Data Layer

Vantage now goes beyond storing articles.

Relevant articles can be converted into structured venture data.

The current intelligence pipeline can retrieve full article content and use an LLM to extract structured information including:

- Company
- Funding amount
- Currency
- Round type
- Investors
- Lead investors
- Company sector
- Company location
- Founding year
- Evidence describing the financing event

Conceptually:

```text
Article
   ↓
Full Article Content
   ↓
LLM Classification & Extraction
   ↓
Structured Funding Event
   ↓
Company + Investors + Funding Round
   ↓
Database
```

This represents an important architectural transition.

News is no longer only something Vantage displays.

News becomes **evidence from which structured venture activity can be created**.

---

# 3. VC Ecosystem Map

The next layer organizes structured activity around entities and relationships rather than around a chronological article feed.

The core entities currently include:

- Companies
- Investors
- Funding rounds
- Articles

Over time this can expand to include:

- Venture capital firms
- Funds
- Partners
- Founders
- Acquisitions
- IPOs
- Other relevant ecosystem events

The basic relationship model already begins to resemble:

```text
                    Investor A
                       │
                       │ invests
                       ▼
Investor B ───────► Funding Round
                       │
                       │ funds
                       ▼
                    Company
                       │
                       │ evidenced by
                       ▼
                     Article
```

A company can therefore accumulate financing history.

An investor can accumulate investment history.

Funding rounds connect those entities.

Articles provide evidence for those relationships.

This is the foundation of the future ecosystem map.

---

# 4. Lightweight VC Intelligence Platform

Once Vantage has accumulated enough clean structured historical data, the system can begin supporting analysis rather than only monitoring.

Potential questions include:

- Which VC firms are most active in European AI?
- Which sectors are seeing increased Series A activity?
- Which investors are becoming more active in defence technology?
- What new funds have major European VCs raised this year?
- Which companies have raised multiple rounds within a short period?
- Which investors frequently co-invest?
- Which geographies are attracting increasing venture activity?
- How are funding volumes and round sizes changing over time?

The progression becomes:

```text
Articles
   ↓
Events
   ↓
Entities
   ↓
Relationships
   ↓
Historical Dataset
   ↓
Metrics & Patterns
   ↓
Intelligence
```

The ambition is deliberately **lightweight** rather than attempting to recreate comprehensive commercial databases.

The focus is on useful venture-market monitoring and intelligence derived from a carefully designed network of public information sources.

---

# Architecture Direction

The intended long-term information flow is:

```text
RSS / News / APIs / Public Sources
              ↓
          INGESTION
              ↓
     Normalize / Deduplicate
              ↓
       Retrieve Full Text
              ↓
     Filter / Classify / Enrich
              ↓
      LLM Event Extraction
              ↓
     Entity & Event Resolution
              ↓
           DATABASE
              ↓
 Companies ↔ Investors ↔ Funds
              ↓
 News / Funding / Profiles / Search
              ↓
     Analytics & Intelligence
```

The original Flask/RSS application is therefore not intended to be discarded later.

It represents the first version of the ingestion, persistence, querying, and presentation layers of the broader system.

---

# Current State — Project Vantage Checkpoint

Vantage has progressed substantially beyond the original RSS prototype.

The application currently includes four broad layers.

## 1. Ingestion

- Multiple configurable RSS sources
- RSS parsing with `feedparser`
- Article normalization
- HTML cleaning with BeautifulSoup
- VC relevance filtering
- Article categorization
- URL-based deduplication
- Persistent article storage
- Source-health monitoring
- In-memory feed caching

Current article categories include:

- Funding Round
- Fund News
- M&A
- IPO
- Other

---

## 2. Article Processing

Vantage can retrieve and persist full article content rather than relying only on RSS titles and summaries.

This allows downstream intelligence processing to operate on substantially richer source material.

The application also tracks whether articles have been processed by the intelligence layer, allowing batches to avoid repeatedly processing the same articles.

Conceptually:

```text
RSS Article
     ↓
Stored Article
     ↓
Full Content Retrieval
     ↓
Intelligence Processing State
```

---

## 3. AI-Assisted Structured Extraction

Vantage integrates with the OpenAI API to transform unstructured articles into validated structured funding information.

The extraction layer can currently identify:

- Whether an article describes a funding event
- Evidence supporting that determination
- Company name
- Funding amount
- Currency
- Round type
- Participating investors
- Lead investors
- Sector
- Company city
- Company country
- Founding year

Structured responses are validated before being persisted.

The application can then create or enrich:

- Companies
- Investors
- Funding rounds
- Company metadata
- Investor relationships
- Lead-investor relationships
- Funding-event evidence

This has created the first genuine **VC knowledge layer** within the application.

---

## 4. Product & User Interface

The original simple article feed has evolved into a more coherent product interface under the working name **Vantage**.

The application currently provides:

### News

A searchable and filterable venture-news feed.

### Funding Intelligence

A structured view of detected financing events, including:

- Company
- Round size
- Round type
- Investors
- Lead investors
- Event evidence
- Source article

### Company Profiles

Company pages can display:

- Sector
- Location
- Founding year
- Funding history
- Investors
- Lead investors
- Supporting evidence

### Investor Profiles

Investor pages can display tracked investment activity and link back to portfolio companies and financing events.

### Source Health

A monitoring view of the ingestion network and source performance.

The UI now uses a shared application shell and a more deliberate intelligence-dashboard design.

---

# Current Product Architecture

At the current checkpoint, Vantage can be summarized as:

```text
1. INGESTION
   News sources
        ↓
   RSS / articles

2. PROCESSING
   Normalize
   Deduplicate
   Filter
   Classify
   Retrieve content
        ↓

3. INTELLIGENCE
   LLM classification
   Structured extraction
   Event evidence
        ↓

4. KNOWLEDGE
   Companies
   Investors
   Funding rounds
   Relationships
        ↓

5. PRODUCT
   News
   Funding Intelligence
   Company profiles
   Investor profiles
   Source monitoring
```

This marks the transition from **VC news aggregator** toward an early **VC intelligence system**.

---

# Current Technology

The application deliberately remains technically lightweight.

Current core technologies include:

- Python
- Flask
- Jinja
- SQLAlchemy
- SQLite
- Flask-Migrate / Alembic
- `feedparser`
- BeautifulSoup
- OpenAI API
- Pydantic
- `pytest`
- HTML / CSS

The application currently runs locally.

This simplicity is intentional.

Infrastructure should become more sophisticated when product requirements justify it, rather than because a production-scale architecture is theoretically possible.

---

# Immediate Development Priority

## Reliable VC Knowledge Base

The next major development chapter is **not simply adding more features**.

The priority is making the structured intelligence layer increasingly reliable.

Before Vantage can produce trustworthy ecosystem analytics, it needs trustworthy entities and events.

The immediate focus is therefore:

```text
Extracted Records
       ↓
Entity Resolution
       ↓
Canonical Companies & Investors
       ↓
Reliable Events
       ↓
Connected Knowledge Base
```

---

# Entity Resolution & Data Quality

LLM extraction can identify entities from individual articles, but real-world entities may appear under different names.

For example:

```text
Andreessen Horowitz
a16z
Andreessen Horowitz (a16z)
```

should not become three unrelated investors.

Likewise:

```text
Brazil's Kesh
Kesh
```

may refer to the same company.

Vantage therefore needs a canonical entity layer.

Conceptually:

```text
Raw extracted names
        ↓
Normalization
        ↓
Alias matching
        ↓
Entity resolution
        ↓
Canonical entity

Andreessen Horowitz
├── a16z
└── Andreessen Horowitz (a16z)
```

This is foundational for future intelligence.

Without reliable entity resolution, metrics such as investor activity, co-investment patterns, portfolio relationships, and funding histories become fragmented or misleading.

---

# Intelligence Pipeline Direction

The current intelligence pipeline works, but processing should progressively become systematic rather than manually invoked.

The desired flow is:

```text
NEW ARTICLE
     ↓
Store
     ↓
Retrieve Full Content
     ↓
Candidate Relevance Filter
     ↓
LLM Classification
     ↓
Structured Extraction
     ↓
Entity Resolution
     ↓
Event Resolution
     ↓
Database
```

Each relevant article should eventually move through a defined processing lifecycle.

The goal is to transform Vantage from a prototype that *can* generate intelligence into a system that **continuously builds its own structured knowledge base**.

---

# Broader Event Model

Funding rounds are the first structured event type because they provide a clear and useful starting point.

They should not remain the only event type.

Future structured events may include:

- Funding Round
- New Fund / Fund Raise
- Acquisition
- IPO
- Strategic Investment
- Geographic Expansion
- New Office
- Partner Join / Departure
- Portfolio Exit
- Company Launch
- Other significant VC ecosystem activity

For example:

```text
Article:
"Northern Gritstone to open San Francisco office"

              ↓

Entity:
Northern Gritstone

              ↓

Event:
Geographic Expansion

              ↓

Location:
San Francisco
```

This turns news into machine-readable ecosystem activity.

---

# Ecosystem Discovery

Once entity quality is sufficiently reliable, Vantage should make the underlying ecosystem directly browseable.

The primary navigation can progressively evolve toward:

```text
VANTAGE

News
Funding
Companies
Investors
Sources
```

## Companies Directory

A searchable company directory could expose:

- Company
- Sector
- Geography
- Latest funding round
- Total tracked rounds
- Known investors
- Recent activity

Example:

```text
Companies

Computomics
Agritech · Germany
€6.3M Series B
4 tracked investors

Etched
AI Hardware
$700M latest round
Jane Street

Yuno
Fintech
$45M Series B
```

## Investors Directory

A searchable investor directory could expose:

- Investor
- Tracked investments
- Lead investments
- Sectors
- Geographies
- Recent activity
- Portfolio relationships

These discovery interfaces represent the next visible evolution from a news application toward an ecosystem product.

---

# Intelligence & Analytics

Once Vantage has accumulated a sufficiently clean structured historical dataset, analytics become significantly more valuable.

Potential investor intelligence:

```text
SEQUOIA CAPITAL

Tracked investments       17
Lead investments           8
Most active sector         AI
Most active geography      US
Median tracked round       $65M
Recent activity            ↑
```

Potential market intelligence:

```text
LAST 30 DAYS

Tracked AI funding         $2.1B
Tracked Fintech funding    $840M
Tracked Defence funding    $620M

Most active investors
1. Accel
2. Sequoia
3. Index
```

Potential analysis areas include:

- Funding volume
- Round-size trends
- Sector activity
- Geography activity
- Investor activity
- Lead-investor activity
- Co-investment relationships
- Company funding velocity
- Fundraising patterns
- Ecosystem concentration
- Emerging market signals

This represents the transition from:

**"Here are the events."**

to:

**"Here is what the events collectively tell us."**

---

# Source Network V2

Source expansion remains important, but the next stage should prioritize **source quality and evidence diversity**, not simply the number of RSS feeds.

The future source network may combine:

```text
EDITORIAL SOURCES
TechCrunch
Sifted
TechCabal
Inc42
Tech.eu
etc.

        +

VC FIRMS
Sequoia
Accel
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

This enables a single ecosystem event to eventually be supported by multiple sources:

```text
                    FUNDING EVENT
                         │
            ┌────────────┼────────────┐
            ↓            ↓            ↓
       Publication   Company PR    Investor Post
```

This can improve both coverage and confidence in the resulting knowledge base.

---

# Productionization

The current local architecture is appropriate for the present stage of the project.

Eventually, requirements may justify moving from:

```text
Flask
SQLite
Local machine
Manual processing
```

toward something closer to:

```text
Flask / application server
PostgreSQL
Background workers
Scheduled ingestion
Automated intelligence processing
Deployment
Logging
Monitoring
CI/CD
```

Potential future infrastructure may include:

- PostgreSQL
- Background job processing
- Scheduled ingestion
- Production WSGI server
- Cloud deployment
- Application monitoring
- CI/CD
- Containerization

These are intentionally **not immediate priorities**.

Infrastructure should be introduced when it solves a real product or engineering constraint.

---

# Roadmap

## Phase 1 — News & Ingestion Foundation

**Status: largely achieved**

Build a robust VC information-ingestion foundation.

### Delivered / underway

- Multi-source RSS ingestion
- Article normalization
- Deduplication
- Relevance filtering
- Categorization
- Persistent storage
- Search
- Filtering
- Source-health monitoring
- Full article retrieval
- Automated tests

---

## Phase 2 — Structured VC Data Layer

**Status: working prototype**

Transform unstructured venture news into structured entities and events.

### Delivered / underway

- Company model
- Investor model
- Funding-round model
- Company ↔ funding relationships
- Investor ↔ funding relationships
- Lead-investor relationships
- LLM structured extraction
- Event evidence
- Company metadata enrichment
- Article intelligence-processing state
- Batch intelligence processing

### Next priorities

- Entity normalization
- Alias handling
- Duplicate entity resolution
- Data-quality safeguards
- More systematic intelligence processing
- Event confidence / validation where useful

---

## Phase 3 — VC Ecosystem Map

**Status: foundations built**

Build a navigable representation of companies, investors, and venture activity.

### Priorities

- Canonical companies
- Canonical investors
- Companies directory
- Investors directory
- Improved company profiles
- Improved investor profiles
- Activity timelines
- Broader event types
- Funds and fund activity
- Relationship discovery
- Co-investment relationships

Conceptually:

```text
Articles
   ↓
Events
   ↓
Canonical Entities
   ↓
Companies ←→ Investors ←→ Funds
   ↓
Profiles & Directories
   ↓
Activity Timelines
   ↓
Ecosystem Map
```

---

## Phase 4 — VC Intelligence Layer

**Status: early foundations**

Use the structured historical dataset to generate useful market intelligence.

### Priorities

- Funding metrics
- Investor activity metrics
- Sector trends
- Geography trends
- Historical activity analysis
- Investor comparisons
- Co-investment analysis
- Funding velocity
- Dashboards
- Visualizations
- Advanced querying

Conceptually:

```text
Structured Historical Data
            ↓
     Metrics & Trends
            ↓
    Relationships & Patterns
            ↓
       Comparisons
            ↓
       Dashboards
            ↓
        Intelligence
```

---

## Phase 5 — Source Network & Automation

Expand the evidence network and reduce manual processing.

### Priorities

- Selected VC firm sources
- Company announcements
- Higher-value primary sources
- Improved source reliability
- Automated ingestion lifecycle
- Automated intelligence processing
- Multi-source event evidence

---

## Phase 6 — Productionization

Move beyond the local prototype once scale or product requirements justify it.

### Potential priorities

- PostgreSQL
- Background jobs
- Scheduling
- Deployment
- Monitoring
- CI/CD
- Containerization
- Production configuration

---

# Near-Term Execution Plan

From the current Project Vantage checkpoint, the highest-impact sequence is:

```text
CURRENT CHECKPOINT
Project Vantage prototype
        │
        ▼
1. ENTITY RESOLUTION + DATA QUALITY
Canonical companies and investors
Normalize aliases and duplicates
        │
        ▼
2. SYSTEMATIC INTELLIGENCE PIPELINE
Articles consistently become structured events
        │
        ▼
3. BROADER EVENT MODEL
Funding + funds + M&A + IPO + VC activity
        │
        ▼
4. ECOSYSTEM DISCOVERY
Companies directory
Investors directory
Search and filters
        │
        ▼
5. INTELLIGENCE / ANALYTICS
Trends
Investor activity
Sector flows
Geographies
Co-investment patterns
        │
        ▼
6. SOURCE NETWORK V2
VC firms
Company announcements
Primary evidence
        │
        ▼
7. PRODUCTIONIZATION
PostgreSQL
Jobs
Deployment
Monitoring
```

---

# What We Are Deliberately Not Prioritizing Yet

Vantage should avoid premature complexity.

The following may become useful later, but they are not currently the highest-impact development priorities:

- Kubernetes
- Complex microservice architectures
- Large-scale cloud infrastructure
- Vector databases without a clear use case
- Embeddings simply because they are available
- User accounts before there is a strong user-specific workflow
- Large numbers of low-quality news sources
- Elaborate network visualizations before entity quality is reliable
- Extensive UI polish without corresponding product functionality

The system should remain as simple as possible while the underlying product and data model mature.

---

# Guiding Principles

## 1. Information acquisition → structure → intelligence

Every major capability should strengthen this progression.

## 2. News is evidence, not the final product

Articles are the raw material from which ecosystem knowledge is created.

## 3. Structured data must become trustworthy before analytics become sophisticated

A beautiful dashboard built on fragmented entities produces misleading intelligence.

## 4. Prefer useful product capabilities over premature infrastructure

Technical sophistication should solve real constraints.

## 5. Build progressively

The project should continue evolving through working vertical slices:

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
Profile
  ↓
Metric
  ↓
Insight
```

Each layer should make the next layer possible.

---

# Current Strategic Focus

The immediate development objective is:

> **Turn Vantage's collection of extracted records into a clean, canonical VC knowledge base.**

That means the next major engineering chapter is **Entity Resolution & Data Quality**.

Once entity identity is reliable, Vantage can confidently build:

- Company discovery
- Investor discovery
- Portfolio relationships
- Funding histories
- Investor activity metrics
- Co-investment networks
- Sector and geography analysis
- Market intelligence

This is the bridge between the current working prototype and the broader VC ecosystem and intelligence platform envisioned from the beginning.