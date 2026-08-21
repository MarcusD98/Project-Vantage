Project Vantage

Project Vantage is an evidence-backed venture intelligence system.

It continuously observes public venture-market activity, converts those observations into structured historical knowledge, and uses that history to understand how investors, companies, sectors, stages and markets are changing over time.

Vantage began as a simple Python / Flask VC news aggregator.

It is evolving toward a more ambitious product:

A continuously operating intelligence system that observes the venture ecosystem, builds a trustworthy historical activity graph, and surfaces meaningful behavioural change.

The core progression is:

Public venture ecosystem
        ↓
Observation network
        ↓
Evidence
        ↓
Structured understanding
        ↓
Canonical entities & events
        ↓
Historical activity graph
        ↓
Behavioural change
        ↓
Market intelligence

Or more simply:

Information acquisition → structure → intelligence

News is not the product.

Articles, investor announcements, company posts, fund announcements, ecosystem publications and other public information are evidence from which Vantage builds a structured model of venture activity.

Product Thesis

Private-market intelligence is already a large and competitive category.

Platforms such as PitchBook, Dealroom, CB Insights, Harmonic and others provide sophisticated company, investor and market data.

Vantage should not try to win primarily by becoming another static startup database.

The more differentiated thesis is:

Treat the venture ecosystem as a continuously observed behavioural system.

Rather than asking only:

Which companies exist?
Who invested in them?

Vantage should increasingly answer:

Where is investor behaviour changing?

Which investors are accelerating or retreating?

Which sectors are attracting new conviction?

Which stages are becoming more active?

Where is lead-investor behaviour changing?

Which investors are converging around the same themes?

Which syndicates are forming or changing?

What real-world events prove those changes?

The goal is not:

“AI says defence is hot.”

The goal is:

Here is the measurable change, who drove it, the events behind it, and the evidence supporting those events.

That evidence chain is fundamental:

Signal
  ↓
Measurement
  ↓
Behaviour
  ↓
Canonical event
  ↓
Evidence

The governing product principle is:

Inspectable intelligence, not unexplained conclusions.

Strategic Wedge: Investor Behaviour

The first major intelligence wedge is investor behaviour.

Vantage should help answer:

What are investors investing in?

What are they leading?

Which sectors are they entering or leaving?

Which stages are they targeting?

Where are they investing?

Who are they investing alongside?

How active are they?

How is that behaviour changing over time?

Different source types provide different perspectives:

Editorial source
    ↓
What became news?

Investor first-party source
    ↓
What did this investor choose to do?

Company source
    ↓
What did the company announce?

Ecosystem / accelerator source
    ↓
What activity is emerging around a specific network?

Together:

Editorial evidence
        +
Investor evidence
        +
Company / ecosystem evidence
        ↓
Canonical activity
        ↓
Historical behaviour
        ↓
Venture intelligence

Investor first-party history is currently the most developed part of the Vantage corpus.

It is the first wedge, not the final scope of the product.

The Core Asset

The primary asset Vantage is building is not a collection of articles.

It is not simply a database of companies and investors.

It is:

A trustworthy historical activity graph of the observed venture ecosystem.

The graph connects:

Evidence
   ↓
Real-world events
   ↓
Companies
   ↓
Investors
   ↓
Funds
   ↓
Participation
   ↓
Lead relationships
   ↓
Time

As history accumulates, Vantage can establish behavioural baselines and measure change against them.

That historical observation is strategically important.

A system that has reliably observed, resolved and preserved venture activity over time becomes substantially harder to recreate than the individual Python services operating it.

Potential defensibility compounds through:

Source network
        +
Historical evidence corpus
        +
Canonical entity graph
        +
Canonical event graph
        +
Extraction history
        +
Provenance
        +
Behavioural history
        +
Signal methodology
        +
Customer workflow

The codebase itself is unlikely to be the primary moat.

The data-producing machine and the historical knowledge it accumulates are more important.

Product Architecture

Vantage has four connected layers.

1. Observation

Understand:

What is happening?

Responsibilities include:

discovering public venture information

operating many sources through reusable mechanisms

normalizing evidence

preserving source provenance

retrieving content and metadata

filtering noise

recovering historical evidence

monitoring source reliability and contribution

Current reusable discovery mechanisms include:

RSS
Sitemap
HTML listing

The objective is not simply to ingest more URLs.

