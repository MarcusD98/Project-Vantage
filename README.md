Library
/
README_Project_Vantage.md


Project Vantage
Project Vantage is an evidence-backed venture intelligence system.

It observes public venture-market activity, converts fragmented evidence into structured historical knowledge, and uses that history to understand how investors, companies, sectors, stages and markets are changing over time.

The core progression is:

Information acquisition
        ↓
Structured knowledge
        ↓
Historical behaviour
        ↓
Intelligence
        ↓
User value
Vantage began as a Python / Flask VC news aggregator.

News is no longer the product.

Articles, investor announcements, company posts, fund announcements and other public information are evidence from which Vantage builds a structured model of venture activity.

The long-term ambition is to build a trustworthy intelligence layer over the venture ecosystem.

Product Thesis
Private-market intelligence is already a large and competitive category.

Vantage should not try to win primarily by becoming another static database of startups, investors and funding rounds.

The more differentiated thesis is:

Treat the venture ecosystem as a continuously observed behavioural system.

Instead of only asking:

Which companies exist?

Who invested in them?

How much did they raise?

Vantage should increasingly answer:

Which investors are becoming more or less active?

Which sectors are gaining or losing investor participation?

Which stages are changing?

Where is lead-investor behaviour shifting?

How is an investor's strategy changing over time?

Which investors are converging around the same themes?

Which syndicates are forming or changing?

What real-world events support those conclusions?

The objective is not:

"AI says cybersecurity is hot."

It is:

Here is the measured change, who drove it, the canonical events behind it, and the evidence supporting those events.

The governing product principle is:

Inspectable intelligence, not unexplained conclusions.

The Core Asset
The primary asset Vantage is building is not the application code or a collection of articles.

It is:

A trustworthy historical activity graph of the observed venture ecosystem.

Conceptually:

Evidence
   ↓
Real-world events
   ↓
Companies / Investors / Funds
   ↓
Participation / Lead relationships
   ↓
Time
   ↓
Historical behaviour
As that history accumulates, Vantage can establish behavioural baselines and detect change.

Potential defensibility compounds through:

Observation network
        +
Historical evidence corpus
        +
Canonical entities
        +
Canonical events
        +
Extraction history
        +
Provenance
        +
Behavioural history
        +
Signal methodology
        +
User workflow
The codebase matters because it produces and protects this asset.

The accumulated evidence, identities, event history and behavioural context are ultimately more difficult to recreate than the individual services that operate them.

Current Strategic Wedge: Investor Behaviour
Investor behaviour is the first major intelligence wedge.

Vantage can already model and analyse:

observed investment activity

lead activity

stage exposure

sector exposure

geographic exposure where coverage supports it

co-investors

recent investments

current vs previous periods

confidence-qualified behavioural change

First-party investor evidence is particularly useful because it gives Vantage an observable record of what an investor publicly chose to associate itself with.

It must not be interpreted as a complete record of everything that investor actually did.

Funding rounds are currently the most mature event type and therefore the primary analytical primitive.

They are not intended to become the entire Vantage domain model.

The system already also models funds and fund closes. Broader venture events should be added as the product and domain understanding justify them rather than through premature ontology expansion.

How Vantage Works
The current architecture has four connected layers.

1. Observation
Question: What happened?

Vantage discovers public evidence through a canonical source registry and reusable acquisition mechanisms.

Current discovery methods:

RSS

XML sitemaps

HTML listings

Current source configuration supports:

publications

investors

ecosystem sources

company sources

structured sources

The presently configured corpus is concentrated on publications and first-party investor sources.

The source platform is deliberately configuration-first:

Source Registry
      ↓
RSS / Sitemap / HTML
      ↓
Normalized Evidence
Adding a new source should normally require configuration rather than a new scraper.

The platform also supports:

incremental discovery

historical discovery

source-specific URL policies

publication-date recovery

relevance filtering

content retrieval

source compatibility probing

fleet execution

failure isolation

persistent source-run telemetry

source contribution measurement

The current registry contains 19 enabled investor sources, including multiple historical-capable investors.

The purpose of future source expansion is not to maximise source count.

It is to improve the observable universe.

2. Structured Knowledge
Question: Who did what?

Persisted evidence is transformed into structured knowledge about:

companies

investors

funds

funding rounds

fund closes

investor participation

lead-investor relationships

supporting evidence

canonical identities

The target relationship is:

Many observations
       ↓
One real-world event
For example:

Investor announcement
        +
Company announcement
        +
Editorial article
        ↓
One canonical financing event
        ↓
