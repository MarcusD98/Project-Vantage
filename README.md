# Project Vantage

**Project Vantage** is an evidence-backed venture intelligence system.

It continuously observes public venture-market activity, converts those observations into structured historical knowledge, and uses that history to understand how investors, companies, sectors, stages, and markets are changing over time.

Vantage began as a simple Python / Flask VC news aggregator.

It is evolving into a system for answering a much more interesting question:

> **What are important participants in the venture ecosystem actually doing, how is that behaviour changing, and what might that tell us about the market?**

The core progression is:

```text
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
```

Or more simply:

> **Information acquisition → structure → intelligence**

News is not the product.

Articles, investor announcements, company posts, fund announcements, ecosystem publications and other public information are **evidence** from which Vantage builds a structured model of venture activity.

---

# Product Thesis

Private-market intelligence is already a large and competitive category.

Platforms such as PitchBook, Dealroom, CB Insights, Harmonic and others provide increasingly sophisticated company, investor and market data.

Vantage should not try to win primarily by becoming another static startup database.

The more differentiated thesis is:

> **Treat the venture ecosystem as a continuously observed behavioural system.**

Rather than asking only:

```text
Which companies exist?
Who invested in them?
```

Vantage should increasingly answer:

```text
Where is investor behaviour changing?

Which investors are accelerating or retreating?

Which sectors are attracting new conviction?

Where is lead-investor activity changing?

Which stages are becoming more active?

Which investor groups are converging around the same themes?

What real-world events prove those changes?
```

The goal is not:

> "AI says defence is hot."

The goal is:

> **Here is the measurable change, who drove it, the events behind it, and the evidence supporting those events.**

That evidence chain is fundamental:

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

---

# Strategic Wedge: Investor Behaviour

The first major intelligence wedge is **investor behaviour**.

Vantage should help answer:

- What are investors investing in?
- What are they leading?
- Which sectors are they entering or leaving?
- Which stages are they targeting?
- Where are they investing?
- Who are they investing alongside?
- How active are they?
- How is that behaviour changing over time?

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

The first-party investor corpus is particularly valuable because it helps Vantage build a historical record of what strategically important investors actually chose to do.

---

# The Core Asset

The primary asset Vantage is trying to build is not a collection of articles.

It is not even simply a database of companies and investors.

It is:

> **A trustworthy historical activity graph of the observed venture ecosystem.**

That graph connects:

```text
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
```

As that history accumulates, Vantage can establish behavioural baselines and measure change against them.

This is what makes continuous observation strategically important.

A system that has reliably observed and resolved venture activity for years becomes substantially harder to recreate than the individual Python services that operate it.

---

# Product Architecture

Vantage has four connected product layers.

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
- recovering historical evidence
- monitoring source health and contribution

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

The target relationship is:

```text
many observations
        ↓
one real-world event
```

For example:

```text
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
```

This is fundamentally different from:

```text
3 articles
   ↓
3 duplicated funding-round records
```

---

## 3. Behavioural Intelligence

Understand:

> **How is behaviour changing?**

The current graph supports investor-level analysis including:

- observed investment activity
- lead activity
- stage exposure
- sector exposure
- geographic exposure where coverage supports it
- co-investors
- financing-round participation
- recent investments
- current vs previous time periods
- confidence-qualified trends

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

The next major analytical layer aggregates behaviour across many participants.

Potential signal categories include:

- sector momentum
- stage shifts
- geographic momentum
- investor strategy changes
- funding acceleration
- changing syndicates
- changing lead behaviour
- increasing investor participation
- capital-formation cycles
- emerging themes

Static profiles are useful.

**Behavioural change is more valuable.**

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
- which time periods changed
- which sources support those events
- which evidence was editorial
- which evidence was first-party

The principle is:

> **Inspectable intelligence, not unexplained conclusions.**

---

# Current System

Vantage already has a functioning observation and knowledge platform.

The current system is approximately:

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
                    INTELLIGENCE
```

This architecture has been proven sufficiently to expose the next important constraint.

---

# Current Architectural Constraint

Today, extraction and canonical persistence are still too tightly coupled.

Conceptually:

```text
Evidence
   ↓
LLM extraction
   ↓