It is to build a useful:

Observable venture universe

The source platform is configuration-first.

Adding source #50 should normally require configuration rather than a new scraper.

New acquisition mechanisms should be added when they unlock classes of strategically useful sources, not individual websites.

Potential future mechanisms may include:

Structured JSON / public APIs
Embedded page JSON
Pagination APIs
JavaScript-rendered / headless browsing
Newsletter / email ingestion
Regulatory or other structured public datasets

These should be introduced in response to demonstrated source-cohort needs.

2. Structured Knowledge

Understand:

Who did what?

Evidence is transformed into structured:

Companies

Investors

Funds

Funding rounds

Fund closes

Investor participation

Lead-investor relationships

Supporting evidence

Canonical identities

Historical activity

The target relationship is:

many observations
        ↓
one real-world event

For example:

TechCrunch article
        +
Investor announcement
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
Evidence

This is fundamentally different from:

3 articles
   ↓
3 duplicated funding-round records

Canonical truth is therefore deliberately separated from probabilistic extraction.

The current knowledge pipeline is:

RAW EVIDENCE
     ↓
VERSIONED EXTRACTION
     ↓
AUTOMATED VALIDATION
     ↓
PROMOTE / REVIEW / REJECT
     ↓
CANONICALIZATION
     ↓
KNOWLEDGE GRAPH

ExtractionRecord preserves what a specific extractor version believed about a specific piece of evidence.

This allows Vantage to improve extraction and validation without losing historical machine interpretation.

3. Behavioural Intelligence

Understand:

How is behaviour changing?

The current graph already supports investor-level intelligence including:

observed investment activity

lead activity

stage exposure

sector exposure

geographic exposure where coverage supports it

co-investors

financing-round participation

recent investments

current vs previous periods

confidence-qualified trends

Example:

ACCEL

Current 365D       Previous 365D

22 investments     11 investments
17 leads             8 leads

        ↓

Observed activity increased

        ↓

CORPUS-SUPPORTED

Static profiles are useful.

Behavioural change is more valuable.

4. Market Intelligence

This is now the major product frontier.

Market intelligence aggregates behaviour across many participants and asks:

What materially changed across the observed venture ecosystem?

Initial signal categories should remain simple, deterministic and inspectable.

Priority areas include:

Investor Activity Acceleration

Current activity
vs
Previous comparable period

Which investors are materially increasing or decreasing activity?

Sector Momentum

Which sectors are attracting increasing observed participation?

Stage and Lead-Activity Shifts

Are investors becoming more or less active at specific stages?

Is lead behaviour changing?

Investor Strategy Change

Is an investor's observed sector, stage or geographic behaviour materially different from its own historical baseline?

Later Signal Categories

Potential extensions include:

funding acceleration

changing syndicates

geographic momentum

increasing investor participation

capital-formation cycles

emerging themes

cross-investor convergence

The initial Market Signal Engine should be measurement-first rather than LLM-opinion-first.

For example:

AI Infrastructure activity
+42% vs previous 180 days

Driven by:
11 observed investors
18 canonical financing events
9 companies

Evidence →

Every signal should remain drillable through:

Signal
 ↓
Measurement
 ↓
Investors
 ↓
Companies
 ↓
Events
 ↓
Evidence

Observation Coverage and Confidence

Vantage observes a subset of the venture ecosystem.

It must never confuse:

Observed activity

with:

Total market activity

This becomes especially important as market-level signals are introduced.

For example:

Previous 180D
10 observed defence rounds

Current 180D
20 observed defence rounds

does not automatically mean defence activity doubled.

The observation network itself may also have changed.

Market intelligence must therefore increasingly account for:

source coverage

investor coverage

date coverage

processing completeness

comparable cohort composition

historical continuity

Where possible, behavioural comparisons should use a consistent observed cohort across both periods.

Where this is not possible, confidence should be explicitly qualified.

Current investor intelligence already distinguishes concepts such as:

CORPUS-SUPPORTED

Enough observations exist and the relevant discovered comparison corpus has been sufficiently processed.

OBSERVATIONAL

A pattern can be calculated, but equivalent observation coverage is incomplete or unavailable.

INSUFFICIENT

The evidence does not support a meaningful conclusion.

Importantly:

Corpus-supported does not mean complete knowledge of real-world activity.

It describes the strength of the observed Vantage corpus.

Source Platform

