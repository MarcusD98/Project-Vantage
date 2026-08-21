# Project Vantage

**Project Vantage** is a venture intelligence system that continuously observes public venture-market activity, converts it into structured historical knowledge, and uses that history to understand how investors, companies, sectors, stages, and markets are changing over time.

Vantage began as a simple Python/Flask VC news aggregator.

It is evolving into an evidence-backed **venture intelligence platform**.

```text
Public venture ecosystem
        ↓
Source network
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
```

The core idea is:

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

News articles, investor announcements, company posts, fund announcements, ecosystem publications and other public information are **evidence** from which Vantage builds a structured model of the venture ecosystem.

---

# Product Thesis

Private-market intelligence is already a large and competitive category.

Platforms such as PitchBook, Dealroom, CB Insights, Harmonic and others provide increasingly sophisticated company, investor and market data.

Vantage should not attempt to win primarily by becoming another static company database.

The more interesting thesis is:

> **Continuously observe what important participants in the venture ecosystem are actually doing, turn those observations into structured historical knowledge, and identify meaningful changes in behaviour over time.**

Conceptually:

```text
LIVE PUBLIC INFORMATION

Publications
Investor websites
Company announcements
Fund announcements
Accelerators
Ecosystem sources
Selected structured sources
        ↓
Evidence acquisition
        ↓
AI understanding
        ↓
Canonical knowledge
        ↓
Historical behaviour
        ↓
Change over time
        ↓
Venture intelligence
```

The system increasingly begins from:

> **What are important venture-market participants actually doing?**

and aims to answer:

> **How is that behaviour changing, who is driving the change, and what might that tell us about the market?**

---

# Strategic Wedge: Investor Behaviour

The first major intelligence wedge is investor behaviour.

Vantage should answer questions such as:

```text
What are investors investing in?

What are they leading?

Which sectors are they entering?

Which stages are they targeting?

Where are they investing?

Who are they investing alongside?

How active are they?

How is that changing over time?
```

Different evidence types provide different perspectives.

```text
Editorial source
    ↓
"What became news?"

Investor first-party source
    ↓
"What did this investor choose to do?"

Company source
    ↓
"What did the company announce?"
```

Together:

```text
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
```

---

# Where Vantage Could Be Different

The opportunity is not simply:

> Build a better startup database.

The more differentiated product direction is:

> **Treat the venture ecosystem as a continuously observed behavioural system.**

Instead of asking only:

```text
Which companies exist?
```

Vantage should increasingly answer:

```text
Where is investor behaviour changing?

Which sectors are attracting new conviction?

Which investors are accelerating or retreating?

Where are lead-investor patterns changing?

Which investor groups are converging around the same themes?

What underlying events prove that?
```

For example:

```text
Observed European defence activity
increased materially over the last six months
        ↓
More tracked investors participated
        ↓
Lead activity increased
        ↓
Financing frequency increased
        ↓
Specific investors drove the change
        ↓
Canonical financing events
        ↓
Underlying evidence
```

This evidence chain is central:

```text
Signal
  ↓
Measurement
  ↓
Behaviour
  ↓
Canonical event
  ↓
Evidence
```

The goal is not:

> "AI says defence is hot."

The goal is:

> **Here is the measurable behavioural change, who caused it, the events behind it, and the evidence supporting those events.**

---

# Product Architecture

Vantage has four connected layers.

## 1. Observation

Understand:

> **What is happening?**

Responsibilities include:

- discovering public venture information
- operating many sources through reusable mechanisms
- normalizing evidence
- preserving provenance
- retrieving underlying content
- filtering noise
- building historical coverage
- monitoring source health

Current reusable discovery mechanisms include:

```text
RSS
Sitemap
HTML listing
```

The objective is not simply to ingest more URLs.

It is to build a useful **observable venture universe**.

---

## 2. Structured Knowledge

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
- Canonical identities
- Historical activity

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
Evidence
```

The target relationship is:

```text
many observations
        ↓
one real-world event
```

rather than:

```text
many observations
        ↓