Canonical database
```

This works at small scale.

It becomes increasingly dangerous as evidence volume grows.

Even a low extraction error rate becomes expensive when every accepted extraction can immediately influence:

- canonical entities
- canonical events
- company metadata
- investor relationships
- lead relationships
- historical activity
- downstream intelligence

At larger scale, the system cannot depend on repeatedly discovering and manually repairing bad canonical records.

The next architecture therefore introduces a durable boundary between:

```text
What did the extractor think?
```

and:

```text
What does Vantage accept as canonical truth?
```

---

# Target Knowledge Pipeline

The target architecture is:

```text
RAW EVIDENCE
     ↓
VERSIONED EXTRACTION
     ↓
AUTOMATED VALIDATION
     ↓
CANDIDATE STATE
     ↓
CANONICALIZATION
     ↓
KNOWLEDGE GRAPH
     ↓
INTELLIGENCE
```

The first durable intermediate object is an `ExtractionRecord`.

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
validator_version

created_at
validated_at
promoted_at
```

An extraction record represents:

> **What one specific version of the extraction system believed about one piece of evidence.**

Extraction records should be append-oriented.

Re-running an article using a newer extractor should create a new extraction record rather than overwrite the old one.

For example:

```text
Article #817
   │
   ├── funding-v1
   │      ↓
   │   ExtractionRecord #1201
   │      ↓
   │    REVIEW
   │
   └── funding-v2
          ↓
       ExtractionRecord #1844
          ↓
        PROMOTE
          ↓
     Canonical event
```

This creates a durable history of machine interpretation.

---

# Validation and Promotion

Not every extraction should automatically become canonical truth.

Validated extraction records should initially move into one of three states:

```text
PROMOTE
REVIEW
REJECT
```

### PROMOTE

The extraction is sufficiently consistent and complete to enter canonicalization.

### REVIEW

The extraction may be valid but contains ambiguity or risk that should prevent automatic promotion.

### REJECT

The extraction is not suitable for canonicalization.

Initial deterministic validation should focus on recurring integrity risks such as:

- internal extraction consistency
- required event identity
- event completeness
- invalid or implausible values
- source perspective
- investor / lead-investor consistency
- multi-event ambiguity
- conflicting event attributes
- compound funding evidence
- unsupported relationships

The goal is not to construct a universal rules engine.

The goal is to intercept recurring classes of error before they contaminate canonical knowledge.

---

# Replay and Reprocessing

Stored evidence should be safely reprocessable.

Re-extraction should be possible when:

- prompts improve
- models improve
- extraction schemas evolve
- validators improve
- integrity rules improve

Conceptually:

```text
Stored evidence
      ↓
Extractor v1
      ↓
Candidate rejected
      ↓

Extractor improves

      ↓
Extractor v2
      ↓
New ExtractionRecord
      ↓
Validated
      ↓
Promoted
```

Canonical history should not require manual reconstruction every time the extraction layer improves.

This is a major objective of the scalable knowledge pipeline.

---

# Knowledge Pipeline Measurement

The knowledge pipeline should become measurable in the same way the source platform is measurable.

Useful metrics include:

- extraction attempts by version
- successful extraction rate
- validation outcome rates
- promotion rate
- review rate
- rejection rate
- validation flags by frequency
- canonical event yield
- reprocessing outcomes
- source-level extraction quality
- extractor-version comparison

The purpose is to answer questions such as:

```text
What fails repeatedly?

Which errors matter?

Which source types produce the most ambiguity?

Did extractor v2 improve promotion quality?

Which validation rule catches the most dangerous failures?

Where should engineering effort go next?
```

The principle remains:

> **Fix recurring classes of failure, not isolated records.**

---

# Source Platform

Vantage operates sources through a configuration-first source registry.

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

Supported discovery mechanisms currently include:

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

New acquisition mechanisms should normally be introduced only when they generalize across multiple strategically useful sources.

---

# Fleet Operations

The source platform can operate groups of sources rather than individual scripts.

Fleet operations support:

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

Vantage measures both source health and source contribution.

Useful questions include:

```text
Which sources are healthy?

Which sources repeatedly fail?

Which sources produce useful evidence?

Which sources contribute unique events?

Which sources mainly corroborate existing events?

Which sources deserve additional engineering effort?
```

The objective is not:

> Support every source on the internet.

It is:

> **Build a source network whose combined observations materially improve the venture knowledge graph.**

---

# Scaling Strategy

Vantage should scale by **cohorts**, not by endlessly perfecting one source at a time.

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
Large candidate cohort
        ↓