Vantage operates sources through a canonical source registry.

A source conceptually defines:

identity
├── key
├── name
├── type
└── region

discovery
├── incremental
└── historical

policies
├── URL rules
├── recency
└── enabled

Supported source types currently include:

publication
investor
ecosystem
company
structured

Supported discovery methods currently include:

rss
sitemap
html

The operating principle is:

Configuration before bespoke code.

Vantage should avoid becoming:

accel_scraper.py
sequoia_scraper.py
index_scraper.py
techcrunch_scraper.py
...

The desired scaling model is:

Large candidate cohort
        ↓
Run through generic platform
        ↓
Measure compatibility
        ↓
Keep productive sources
        ↓
Identify recurring failure classes
        ↓
Improve reusable mechanisms

A result such as:

50 candidate sources

34 productive
9 partially productive
7 unsupported

can still represent a successful source platform.

Universal compatibility is not the objective.

A useful network is.

Corpus Observability

As observation scale increases, Vantage also needs to understand the shape and quality of its own corpus.

A lightweight Corpus Observability layer should increasingly answer:

What can Vantage actually see?

Useful measurements include:

evidence growth over time

evidence by source type

number of productive sources

investor coverage

date coverage

historical coverage

processed vs unprocessed evidence

canonical event contribution

unique contribution

evidence overlap

source reliability

Useful visualizations may include:

Corpus growth over time

Evidence by:
Investor / Editorial / Company / Ecosystem

and source coverage matrices such as:

                 2024    2025    2026

Accel              █       █       █
Sequoia            █       █       █
Index               █       █       █
Greylock            █       █       █
a16z                 ·       ·       █

This layer is valuable both operationally and analytically.

It helps Vantage distinguish actual market change from changes in its own observation network.

The goal is useful observability, not visually impressive but low-information network diagrams.

Current State

Vantage now has a functioning observation, knowledge and early intelligence platform.

The current system is approximately:

                    PUBLIC ECOSYSTEM
                          │
                          ▼
                    SOURCE REGISTRY
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
                 CONTENT + METADATA
                          │
                          ▼
                   CATEGORIZATION
                          │
                          ▼
                VERSIONED EXTRACTION
                          │
                          ▼
                     VALIDATION
                          │
                          ▼
              PROMOTE / REVIEW / REJECT
                          │
                          ▼
                 CANONICALIZATION
                          │
                          ▼
                   KNOWLEDGE GRAPH
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         Companies     Investors      Funds
             │            │            │
             └──── Events & Relationships
                          │
                          ▼
                 HISTORICAL ACTIVITY
                          │
                          ▼
              BEHAVIOURAL INTELLIGENCE
                          │
                          ▼
                MARKET SIGNALS

The technical question:

Can Vantage continuously observe public venture activity and turn it into structured historical knowledge?

has been substantially de-risked.

The next questions are harder and more important:

Can Vantage operate across a materially broader observable universe?

and:

Can that historical graph produce intelligence valuable enough that professional users change how they work?

Current Priorities

The project is now changing mode.

The primary objective is no longer endless refinement of individual extraction or source edge cases.

The next stage is:

BROADER OBSERVATION
        +
MARKET SIGNALS
        +
PRODUCT VALIDATION

in parallel.

Priority 1 — Scale the Observable Universe

Expand the source network through cohorts rather than individual source perfection.

Near-term target direction:

20–30 investor sources
10–15 editorial sources
5–10 company / accelerator / ecosystem sources

Then expand further based on what the system reveals.

Measure:

compatibility

source reliability

evidence yield

candidate yield

event yield

unique contribution

overlap

extraction quality

historical coverage

Let scale expose systemic problems.

Do not build around isolated failures.

Priority 2 — Market Signal Engine V1

Begin converting the graph into cross-market behavioural intelligence.

Start with a small number of transparent signals:

1. Investor activity acceleration

2. Sector momentum

3. Stage / lead-activity shifts

4. Investor strategy change

Signals should initially be deterministic and graph-based.

LLMs may later help interpret or communicate structured measurements, but they should not invent the underlying signal.

Priority 3 — Productise the Intelligence

Once meaningful signals exist, significantly improve the product experience.

The next major UI / UX redesign should be built around:

What changed?
Who drove it?
Why?
What evidence supports it?
What should I investigate?

Potential product surfaces include:

intelligence overview

signal cards

trend visualisations