many duplicated database records
```

---

## 3. Behavioural Intelligence

Understand:

> **How is behaviour changing?**

The current knowledge graph can support investor-level analysis including:

- observed investment activity
- lead-investor activity
- stage exposure
- sector exposure
- geography where coverage supports it
- co-investors
- financing-round volume participated in
- recent investments
- current vs previous time windows
- confidence-qualified trend signals

Example:

```text
ACCEL

Current 365D       Previous 365D

22 investments     11 investments
17 leads             8 leads

        ↓

Observed activity increased

        ↓

CORPUS-SUPPORTED
```

All intelligence should remain traceable to canonical events and underlying evidence.

---

## 4. Market Intelligence

The next major product layer aggregates behaviour across many participants.

Potential signal categories include:

- sector momentum
- stage shifts
- geographic momentum
- investor strategy changes
- funding acceleration
- changing syndicates
- changing lead behaviour
- increasing investor conviction
- capital-formation cycles
- emerging themes

Static profiles are useful.

Behavioural change is more valuable.

---

# Evidence-Backed Intelligence

Inspectability is a core product principle.

A user should be able to move from:

```text
Observed European defence activity is increasing.
```

to:

```text
Why?
```

and inspect:

- which investors changed behaviour
- which financing events contributed
- which companies were involved
- which periods changed
- which sources support those events
- which evidence was editorial
- which evidence was first-party

The principle is:

> **Inspectable intelligence, not unexplained conclusions.**

---

# Current System

The current architecture is approximately:

```text
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
                 HISTORICAL ACTIVITY
                          │
                          ▼
                    INTELLIGENCE
```

This architecture has now been proven sufficiently to expose the next scaling constraint.

---

# The Next Architectural Step

Today, extraction and canonical persistence are still relatively tightly coupled.

Conceptually:

```text
Evidence
   ↓
LLM extraction
   ↓
Canonical database
```

This works well at small scale.

It becomes dangerous as evidence volume grows.

If a small percentage of extractions contain subtle errors, directly promoting every extraction into canonical truth eventually creates a manual-cleaning problem.

The next target architecture is therefore:

```text
RAW EVIDENCE
     ↓
VERSIONED EXTRACTION
     ↓
AUTOMATED VALIDATION
     ↓
EVENT CANDIDATE
     ↓
CANONICALIZATION
     ↓
KNOWLEDGE GRAPH
     ↓
INTELLIGENCE
```

A lightweight intermediate object such as an `ExtractionRecord` or `EventCandidate` should represent:

```text
What did the extractor think?
```

before Vantage decides:

```text
What do we accept as canonical truth?
```

Conceptually:

```text
ExtractionRecord

article_id
event_type
payload

extractor_version
model

validation_state
validation_flags

created_at
processed_at
```

This enables:

- versioned extraction
- automated validation
- quarantine
- replay / reprocessing
- comparison between extractor versions
- selective promotion
- safer bulk processing
- lower dependence on manual cleanup

The objective is not zero errors.

The objective is:

> **Errors become observable, quarantinable and reprocessable without contaminating canonical truth.**

---

# Source Platform

Vantage already operates sources through a configuration-first source registry.

A source conceptually defines:

```text
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
```

Supported source types include:

```text
publication
investor
ecosystem
company
structured
```

Supported discovery mechanisms include:

```text
rss
sitemap
html
```

The operating principle is:

> **Adding source #50 should normally require configuration, not new application logic.**

Vantage should avoid becoming:

```text
accel_scraper.py
sequoia_scraper.py
index_scraper.py
techcrunch_scraper.py
...
```

New acquisition mechanisms should normally be introduced only when they generalize across multiple valuable sources.

---

# Fleet Operations

The source platform can operate groups of sources rather than individual source scripts.

Fleet operations support concepts such as:

- source selection by type
- source selection by name
- incremental discovery
- historical discovery
- isolated source failures
- persistent run telemetry
- aggregated run statistics
- optional downstream processing

The principle is:

> **A failing source should not stop the network.**

---

# Source Measurement

Vantage measures both source health and contribution.

Useful questions include:

```text
Which sources are healthy?