Company
Investors
Lead investors
Amount
Stage
Date
Evidence
This is fundamentally different from storing three articles as three separate funding events.

Safe knowledge pipeline
Probabilistic extraction is deliberately separated from canonical truth:

RAW EVIDENCE
     ↓
STRUCTURED EXTRACTION
     ↓
EXTRACTION RECORD
     ↓
DETERMINISTIC VALIDATION
     ↓
PROMOTE / REVIEW / REJECT
     ↓
CANONICALIZATION
     ↓
KNOWLEDGE GRAPH
ExtractionRecord preserves an append-oriented history of what a specific extractor version believed about a specific piece of evidence.

Replay creates a new extraction record rather than overwriting historical machine interpretation.

Only validated PROMOTE results are permitted to reach canonical persistence.

Failed promotions remain observable and retryable.

Some legacy Article processing fields remain as compatibility state while the newer extraction architecture becomes authoritative across the full pipeline. That migration should continue only where it materially improves correctness or maintainability.

3. Behavioural Intelligence
Question: How is behaviour changing?

Canonical historical events support investor-level behavioural analysis.

For a given investor, Vantage can compare equal periods and analyse:

Current period
      vs
Previous period
across:

investment activity

lead activity

companies

sectors

stages

geography

co-investors

This layer deliberately distinguishes measurement from confidence.

A computable trend is not automatically a trustworthy trend.

4. Market Intelligence
Question: What changed across the observed market?

This is the current product frontier.

Market intelligence aggregates canonical behaviour across a comparable observed cohort rather than blindly comparing whatever Vantage happened to discover in each period.

The first implemented market signal is:

Sector Momentum V1 — Implemented
Sector Momentum compares canonical funding events across equal windows for investors whose relevant first-party corpora are sufficiently complete.

It measures:

current vs previous canonical event count

company count

investor participation

lead-event participation

absolute change

percentage change

contributing investors

underlying canonical event IDs

dimensional coverage

cohort coverage

Signal interpretation is deterministic.

An LLM does not decide whether a sector is rising or falling.

Catch-all values such as Other, Unknown and Unclassified may remain valid measurements but are not promoted as market signals.

The next intended signal families are:

Investor Activity Acceleration

Stage / Lead-Activity Shifts

Investor Strategy Change

Signal methodology should become more selective as it matures. A statistically or numerically non-flat measurement should not automatically be treated as commercially meaningful change.

Observation Coverage and Confidence
Vantage observes a subset of the venture ecosystem.

It must never confuse:

Observed activity

with:

Total real-world market activity

Changes in the observation network can otherwise be mistaken for changes in the market.

For this reason, behavioural comparisons increasingly account for:

source coverage

historical continuity

publication-date coverage

processing completeness

canonical identity

comparable cohort composition

analytical-dimension coverage

Current confidence concepts include:

CORPUS-SUPPORTED
The observed Vantage corpus is sufficiently complete for the specific comparison being made.

OBSERVATIONAL
A pattern can be calculated, but equivalent corpus coverage is unavailable or incomplete.

INSUFFICIENT
The evidence does not support a meaningful comparison.

Corpus-supported does not mean complete knowledge of real-world activity.

It describes the quality of the relevant observed Vantage corpus.

Coverage gates should also be scoped to the analytical question.

For example, an undated unrelated commentary article should not invalidate a funding-activity comparison, while undated funding evidence capable of changing the comparison should.

Corpus Observability
Vantage already measures important characteristics of its own observation network and corpus.

Current backend observability includes:

configured and productive sources

incremental and historical capability

stored evidence

dated vs undated evidence

historical date span

extraction attempts

promotion / review / rejection

processing backlog

canonical event contribution

unique event contribution

multi-source overlap

This should become a visual product surface.

Useful first visualisations include:

corpus growth over time

evidence by source family

investor-by-time coverage heatmaps

discovered → processed → promoted → canonical funnels

source contribution and overlap

historical / processing completeness

A visually impressive node graph is not the objective.

The first question Corpus Observability should answer is:

What can Vantage actually see, and how much should we trust comparisons based on it?

Current State
Vantage is no longer an experimental news scraper.

The repository now contains a functioning observation, structured-knowledge and early market-intelligence platform.

                  PUBLIC ECOSYSTEM
                         │
                         ▼
                  SOURCE REGISTRY
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
             RSS      Sitemap      HTML
              │          │          │
              └──────────┼──────────┘
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
                CANONICAL KNOWLEDGE
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Companies   Investors    Funds
              │          │          │
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
Established foundation
reusable evidence acquisition