investor comparison

sector views

evidence drill-down

source / corpus observability

improved structured search

saved investigations

A frontend rewrite is not automatically required.

Flask / Jinja remains acceptable until interaction complexity demonstrates otherwise.

Priority 4 — Product Validation

Product discovery should run alongside engineering.

Potential users include:

venture investors

growth investors

corporate venture teams

LP / fund-of-funds intelligence teams

strategy teams

market intelligence teams

ecosystem researchers

Users should be given real intelligence tasks rather than asked whether they “like the product.”

Examples:

How is Sequoia's behaviour changing?

Which investors are increasing exposure to defence?

Who is becoming more active at Series A?

Which investors are driving AI infrastructure activity?

Which syndicates are becoming more common?

Which sectors show increasing lead-investor activity?

Important questions include:

What do users repeatedly investigate?

What is difficult to answer elsewhere?

Which signals make them investigate further?

What would they want monitored?

What would they pay to know sooner or more reliably?

Future workflow features should emerge from these answers.

Development Principles

1. Information acquisition → structure → intelligence

Every major capability should strengthen this progression.

2. News is evidence

Articles are raw material, not the product.

3. Canonical truth is earned

Probabilistic extraction should not automatically become canonical knowledge.

4. Preserve provenance

Important conclusions should remain traceable to underlying evidence.

5. Build the machine, not individual integrations

A fix is most valuable when it improves a reusable capability.

6. Configuration before bespoke code

New sources should normally require configuration.

7. Use LLMs for semantic understanding

LLMs should interpret unstructured evidence.

Deterministic systems should own:

persistence

workflow state

identity

constraints

validation

matching

canonicalization

aggregation

measurement

8. Prefer ambiguity over false certainty

Incorrect canonical knowledge contaminates downstream intelligence.

9. Manual review is an exception path

Human review should teach us where the machine needs improvement.

It should not become the machine.

10. Measure the observed universe

Do not confuse observation with complete real-world knowledge.

11. Let scale expose systemic problems

Do not continually hunt isolated imperfections.

Fix problems when:

they recur
+
they threaten integrity
+
the fix strengthens the platform

12. Accept imperfect source coverage

A valuable observation network matters more than universal compatibility.

13. Protect development speed

Do not introduce infrastructure without a demonstrated constraint.

14. Validate the product alongside the technology

Engineering determines what can be built.

Users determine what is valuable.

What Not to Build Yet

Avoid premature work on:

perfect source compatibility

scraper-per-site architecture

universal crawling

excessive validator refinement for isolated cases

opaque AI-generated market scores

unnecessary ontology complexity

frontend framework rewrites for their own sake

microservices

Kubernetes

Kafka or elaborate event buses

vector databases without a demonstrated retrieval requirement

agent frameworks without a demonstrated workflow requirement

infrastructure introduced because “real startups use it”

Technical sophistication is not the product.

Technical Direction

Vantage deliberately remains technically lightweight.

Current core technologies include:

Python

Flask

Jinja

SQLAlchemy

SQLite

Flask-Migrate / Alembic

OpenAI API

Pydantic

BeautifulSoup

feedparser

requests

pytest

HTML / CSS

Much of the knowledge-building system is also operable through Flask CLI commands.

The current development loop is intentionally simple:

edit
 ↓
pytest
 ↓
run
 ↓
measure
 ↓
inspect

That speed is valuable.

Infrastructure should solve demonstrated constraints rather than anticipated ones.

Potential future progression:

SQLite
   ↓
PostgreSQL

when concurrency, workload or deployment requirements justify it.

Likewise:

Local execution
   ↓
Scheduled / background execution

when continuous operation requires it.

And:

Local environment
   ↓
Containerised deployment

when reproducibility and deployment materially benefit.

Two lightweight engineering improvements have near-term value:

dependency management / reproducible installation

CI automatically running the test suite

These strengthen the development process without changing the product architecture.

Roadmap

Phases 1–4 — Observation & Knowledge Foundation

Status: Complete

Established:

evidence ingestion

normalized evidence

content retrieval

categorization

structured extraction

companies / investors / funds

funding rounds

fund closes

entity resolution

event resolution

provenance

historical operations

integrity tooling

Phase 5 — Source Platform V1

Status: Complete

Established:

canonical source registry

RSS / sitemap / HTML discovery

incremental / historical modes

source configuration validation