Which sources repeatedly fail?

Which sources produce useful evidence?

Which sources contribute unique events?

Which sources mainly corroborate existing events?

Which sources deserve further engineering effort?
```

The goal is not:

> Support every source.

The goal is:

> **Build a source network whose combined observations materially improve the venture knowledge base.**

---

# Scaling Strategy

Vantage should now scale by cohorts rather than source-by-source refinement.

Instead of:

```text
Add investor
    ↓
Test investor
    ↓
Fix investor
    ↓
Add next investor
```

the target approach is:

```text
Large candidate source cohort
        ↓
Run through generic platform
        ↓
Measure compatibility
        ↓
Keep productive sources
        ↓
Ignore low-value failures
        ↓
Fix only recurring systemic problems
```

A result such as:

```text
75 candidate sources

50 work generically
12 work partially
13 unsupported
```

can still represent a successful platform.

Unsupported websites should not automatically trigger bespoke scraper development.

A useful future observation cohort might include approximately:

```text
30–50 investors
15–25 publications
10–20 ecosystem / company / accelerator sources
```

The exact number is not important.

The purpose is to expose the next systemic bottlenecks while rapidly expanding the observable venture universe.

---

# Historical Coverage

Behavioural intelligence requires history.

The objective is not to build a perfect historical archive of the internet.

The more strategically valuable asset is:

> **A historical record of what important venture-market participants actually did.**

For strategically important investors, a useful target is:

```text
12 months minimum
        ↓
24 months where practical
```

Historical completeness should always be described relative to the **discovered Vantage corpus**, not as complete knowledge of all real-world investment activity.

---

# Confidence

Vantage measures an observed subset of the venture ecosystem.

It should therefore explicitly distinguish:

```text
Observed activity
```

from:

```text
Total market activity
```

Investor trend confidence currently follows concepts such as:

```text
CORPUS-SUPPORTED
```

Enough observations exist and the relevant discovered first-party comparison corpus has been processed.

```text
OBSERVATIONAL
```

Enough observations exist for a trend, but equivalent temporal first-party coverage is unavailable or incomplete.

```text
INSUFFICIENT
```

There is not enough evidence for a reliable comparison.

Crucially:

> **Corpus-supported does not mean complete knowledge of every investment made by an investor.**

It describes the quality of Vantage's observed corpus.

---

# Integrity Philosophy

Vantage has accumulated reusable safeguards around:

- entity normalization
- entity aliases
- canonical entity resolution
- canonical event resolution
- multi-source evidence
- stage normalization
- sector normalization
- source-aware extraction
- historical reconciliation
- multi-event safety
- multi-round review
- source provenance
- confidence semantics
- human review of ambiguity

The governing principle is:

> **Ambiguity is preferable to confidently wrong canonical data.**

But Vantage should not become a manual-cleaning operation.

The development rule going forward is:

> **Fix recurring classes of failure, not isolated records.**

If one record is wrong, record it.

If the same failure repeatedly appears and threatens downstream intelligence, improve the machine.

Manual review should teach us where the architecture needs improvement.

It should not become the architecture.

---

# Current Product Surfaces

The Flask application currently exposes several views into the venture graph.

## Evidence

Search and inspect discovered public evidence.

## Funding

Browse structured financing events.

## Companies

Inspect company metadata and funding history.

## Investor Intelligence

Inspect:

- observed activity
- behaviour changes
- confidence
- stage patterns
- sector patterns
- geographic coverage
- lead behaviour
- co-investors
- recent investments
- evidence history

## Sources

Inspect source health and contribution.

## Data Quality

Inspect resolution and integrity issues.

## Intelligence

View early aggregate venture activity.

These increasingly represent interfaces into the underlying knowledge graph rather than isolated article pages.

---

# Startup Thesis

Vantage is currently best described as:

> **A credible startup thesis backed by a working technical prototype, not yet a validated business.**

The technical question:

> Can this system observe public venture activity and turn it into structured behavioural intelligence?

has been substantially de-risked.

The larger remaining question is:

> **Can Vantage produce intelligence sufficiently differentiated and useful that professional investors change how they work and pay for it?**

That cannot be answered by engineering alone.

---

# Potential Users

Possible initial users include:

- venture investors
- growth investors
- corporate venture teams
- fund-of-funds and LP intelligence teams
- market intelligence teams
- strategy teams
- ecosystem researchers

The exact initial customer profile remains to be validated.

---

# Customer Discovery

Customer discovery should now run alongside engineering.

The objective is not to ask:

> "Would you use Vantage?"

Instead, users should be shown real intelligence and asked to perform real work.

Examples:

```text
Understand how Sequoia's activity is changing.