Run through generic platform
        ↓
Measure compatibility
        ↓
Keep productive sources
        ↓
Identify recurring failures
        ↓
Fix systemic problems
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

The purpose of scale is to expose the next systemic bottlenecks while expanding the observable venture universe.

---

# Historical Coverage

Behavioural intelligence requires history.

The objective is not to construct a perfect archive of the internet.

The strategically useful asset is:

> **A historical record of what important venture-market participants actually did.**

For strategically important investors, a useful target is:

```text
12 months minimum
        ↓
24 months where practical
```

Historical completeness should always be described relative to the **discovered Vantage corpus**, not as complete knowledge of all real-world activity.

---

# Confidence

Vantage measures an observed subset of the venture ecosystem.

It should explicitly distinguish:

```text
Observed activity
```

from:

```text
Total market activity
```

Investor trend confidence currently follows three broad concepts.

### CORPUS-SUPPORTED

Enough observations exist for a comparison and the relevant discovered first-party comparison corpus has been processed.

### OBSERVATIONAL

Enough observations exist to calculate a trend, but equivalent temporal first-party coverage is incomplete or unavailable.

### INSUFFICIENT

There is not enough evidence for a reliable comparison.

Crucially:

> **Corpus-supported does not mean complete knowledge of every investment made by an investor.**

It describes the quality and processing completeness of the observed Vantage corpus.

---

# Integrity Philosophy

Vantage already has reusable safeguards around:

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
- ambiguity review

The governing principle is:

> **Ambiguity is preferable to confidently wrong canonical data.**

But ambiguity cannot lead to a manual-cleaning architecture.

Manual review should be an exception path that teaches us where the system needs improvement.

It should not become the system.

If one record is wrong:

> Record the problem.

If the same problem repeatedly appears and threatens downstream intelligence:

> Improve the machine.

---

# Current Product Surfaces

The Flask application currently provides interfaces into several parts of the knowledge graph.

## Evidence

Search and inspect discovered public evidence.

## Funding

Browse canonical financing events.

## Companies

Inspect company metadata and funding history.

## Investor Intelligence

Inspect:

- observed activity
- behavioural changes
- confidence
- stage patterns
- sector patterns
- geographic coverage
- lead behaviour
- co-investors
- recent investments
- supporting evidence

## Sources

Inspect source health and contribution.

## Data Quality

Inspect resolution and integrity issues.

## Intelligence

View early aggregate venture activity.

These are increasingly interfaces into the underlying venture graph rather than isolated news pages.

---

# Product Validation

Vantage is currently:

> **A credible product thesis backed by a working technical prototype, not yet a validated business.**

The technical question:

> Can a system continuously observe public venture activity and turn it into structured behavioural intelligence?

has been substantially de-risked.

The larger remaining question is:

> **Can Vantage produce intelligence valuable enough that professional users change how they work and pay for it?**

Engineering alone cannot answer that.

Product discovery should therefore run alongside the technical roadmap.

Potential users include:

- venture investors
- growth investors
- corporate venture teams
- fund-of-funds and LP intelligence teams
- strategy teams
- market intelligence teams
- ecosystem researchers

The initial customer profile remains to be validated.

Rather than asking:

> "Would you use Vantage?"

users should be given real intelligence tasks.

Examples:

```text
Understand how Sequoia's investment behaviour is changing.

Find investors increasing exposure to defence.

Identify investors becoming more active at Series A.

Understand who is driving AI infrastructure activity.

Find emerging co-investment relationships.

Identify sectors where lead-investor activity is accelerating.
```

The important questions are:

```text
What do users repeatedly investigate?

Which questions are difficult to answer elsewhere?

Which signals cause them to investigate further?

What would they want monitored continuously?

What would they pay to know sooner or more reliably?
```

The eventual workflow product should emerge from those answers.

---

# Potential Defensibility

The Python codebase itself is unlikely to become Vantage's primary moat.

Much of the individual software architecture could be reproduced.

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
Extraction history
        +
Provenance
        +
Behavioural history
        +
Signal methodology
        +
Customer workflow
```

The important asset is the **data-producing machine and the historical knowledge it accumulates**.

The flywheel is:

```text
More useful sources
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

# Roadmap

## Phases 1–4 — Observation & Knowledge Foundation

**Status: Complete**

Established:

- evidence ingestion
- normalized evidence
- content retrieval
- categorization
- structured extraction
- company / investor / fund entities
- funding rounds
- fund closes
- canonical entity resolution
- canonical event resolution
- multi-source evidence
- provenance
- historical operations
- integrity tooling

---

## Phase 5 — Source Platform V1

**Status: Complete**

Established:

- canonical source registry
- RSS / sitemap / HTML discovery
- incremental / historical modes
- source configuration validation
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

## Phase 7 — Scalable Knowledge Pipeline

**Status: Current**

Phase 7 introduces a safety boundary between probabilistic extraction and canonical truth.

### 7.1 — Versioned Extraction

Introduce durable `ExtractionRecord` persistence.

```text
Evidence
   ↓
Extractor
   ↓
Versioned ExtractionRecord
```

Requirements:

- append-oriented extraction history
- explicit extractor version
- explicit model metadata
- structured payload
- extraction timestamps
- no direct canonical mutation during extraction

### 7.2 — Validation & Safe Promotion

Introduce deterministic candidate validation.

```text
ExtractionRecord
       ↓
Validation
       ↓
PROMOTE / REVIEW / REJECT
       ↓
Canonicalization
```

Reuse the existing canonical entity and event-resolution machinery behind the promotion boundary.

Do not rebuild canonicalization.

### 7.3 — Replay & Reprocessing

Allow the same stored evidence to be safely processed by newer:

- extractors
- prompts
- models
- schemas
- validators

Preserve prior extraction records for comparison and auditability.

### 7.4 — Pipeline Measurement

Measure:

- extraction success
- validation outcomes
- quarantine reasons
- promotion rate
- event yield
- reprocessing outcomes
- extractor-version quality

Use those measurements to identify systemic failure classes.

### Phase 7 success condition

A representative failure should be recoverable like this:

```text
Evidence
   ↓
Extractor v1
   ↓
Bad candidate
   ↓
REVIEW / REJECT

Extractor improves

   ↓
Extractor v2
   ↓
New candidate
   ↓
PROMOTE
   ↓
Canonical event
```

without manually reconstructing the knowledge graph.

---

## Phase 8 — Observation & Historical Scale

**Status: Planned**

Operate substantially larger source cohorts.

Target direction:

```text
30–50 investors
15–25 publications
10–20 ecosystem / company / accelerator sources
```

Expand matched historical coverage across a strategically useful investor cohort.

Measure:

- source reliability
- evidence yield
- event yield
- unique contribution
- evidence overlap
- extraction quality
- historical completeness
- review rate

Let scale expose the next systemic problems.

Do not aim for universal source compatibility.

---

## Phase 9 — Market & Signal Intelligence

**Status: Planned**

Aggregate behaviour across the venture graph.

Potential signals include:

- sector momentum
- stage shifts
- geographic momentum
- funding acceleration
- investor strategy drift
- changing lead activity
- changing syndicates
- increasing investor participation
- emerging themes

Initial signals should remain transparent.

For example:

```text
Current 180D
vs
Previous 180D
```

with drill-down:

```text
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
```

---

## Phase 10 — Search, Monitoring & Workflow

**Status: Future**

Turn the graph into a directly explorable intelligence product.

Potential questions include:

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

Potential workflows include:

- structured search
- investor comparison
- sector monitoring
- saved searches
- watchlists
- alerts
- recurring intelligence briefs

These should be shaped by customer discovery rather than assumed upfront.

---

# Technical Direction

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

Much of the knowledge-building system is also operable through Flask CLI commands.

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

---

# Infrastructure Philosophy

Infrastructure should solve demonstrated constraints rather than anticipated ones.

Vantage should not move to PostgreSQL, Docker, background workers or distributed infrastructure merely because a mature production system might eventually use them.

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

justify the change.

Likewise:

```text
Local execution
   ↓
Scheduled execution
```

when continuous observation requires it.

And:

```text
Local environment
   ↓
Docker
```

when reproducible deployment materially helps development or operations.

One near-term exception is **CI**.

The project now has enough integrity logic and regression tests that automatically running the test suite on repository changes has high leverage without meaningfully increasing architectural complexity.

Technical sophistication is not the product.

---

# Development Principles

## 1. Information acquisition → structure → intelligence

Every major capability should strengthen this progression.

## 2. News is evidence

The article is raw material, not the product.

## 3. Canonical truth is earned