canonical source registry

incremental and historical source operation

source probing and fleet execution

persistent SourceRun telemetry

content and publication-date enrichment

structured LLM extraction

Pydantic extraction contracts

durable versioned ExtractionRecord

deterministic validation

safe promotion

replay / reprocessing

company and investor entity resolution

aliases and resolution review

canonical funding-event resolution

multi-source evidence

lead-investor relationships

funds and fund closes

canonical stage and sector normalization

historical reconciliation and integrity tooling

source contribution measurement

corpus observability metrics

investor behavioural intelligence

temporal corpus confidence

comparable-cohort market comparison

Sector Momentum V1

Flask / Jinja operational UI

Flask CLI operational tooling

The current local test suite contains 379 passing tests.

That is useful evidence of engineering discipline, but test count alone is not proof of correctness.

Current Constraints
The project has reached a point where engineering trustworthiness matters as much as feature velocity.

The main risks are increasingly silent correctness and reproducibility failures, not simply obvious application crashes.

Examples include:

incorrect entity resolution

duplicate or incorrectly merged canonical events

extraction drift

misleading publication dates

incomplete corpus interpreted as behavioural change

weak tests that remain green while behaviour is wrong

local reference data that cannot be recreated

loss or corruption of the accumulated local corpus

Current engineering constraints include:

SQLite is the active datastore

database configuration is still local/application-specific

the accumulated local database is not protected by Git

the repository does not yet contain a reproducible dependency manifest

CI is not yet running the test suite automatically on every change

some important reference data can still depend on local database state

the test suite has not yet undergone a systematic test-trust / mutation audit

These are not reasons to redesign the architecture.

They are reasons to strengthen the guardrails around it.

Roadmap
The roadmap is now driven by demonstrated product and engineering constraints rather than historical phase numbering.

Completed Foundation
Observation & Knowledge Foundation — Complete
Established evidence ingestion, content retrieval, structured entities, funding rounds, funds, fund closes, entity resolution, event resolution, provenance and historical operations.

Source Platform V1 — Complete
Established the canonical source registry, reusable RSS / sitemap / HTML discovery, incremental and historical modes, source validation, fleet execution, persistent source runs, failure isolation and measurement.

Investor Intelligence V1 — Complete / MVP Established
Established investor profiles, activity, lead behaviour, sector/stage/geographic exposure, co-investors, temporal comparison and confidence-qualified intelligence.

Scalable Knowledge Pipeline — Complete / Foundation Established
Established versioned extraction, deterministic validation, safe promotion, replay, measurement and canonical event integrity.

Further changes here should be driven by recurring systemic failures rather than isolated records.

Observation Scale V1 — Current Objective Achieved
The investor observation network has been materially broadened using existing generic acquisition mechanisms.

Compatibility probing, historical acquisition, source measurement and corpus observability have demonstrated that the source platform can scale beyond the original small cohort.

Further investor-source expansion is no longer the default priority.

New sources should be added when they materially improve the observable universe or expose a reusable acquisition gap.

Market Intelligence — Active
A generic equal-window comparable-cohort market comparison engine exists.

Sector Momentum V1 is implemented and has been empirically exercised against the expanded investor corpus.

The remaining initial signal families are not yet complete.

Immediate Priorities
1. Engineering Trustworthiness V1
Before substantially increasing system complexity, strengthen the safeguards around what already exists.

Priority work:

reproducible dependency / environment specification

database backup and restore

environment-driven configuration

automated CI running the full test suite

systematic test-trust audit

coverage analysis of critical truth-producing paths

targeted mutation / invariant testing where valuable

small deterministic "golden corpus" regression suite

reproducible bootstrap/reference data for important canonical aliases

The objective is not infrastructure sophistication.

It is:

Make it difficult for Vantage to become silently wrong or impossible to reproduce.

SQLite should remain until concurrency, deployment, reliability or workload gives a concrete reason to move to PostgreSQL.

2. Continue Market Signal Engine V1
After the trustworthiness checkpoint, continue converting historical activity into useful behavioural intelligence.

Current sequence:

Sector Momentum                 ✅
Investor Activity Acceleration  NEXT
Stage / Lead Shifts             NEXT
Investor Strategy Change        NEXT
Signals should remain:

deterministic

measurement-first

coverage-aware

confidence-qualified

inspectable

traceable to canonical events and evidence

The signal layer should become better at distinguishing material change from merely non-zero change.

3. Venture-Capital Domain Grounding
Funding rounds are a strong first wedge, but Vantage is intended to model a broader venture ecosystem.