Find investors increasing exposure to defence.

Identify investors becoming more active at Series A.

Understand who is driving AI infrastructure activity.

Find emerging co-investment relationships.
```

The important questions are:

```text
What do users repeatedly investigate?

Which information is difficult to get elsewhere?

Which signals cause them to ask for more?

What would they want monitored automatically?

What would they pay to have continuously?
```

Product development should increasingly be informed by these workflows.

---

# Potential Moat

The codebase itself is unlikely to become the primary moat.

A sophisticated competitor could reproduce much of the software architecture.

Potential defensibility compounds through:

```text
Source network
        +
Historical evidence corpus
        +
Canonical entity graph
        +
Canonical event graph
        +
Provenance
        +
Behavioural history
        +
Signal methodology
        +
Customer workflow
```

The key asset is the **data-producing machine and the historical knowledge it accumulates**.

A system that has continuously observed and resolved venture activity for years becomes substantially harder to recreate than its individual Python services.

The flywheel is:

```text
More sources
    ↓
More observations
    ↓
More canonical history
    ↓
Better behavioural baselines
    ↓
Better signals
    ↓
More useful workflows
    ↓
More product learning
```

---

# What Would Validate the Business?

Engineering progress alone does not validate the company.

More meaningful milestones would look like:

```text
Serious users repeatedly use the product
        ↓
They rely on specific intelligence workflows
        ↓
They return without prompting
        ↓
They ask for alerts / search / monitoring
        ↓
Someone pays
        ↓
Customers retain and expand usage
```

The largest risk is no longer:

> Can we build the system?

The larger risk is:

> **Can we make it sufficiently differentiated that someone cares enough to change their workflow?**

---

# Technology

Vantage deliberately remains technically lightweight.

Current core technologies include:

- Python
- Flask
- Jinja
- SQLAlchemy
- SQLite
- Flask-Migrate / Alembic
- OpenAI API
- Pydantic
- BeautifulSoup
- feedparser
- requests
- pytest
- HTML / CSS

The application currently runs locally and much of the knowledge-building pipeline is operated through Flask CLI commands.

---

# Infrastructure Philosophy

Infrastructure should solve real constraints rather than anticipated ones.

The current development loop is intentionally simple:

```text
edit
 ↓
pytest
 ↓
run
 ↓
inspect
```

That speed is valuable.

Vantage should **not** move to PostgreSQL, Docker, workers or more complex infrastructure simply because a mature production system might eventually use them.

Potential future progression:

```text
SQLite
   ↓
PostgreSQL
```

when requirements such as:

- concurrent writes
- background workers
- database locking
- substantially larger workloads
- multi-user deployment

justify it.

Likewise:

```text
Local execution
   ↓
Scheduled execution
```

when continuous observation becomes operationally necessary.

And:

```text
Local environment
   ↓
Docker
```

when reproducible deployment materially helps development or operation.

CI may provide value earlier than Docker because automated regression testing directly protects the development cycle.

Flask itself is not currently a scaling problem.

Vantage does **not** need premature:

- Kubernetes
- microservices
- complex distributed systems
- elaborate event buses
- vector databases
- agent frameworks

Technical sophistication is not the product.

---

# Brief History

Vantage has evolved through several distinct ideas.

## 1. VC News Aggregator

The original project was:

```text
RSS
 ↓