Probabilistic extraction should not automatically become canonical knowledge.

## 4. Preserve provenance

Every important conclusion should remain traceable to underlying evidence.

## 5. Build the machine, not individual integrations

A fix is most valuable when it improves a reusable capability.

## 6. Configuration before bespoke code

New sources should normally require configuration rather than new scraper implementations.

## 7. Use LLMs for semantic understanding

LLMs should interpret unstructured evidence.

Deterministic systems should own:

- persistence
- workflow state
- identity
- constraints
- validation
- matching
- canonicalization
- aggregation

## 8. Prefer ambiguity over false certainty

Incorrect canonical data contaminates downstream intelligence.

## 9. Manual review is an exception path

Human review should teach us how the machine needs to improve.

It should not become the machine.

## 10. Measure the observed universe

Do not confuse observed activity with total market activity.

## 11. Let scale expose systemic problems

Do not continually hunt isolated imperfections.

Fix problems when:

```text
they recur
+
they threaten integrity
+
the fix strengthens the platform
```

## 12. Accept imperfect source coverage

A valuable network matters more than universal compatibility.

## 13. Protect development speed

Do not introduce infrastructure that slows iteration without solving a real constraint.

## 14. Validate the product alongside the technology

Engineering determines what can be built.

Users determine what is valuable.

---

# What Not to Build Yet

Avoid premature work on:

- perfect publication archives
- scraper-per-site architecture
- universal crawling
- opaque AI scores
- complex recommendation systems
- unnecessary ontology complexity
- frontend rewrites for their own sake
- microservices
- Kubernetes
- elaborate event buses
- large distributed infrastructure
- vector databases without a demonstrated retrieval requirement
- agent frameworks without a demonstrated workflow requirement
- infrastructure introduced only because "real startups use it"

---

# Brief History

Vantage has evolved through several distinct stages.

## 1. VC News Aggregator

The original project was approximately:

```text
RSS
 ↓
Articles
 ↓
Searchable news feed
```

The article was effectively the product.

---

## 2. Structured Venture Data

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

The project shifted from displaying news toward structuring venture activity.

---

## 3. Canonical Knowledge

As data accumulated, identity and duplication became the important problems.

The architecture evolved from:

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

Entity resolution, aliases, event resolution, taxonomy normalization and multi-source evidence became foundational.

---

## 4. Source Platform

Observation expanded beyond editorial RSS into reusable:

```text
RSS
Sitemaps
HTML listings
```

A canonical source registry, historical modes, fleet operations and source measurement moved the project away from bespoke scraping.

---

## 5. Investor Intelligence

First-party investor history changed the question from:

```text
What happened?
```

to:

```text
What did this investor actually do?
```

and then:

```text
How has that behaviour changed?
```

Time-window comparisons, lead activity, temporal coverage and confidence-qualified intelligence followed.

---

## 6. Current Stage — Scale the Knowledge Machine

The core concept now works.

The question is no longer:

> Can Vantage understand another venture article?

It is:

> **Can Vantage safely process a much larger evidence corpus and continuously convert it into trustworthy historical knowledge?**

That is why the current focus is versioned extraction, validation, replay and safe canonicalization.

Once that foundation holds under larger scale, Vantage can expand observation aggressively and begin producing broader market-level behavioural signals.

---

# Current Priority

The immediate engineering objective is:

> **Turn Vantage's proven ingestion and knowledge-building pipeline into a scalable, versioned knowledge system that can process much larger evidence volumes without allowing extraction errors to silently contaminate canonical truth.**

The immediate progression is:

```text
VERSIONED EXTRACTION
        ↓
AUTOMATED VALIDATION
        ↓
SAFE PROMOTION
        ↓
REPLAY / REPROCESSING
        ↓
PIPELINE MEASUREMENT
        ↓
LARGER SOURCE NETWORK
        ↓
MORE HISTORICAL BEHAVIOUR
        ↓
CROSS-INVESTOR SIGNALS
        ↓
SEARCH / MONITORING WORKFLOWS
```

In parallel, Vantage should test whether its emerging intelligence is genuinely useful to professional users.

The core engineering question is:

> **Can Vantage continuously observe the venture ecosystem at scale and turn that activity into trustworthy, inspectable intelligence?**

The core product question is:

> **Can that intelligence reveal something valuable enough that professional users change how they work?**

Those are now the two questions the project needs to answer.