Before expanding the event ontology aggressively, create a concise domain primer covering the mechanics most relevant to the product, including areas such as:

venture firms and fund structures

GPs and LPs

fundraising and fund lifecycles

portfolio construction and reserves

startup equity and dilution

primary and secondary transactions

SAFEs and convertible instruments

follow-ons and pro rata rights

ownership and lead behaviour

exits and liquidity

fund performance metrics

investor workflows

reporting

regulation

firm structures and decision processes

The primer should explicitly be a compressed grounding document, not a complete representation of venture-capital industry knowledge or regulation.

Its purpose is to prevent the software ontology from growing faster than our understanding of the domain it is intended to represent.

4. Selective Expansion of the Observation Network
The next acquisition improvement should preferably unlock a new class of strategically useful evidence, rather than simply adding another investor website.

Potential future acquisition classes include:

structured public APIs

regulatory datasets

structured data feeds

embedded JSON

pagination APIs

other authoritative public datasets

Future architecture should continue to normalize these into the same evidence system:

Web evidence
Structured API
Regulatory dataset
External feed
       ↓
Normalized evidence + provenance
       ↓
Validation / extraction
       ↓
Canonical knowledge
APIs should enrich the evidence architecture, not bypass it.

5. Productise the Intelligence
The current Flask / Jinja UI is operational but not yet the final intelligence product.

The next significant UX redesign should be built around:

WHAT CHANGED?
      ↓
WHO DROVE IT?
      ↓
WHAT EVENTS CAUSED IT?
      ↓
WHY SHOULD I TRUST IT?
      ↓
SHOW ME THE EVIDENCE
High-value product surfaces include:

intelligence overview

signal cards

trend visualisation

investor comparison

sector exploration

corpus observability

event and evidence drill-down

A React rewrite is not a prerequisite.

Flask / Jinja should remain until interaction complexity demonstrates a genuine need for a different frontend architecture.

6. Product Validation
Engineering and product validation should increasingly run in parallel.

Potential users include:

venture investors

growth investors

corporate venture teams

LP / fund-of-funds intelligence teams

strategy teams

market-intelligence teams

ecosystem researchers

Validation should use real intelligence tasks, for example:

How is a specific investor's behaviour changing?

Which investors are increasing activity?

Which sectors show increasing participation?

Who is becoming more active at a particular stage?

Which investors are changing strategy?

Which signals are worth monitoring?

Important questions are:

What do users repeatedly investigate?

What is difficult to answer elsewhere?

Which signals cause further investigation?

What would users want monitored continuously?

What would they value knowing sooner or with stronger evidence?

Future workflow features should emerge from these answers.

Future Capabilities
Capabilities that may become valuable after the core intelligence product is validated include:

broader venture-event types

structured and regulatory enrichment

cross-source evidence reconciliation

changing syndicates

investor convergence

geographic momentum

capital-formation signals

fund-level intelligence

richer search

saved investigations

watchlists

alerts

recurring intelligence briefs

graph / relationship exploration

deployed continuous operation

These are directions, not commitments.

They should be earned by product value or demonstrated engineering constraints.

Development Principles
1. Information acquisition → structure → intelligence → user value
Every major capability should strengthen this progression.

2. News is evidence
Articles and announcements are raw material, not the final product.

3. Canonical truth is earned
Probabilistic extraction should not automatically become canonical knowledge.

4. Preserve provenance
Important conclusions should remain traceable to evidence.

5. Measurement before interpretation
The system should establish what changed before trying to explain what it means.

6. LLMs understand; deterministic systems govern
LLMs are useful for interpreting unstructured evidence.

Deterministic systems should own:

workflow state

persistence

identity

validation

canonicalization

constraints

aggregation

confidence

measurement

7. Prefer ambiguity over false certainty
Incorrect canonical knowledge contaminates every downstream intelligence layer.

8. Measure the observed universe
Never imply that Vantage's corpus is the entire market.

9. Comparable evidence before behavioural claims
Changes in observation coverage must not masquerade as changes in investor or market behaviour.

10. Configuration before bespoke integrations
Improve reusable acquisition mechanisms rather than accumulating one-off scrapers.

11. Fix failure classes, not isolated records
Let scale reveal recurring weaknesses.

Repair them when they threaten integrity or improve a reusable capability.

12. Manual review is an exception path
Human review should reveal where the system needs improvement.

It should not become the operating model.

13. Frameworks must earn their complexity
Adopt frameworks when they remove substantial generic complexity or solve a demonstrated constraint.