Articles
 ↓
Searchable news feed
```

The article was the product.

---

## 2. Structured Venture Database

LLM extraction introduced:

```text
Articles
   ↓
Companies
Investors
Funding rounds
Funds
Fund closes
```

The project shifted from reading news toward structuring venture activity.

---

## 3. Canonical Knowledge

As data accumulated, the challenge became identity and event integrity.

The architecture evolved from:

```text
1 article
→
1 record
```

toward:

```text
many evidence documents
→
1 real-world event
```

Entity resolution, aliases, event resolution, taxonomy normalization and multi-source evidence became foundational.

---

## 4. Source Platform

Discovery expanded beyond editorial RSS into:

```text
RSS
Sitemaps
HTML listings
```

A canonical source registry and fleet operations proved that sources could increasingly be onboarded through reusable infrastructure rather than bespoke scrapers.

---

## 5. Historical Investor Intelligence

First-party investor history allowed Vantage to begin asking:

```text
What did this investor actually do?
```

and then:

```text
How has that behaviour changed?
```

Time-window comparison, confidence semantics and investor intelligence followed.

---

## 6. Current Stage — Scale the Machine

The core concept now works.

The question is no longer:

> Can Vantage understand another venture article?

It is:

> **Can Vantage safely process large volumes of evidence across a broad source network and continuously turn that activity into differentiated intelligence?**

That is the current focus.

---

# Roadmap

## Phases 1–4 — Observation & Knowledge Foundation

**Status: Complete**

Established:

- evidence ingestion
- normalized evidence
- structured extraction
- company / investor / fund entities
- funding rounds
- fund closes
- canonical entity resolution
- canonical event resolution
- multi-source evidence
- RSS / sitemap / HTML discovery
- provenance
- historical operations
- integrity tooling

---

## Phase 5 — Source Platform V1

**Status: Complete**

Established:

- canonical source registry
- incremental / historical modes
- configuration validation
- fleet operations
- source-type selection
- failure isolation
- persistent source-run telemetry
- source measurement
- source-network scale testing

---

## Phase 6 — Investor Intelligence V1

**Status: Complete / MVP established**

Established:

- durable investor identity
- observed investment activity
- lead activity
- stage exposure
- sector exposure
- geographic coverage
- co-investors
- current vs previous periods
- confidence-gated signals
- temporal corpus confidence
- evidence-backed investor UI
- multi-round integrity safeguards
- source-aware first-party extraction

The objective is now to stop optimizing individual investor records and scale the machine.

---

# Phase 7 — Scalable Knowledge Pipeline

**Status: Next**

## 7.1 — Versioned Extraction

Introduce a durable intermediate representation between evidence and canonical events.

```text
Evidence
  ↓
ExtractionRecord
  ↓
Validation
  ↓
Canonical event
```

## 7.2 — Automated Validation & Quarantine

Classify extracted candidates into:

```text
PROMOTE
REVIEW
REJECT
```

Build reusable validation around:

- internal extraction consistency
- conflicting event attributes
- source perspective
- investor / lead relationships
- multi-event risk
- event completeness

## 7.3 — Reprocessing

Allow stored evidence to be safely re-extracted when:

- prompts improve
- models improve
- schemas evolve
- validators improve

Canonical history should not require manual reconstruction whenever extraction improves.

---

# Phase 8 — Observation & Historical Scale

Operate significantly larger source cohorts.

Target direction:

```text
30–50 investors
15–25 publications
10–20 ecosystem / company / accelerator sources
```

Build useful matched historical coverage across a broader strategically important investor cohort.

Measure:

- source reliability
- event yield
- unique contribution
- evidence overlap
- extraction quality
- historical completeness
- review rate

Let scale expose the next systemic problems.

---

# Phase 9 — Market & Signal Intelligence

Aggregate behaviour across the venture graph.

Potential signals:

- sector momentum
- stage shifts
- geographic momentum
- funding acceleration
- investor strategy drift
- changing lead activity
- co-investment changes
- increasing investor participation
- emerging themes

Initial signals should remain transparent.

Example:

```text
Current 180D
vs
Previous 180D
```

with drill-down:

```text
Signal
 ↓