fleet operations

failure isolation

source-run telemetry

source measurement

Phase 6 — Investor Intelligence V1

Status: Complete / MVP established

Established:

durable investor identity

investment activity

lead activity

stage exposure

sector exposure

geography where supported

co-investors

temporal comparison

confidence-qualified intelligence

evidence-backed investor profiles

Phase 7 — Scalable Knowledge Pipeline

Status: Complete

Established:

durable ExtractionRecord

versioned extraction

deterministic validation

PROMOTE / REVIEW / REJECT states

safe canonical promotion

replay and reprocessing

pipeline measurement

canonical funding-event idempotency

historical contribution measurement

The extraction / canonical-truth boundary is now sufficiently strong to support broader scale.

Further refinement should be driven by recurring systemic failures rather than isolated records.

Phase 8 — Observation & Historical Scale

Status: Current

Objective:

Prove that Vantage can operate across a materially broader and more heterogeneous venture observation network.

Current work includes:

expanding investor cohorts

expanding historical coverage

measuring source compatibility

measuring evidence and event contribution

testing configuration-first acquisition

identifying reusable acquisition gaps

building corpus observability

Phase 8 does not need to be fully complete before intelligence work continues.

Phase 9 — Market & Signal Intelligence

Status: Starting in parallel

Objective:

Turn the historical activity graph into differentiated behavioural intelligence.

Initial V1 signals:

Investor activity acceleration
Sector momentum
Stage / lead shifts
Investor strategy change

Requirements:

transparent methodology

comparable time windows

observation-coverage awareness

confidence qualification

drill-down to canonical events

drill-down to underlying evidence

Phase 10 — Productisation, Search & Workflow

Status: Future / shaped by product validation

Potential capabilities include:

major UI / UX redesign

structured search

investor comparison

sector exploration

saved searches

watchlists

alerts

monitoring

recurring intelligence briefs

These workflows should be shaped by actual user behaviour rather than assumed upfront.

Brief History

1. VC News Aggregator

Vantage began approximately as:

RSS
 ↓
Articles
 ↓
Searchable news feed

The article was effectively the product.

2. Structured Venture Data

LLM extraction shifted the product toward:

Articles
   ↓
Companies
Investors
Funding rounds
Funds
Fund closes

News became raw material rather than the final output.

3. Canonical Knowledge

As data accumulated, identity and duplication became central problems.

The architecture evolved from:

1 article
→
1 database record

toward:

many observations
→
1 real-world event

Entity resolution, aliases, event resolution and multi-source evidence became foundational.

4. Source Platform

Observation expanded beyond editorial RSS into reusable:

RSS
Sitemaps
HTML listings

A canonical registry, historical modes, fleet operations and source measurement moved Vantage away from bespoke scraping.

5. Investor Intelligence

First-party investor history changed the core question from:

What happened?

to:

What did this investor do?

and then:

How is that behaviour changing?

Investor profiles, temporal comparisons and confidence-qualified intelligence followed.

6. Safe Knowledge at Scale

As the corpus grew, extraction could no longer write directly into canonical truth without stronger safeguards.

Vantage introduced:

Evidence
 ↓
Versioned Extraction
 ↓
Validation
 ↓
Safe Promotion
 ↓
Canonical Knowledge

This made larger-scale observation materially safer.

7. Current Stage — From Knowledge Machine to Intelligence Product

The core architecture now works well enough that the primary question has changed again.

It is no longer:

Can Vantage understand another venture article?

It is increasingly:

Can Vantage observe a broad enough universe, build trustworthy historical behaviour, and surface something genuinely valuable that professional users could not easily see before?

That is the current stage of the project.

Current Strategic Focus

The next stage of Vantage is:

BROADER SOURCE NETWORK
        ↓
MORE OBSERVED HISTORY
        ↓
TRUSTWORTHY ACTIVITY GRAPH
        ↓
MARKET SIGNAL ENGINE
        ↓
EXPLAINABLE INTELLIGENCE
        ↓
PRODUCT VALIDATION
        ↓
SEARCH / MONITORING / WORKFLOW

The engineering question is:

Can Vantage continuously observe the venture ecosystem at meaningful scale and safely convert activity into trustworthy historical knowledge?

The product question is:

Can that history reveal meaningful behavioural change that professional users care enough about to change how they work?

Those are now the two questions that should drive the roadmap.