Do not add them because sophisticated systems are expected to use them.

14. Tests must prove behaviour, not merely pass
A large green test suite is useful only if meaningful regressions cause tests to fail.

Critical paths should increasingly be tested through invariants, negative cases and end-to-end regression evidence.

15. Protect the accumulated corpus
The historical evidence and knowledge graph are core project assets.

Data durability matters independently of code durability.

16. Product validation belongs beside engineering
Technical sophistication without useful intelligence is not success.

What Not to Build Yet
Deliberately avoid:

source expansion merely to increase source count

scraper-per-site architecture

universal crawling

headless-browser infrastructure without a demonstrated source need

historical processing merely to clear every backlog

validators or parsers for isolated one-off anomalies

a giant generic event ontology before domain grounding

opaque AI-generated trend scores

LLM-generated market conclusions without deterministic measurements

frontend framework rewrites purely for polish

PostgreSQL migration for appearance rather than need

premature Docker / deployment complexity

Celery / Redis without a real job-processing constraint

Kafka or elaborate event buses

microservices

Kubernetes

vector databases without a demonstrated retrieval requirement

agent frameworks without a demonstrated agentic workflow

orchestration frameworks before local fleet operation becomes a real operational constraint

infrastructure because "real startups use it"

Technical sophistication is not the product.

Technical Direction
Current core technologies include:

Python

Flask

Jinja

SQLAlchemy

SQLite

Flask-Migrate / Alembic

OpenAI structured extraction

Pydantic

BeautifulSoup

feedparser

requests

pytest

HTML / CSS

Much of the observation and knowledge system can also be operated through the flask --app app vantage ... CLI.

The current development loop remains intentionally simple:

edit
 ↓
test
 ↓
run
 ↓
measure
 ↓
inspect
That speed is valuable.

Infrastructure should solve demonstrated constraints rather than anticipated ones.

Possible future transitions include:

SQLite
   ↓
PostgreSQL
when durability, concurrency, deployment or workload requires it.

Manual / local operation
   ↓
Scheduled or orchestrated operation
when continuous execution becomes a genuine requirement.

Current server-rendered UI
   ↓
Richer frontend architecture
only when product interaction complexity earns it.

Brief History
1. News Aggregator
Vantage began as a straightforward Flask application:

RSS
 ↓
Articles
 ↓
Searchable news feed
The article was effectively the product.

2. Structured Venture Data
LLM extraction shifted the system toward:

Evidence
   ↓
Companies
Investors
Funding rounds
Funds
Fund closes
News became input rather than output.

3. Canonical Knowledge
As data accumulated, duplication and identity became more important than extracting another article.

The architecture evolved from:

1 article → 1 record
toward:

many observations → one real-world event
Entity resolution, aliases, event reconciliation and multi-source evidence became foundational.

4. Source Platform
Observation expanded beyond a small set of editorial RSS feeds.

Reusable RSS, sitemap and HTML discovery, a canonical registry, historical operation, fleet execution and source measurement moved Vantage away from bespoke scraping.

5. Investor Behaviour
First-party investor history shifted the core question from:

What happened?

to:

What did this investor do?

and then:

How is that behaviour changing?

Investor profiles, temporal comparisons and corpus-qualified confidence followed.

6. Safe Knowledge at Scale
As the corpus grew, allowing probabilistic extraction to write directly into canonical truth became too risky.

Vantage introduced the durable boundary:

Evidence
 ↓
Versioned Extraction
 ↓
Validation
 ↓
Safe Promotion
 ↓
Canonical Knowledge
7. Market Intelligence
The next conceptual transition was from individual investor intelligence to cross-investor behavioural measurement.

Comparable cohorts and Sector Momentum V1 established the first market-level signal architecture.

The project is now moving from:

Can Vantage build structured venture knowledge?

toward:

Can Vantage safely turn accumulated historical knowledge into intelligence that professional users care about?

What Success Looks Like
Vantage succeeds if it becomes a system that can reliably:

Observe venture activity
        ↓
Preserve the evidence
        ↓
Resolve real entities and events
        ↓
Build trustworthy history
        ↓
Measure behavioural change
        ↓
Surface meaningful signals
        ↓
Explain exactly why they exist
        ↓
Help users decide what to investigate or monitor
A successful Vantage is not the system with the most sources, the most infrastructure or the most AI.

It is the system where a user can ask:

What is changing in the venture ecosystem, who is driving it, and why should I believe it?

and receive an answer that is useful, inspectable and grounded in evidence.