Investors
 ↓
Companies
 ↓
Events
 ↓
Evidence
```

---

# Phase 10 — Search, Discovery & Workflow

Turn the graph into a directly explorable intelligence product.

Potential questions:

```text
European defence startups

AI infrastructure companies in Germany

Seed rounds above $5M

Fintech investors active at Series A

Companies backed by both Accel and Sequoia

Investors increasingly active in robotics

Most active European seed investors

Investors whose sector exposure changed materially
over the past six months
```

Eventually Vantage may support:

- structured search
- saved searches
- watchlists
- alerts
- recurring intelligence briefs
- investor comparison
- sector monitoring

These workflows should be shaped by real customer discovery rather than assumed upfront.

---

# Productionization — When Required

Production infrastructure is a **cross-cutting concern**, not the current product objective.

Introduce components only when demonstrated requirements justify them.

Possible progression:

- configurable database URL
- CI
- scheduled ingestion
- PostgreSQL
- background processing
- Docker
- deployment
- backups
- monitoring
- secret management

The order should be determined by actual bottlenecks.

---

# Development Principles

## 1. Information acquisition → structure → intelligence

Every major capability should strengthen this progression.

## 2. News is evidence

The article is raw material, not the final product.

## 3. Build the machine, not individual integrations

A fix is most valuable when it improves the platform.

## 4. Configuration before bespoke code

New sources should normally require configuration.

## 5. Use LLMs for semantic understanding

LLMs interpret unstructured evidence.

Deterministic systems should own:

- persistence
- state
- identity
- constraints
- validation
- matching
- canonicalization
- aggregation

## 6. Preserve provenance

Every conclusion should remain traceable to evidence.

## 7. Prefer ambiguity over false certainty

Incorrect canonical data contaminates downstream intelligence.

## 8. Measure the observed universe

Do not confuse observed activity with total market activity.

## 9. Let scale expose systemic problems

Do not continually hunt isolated imperfections.

Fix problems when:

```text
they recur
+
they threaten integrity
+
the fix strengthens the platform
```

## 10. Accept imperfect source coverage

A valuable network matters more than universal compatibility.

## 11. Manual review is an exception path

Human review should improve the machine, not become the machine.

## 12. Protect development speed

Do not introduce infrastructure that materially slows iteration without solving a real constraint.

## 13. Validate the product alongside the technology

Engineering proves what can be built.

Users determine what is valuable.

---

# What Not to Build Yet

Avoid premature work on:

- perfect publication archives
- scraper-per-site architecture
- universal crawling
- opaque AI scores
- complex recommendation systems
- React rewrites
- microservices
- Kubernetes
- large distributed infrastructure
- unnecessary ontology complexity
- infrastructure introduced only because "real startups use it"

---

# Current Priority

The immediate engineering objective is:

> **Turn Vantage's proven ingestion and knowledge-building pipeline into a scalable, versioned knowledge system that can safely process a much larger evidence corpus.**

In parallel:

> **Begin validating whether behavioural venture intelligence solves sufficiently important real-world workflows to support a commercial product.**

The next progression is:

```text
VERSIONED EXTRACTION
        ↓
AUTOMATED VALIDATION
        ↓
SAFE CANONICALIZATION
        ↓
LARGER SOURCE NETWORK
        ↓
MORE HISTORICAL BEHAVIOUR
        ↓
CROSS-INVESTOR SIGNALS
        ↓
SEARCH / MONITORING WORKFLOWS
        ↓
VENTURE INTELLIGENCE
```

The core engineering question is no longer:

> Can Vantage process this article?

It is:

> **Can Vantage continuously observe the venture ecosystem at scale and turn that activity into trustworthy, inspectable intelligence?**

The core product question is:

> **Can that intelligence reveal something valuable enough that professional users change how they work?**

That is what Vantage now needs to prove.