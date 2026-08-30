# Project Vantage

Project Vantage is an **evidence-backed behavioural intelligence system for the venture-capital ecosystem**.

It observes fragmented public venture activity, converts evidence into structured historical knowledge, and uses that history to explain how venture investors, funds, strategies and markets are changing over time.

```text
Information acquisition
        ↓
Structured knowledge
        ↓
Historical behaviour
        ↓
Intelligence
        ↓
User value
```

Vantage began as a Python / Flask VC news aggregator.

**News is no longer the product.** Articles, investor announcements, company posts, fund announcements, regulatory filings and other public information are evidence from which Vantage builds an inspectable model of venture activity.

The long-term ambition is to become a trustworthy research and behavioural-intelligence layer for understanding venture investors through time.

---

## Product Thesis

Private-market data is already a large and competitive category.

Vantage should not try to win by becoming a smaller general-purpose database of private companies, investors and funding rounds.

Its sharper thesis is:

> **Treat the venture ecosystem as a continuously observed behavioural system, with capital allocators as the primary subjects of analysis.**

Instead of only asking:

- Which companies exist?
- Who invested in them?
- How much did they raise?

Vantage should increasingly answer:

- How is this investor changing?
- Which stages, sectors and geographies are gaining or losing share of observed activity?
- Is lead behaviour changing?
- Is activity concentrated in new relationships or follow-ons?
- Which syndicates are forming or changing?
- Does observed behaviour align with stated strategy?
- Which fund, team or strategic context may explain the change?
- How does an investor compare with peers or its own historical baseline?
- What events produced the conclusion?
- Why should the user trust it?

The objective is not:

> "AI says cybersecurity is hot."

It is:

> **Here is the measured change, who drove it, the firm and fund context around it, the canonical events behind it, the evidence supporting those events, and the limitations of the observed corpus.**

The governing product principle is:

> **Inspectable intelligence, not unexplained conclusions.**

---

## Strategic Focus: The Venture Ecosystem

Companies remain central to venture capital and central to Vantage's graph, but they are not the strategic centre of gravity.

General private-market platforms can devote enormous resources to exhaustive company intelligence. Vantage should not attempt to reproduce that entire problem.

Its primary analytical subjects should instead be **venture actors**:

- institutional venture firms
- seed and micro-VC firms
- corporate venture investors
- growth investors where relevant
- funds and investment vehicles
- eventually, people and organisational relationships where they materially explain behaviour

Companies remain critical because they are where investment behaviour becomes observable.

A Vantage company profile therefore needs to answer:

> **Why is this company relevant to our understanding of venture activity and investor behaviour?**

rather than becoming an exhaustive private-company research product in its own right.

---

## The Core Asset

The primary asset Vantage is building is:

> **A trustworthy temporal knowledge graph of the observable venture ecosystem.**

```text
Evidence
   ↓
Claims
   ↓
Canonical entities and events
   ↓
Investment firms / Funds / Companies
   ↓
Relationships through time
   ↓
Historical behaviour
   ↓
Change
```

Defensibility can compound through the combination of:

- observation network
- historical evidence corpus
- canonical identities and events
- firm and fund context
- extraction history and provenance
- behavioural baselines
- signal methodology
- research workflow

The accumulated knowledge and evidence history are ultimately more difficult to recreate than the individual services that operate them.

---

# The Target Unit of Analysis

The current codebase is strongest around `Investor`, `Fund`, `FundingRound`, `FundClose` and their evidence.

The longer-term analytical model should distinguish the **firm**, its **funds**, its **people**, its **stated strategies** and its **observed behaviour**:

```text
                       INVESTMENT FIRM
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
        FUNDS               PEOPLE             FIRM STRATEGY
          │                   │                   │
     vehicle / vintage    partners / team      positioning
     size / lifecycle     roles / changes      sectors / stages
     fund strategy        investment history   geography / model
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                      OBSERVED BEHAVIOUR
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
        deals               leads             follow-ons
        stages              sectors           syndicates
        geographies         cadence           outcomes
                              │
                              ▼
                             TIME
                              │
                              ▼
                            CHANGE
                              │
                              ▼
                         INTELLIGENCE
                              │
                              ▼
                           EVIDENCE
```

This is a **product and domain direction**, not a claim that every object above is already implemented.

The current schema does not yet model people, organisational structure, firm history, fund lifecycle, disclosed fund performance or rich firm-vs-fund strategy as first-class objects.

Those concepts should be introduced only when evidence and product value justify them.

A particularly important invariant is:

```text
firm strategy ≠ fund strategy ≠ observed behaviour
```

A firm's aggregate activity can change because different vehicles are active at different times. Vantage should not mistake that mechanically for a firm-wide strategy change.

---

# Investor Intelligence: Target Product

The investor page is likely to become Vantage's flagship research object: a **research dossier + behavioural terminal**, not a static encyclopedia page.

A mature investor view could combine:

| Layer | What Vantage should help answer |
| --- | --- |
| Investor overview | Who is this firm and what kind of investor is it? |
| Firm history & organisation | How did it develop, how is it organised, and what changes matter? |
| Firm strategy | What does the firm publicly say it focuses on and what differentiates it? |
| Funds & capital base | Which vehicles exist, what are their vintages, mandates, strategies and lifecycle states? |
| Observed behaviour | What does the firm actually appear to be doing across stage, sector, geography, cadence, leads and syndicates? |
| Portfolio & outcomes | Which current and historical relationships or exits are most relevant to understanding the investor? |
| Current signals | What changed, when, how materially, and what drove it? |
| Evidence & coverage | What can Vantage see, what is missing, and why should the user trust the analysis? |

### Track Record Requires Strong Semantic Discipline

Vantage must distinguish:

```text
notable portfolio outcomes
        ≠
fund performance
        ≠
firm performance
```

An IPO is not automatically an investor's realised return. A large fund is not performance. Round valuations are not fund marks.

IRR, DPI, TVPI or similar measures should appear only when supported by sufficiently authoritative evidence such as public LP reporting, audited disclosures or equivalent sources.

### Product Experience: Headline → Analysis → Research

The final product should not force every user to read the full dossier.

```text
LEVEL 1 — HEADLINE
What changed?

        ↓

LEVEL 2 — ANALYSIS
How is this investor behaving, and how is that changing?

        ↓

LEVEL 3 — RESEARCH
What is this firm, how are its funds and people relevant,
what is its history, and what evidence supports the view?
```

The product principle is:

> **Headline first. Analysis second. Evidence always available.**

Rich visualisation should eventually compress real analytical questions rather than decorate thin data.

---

# How Vantage Works Today

## 1. Observation

**Question: What happened?**

Vantage discovers evidence through a canonical source registry and reusable acquisition mechanisms.

Implemented capabilities include:

- RSS, XML sitemap and HTML-listing discovery
- incremental and historical operation
- source-specific URL and relevance policies
- publication-date recovery and content retrieval
- source compatibility probing
- fleet execution and failure isolation
- persistent `SourceRun` telemetry
- source contribution and corpus measurement

The registry supports publication, investor, ecosystem, company and structured-source types. The populated corpus remains concentrated on editorial and first-party investor evidence.

For similar websites, acquisition should remain configuration-first. Genuinely new evidence classes may justify source-specific adapters.

---

## 2. Structured Knowledge

**Question: Who did what?**

Persisted evidence is transformed into structured knowledge about companies, investors, funds, funding rounds, fund closes, investor participation, lead relationships and supporting evidence.

The target relationship is:

```text
Many observations
       ↓
One real-world event
```

For example:

```text
Investor announcement
        +
Company announcement
        +
Editorial article
        +
Regulatory observation
        ↓
One canonical financing event
```

### Safe Knowledge Pipeline

```text
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
CANONICAL KNOWLEDGE
```

`ExtractionRecord` preserves versioned machine interpretation rather than overwriting history.

Only validated `PROMOTE` results are permitted to reach canonical persistence.

Knowledge-integrity safeguards also cover recurring failure classes such as aggregate historical financing claims and candidate cross-currency duplicate events.

Detection does not automatically imply canonical mutation.

---

## 3. Behavioural Intelligence

**Question: How is observed investor behaviour changing?**

Canonical historical events support equal-period comparison across:

- investment and lead activity
- companies
- sectors
- stages
- geography
- co-investors

A computable trend is not automatically a trustworthy trend. Measurement and confidence are deliberately separate.

---

## 4. Market Intelligence

**Question: What changed across the observed market?**

Market intelligence aggregates canonical behaviour across a **comparable observed cohort** rather than comparing whatever Vantage happened to discover in each period.

### Sector Momentum V1 — Implemented

Sector Momentum compares equal windows using canonical events and reports change, company and investor participation, leads, contributors, underlying events and coverage.

Signal interpretation is deterministic. An LLM does not decide whether a sector is rising or falling.

Further signal families are not automatic roadmap items.

---

## 5. Product Intelligence

**Question: What changed, why, and why should I trust it?**

The application is now organised around investigation rather than article consumption.

```text
WHAT CHANGED?
      ↓
WHO / WHAT DROVE IT?
      ↓
WHICH CANONICAL EVENTS PRODUCED IT?
      ↓
WHY SHOULD I TRUST IT?
      ↓
SHOW ME THE EVIDENCE
```

Current product capabilities include:

- Intelligence as the default landing experience
- confidence-qualified investor activity comparisons
- Sector Momentum
- human-readable canonical event references
- searchable / filterable Investor and Company explorers
- Funding explorer with stage, sector, currency and participant search
- investor behavioural profiles
- company financing histories
- canonical financing-event investigation
- participating and lead investors
- multi-source supporting evidence
- continuous entity → event → evidence navigation
- Evidence, Source Coverage and Data Quality supporting surfaces

The primary navigation is:

```text
Intelligence
Investors
Companies
Funding
Evidence
System
```

The legacy news feed remains useful as an evidence surface, not the product homepage.

---

# Observation Coverage and Canonical Knowledge

Vantage observes a subset of the venture ecosystem.

It must never confuse:

> **Observed activity**

with:

> **Total real-world market activity**

Private-market information is inherently incomplete and selectively disclosed. That is a permanent property of the domain, not a temporary scraping bug.

Behavioural comparisons therefore consider source coverage, historical continuity, publication dates, processing completeness, canonical identity, cohort comparability and analytical-dimension coverage.

Current confidence concepts are:

### CORPUS-SUPPORTED

The observed Vantage corpus is sufficiently complete for the specific comparison being made.

### OBSERVATIONAL

A pattern can be calculated, but equivalent corpus coverage is unavailable or incomplete.

### INSUFFICIENT

The evidence does not support a meaningful comparison.

**Corpus-supported does not mean complete knowledge of real-world activity.**

### What "Canonical" Means

Vantage should not claim to possess a God's-eye canonical truth of private markets.

Within Vantage, **canonical** means:

> **The system's best reconciled representation of an entity or event given the evidence currently available to it.**

That representation should remain revisable when stronger evidence appears.

---

# Observation & Corpus Strategy

The current frontier is increasingly an **observation-quality problem**, not simply a scraping problem.

Recent corpus diagnostics showed that document volume and historical span alone are insufficient. A source can contain hundreds of pages but contribute little useful financing evidence; an analytically useful investor history can still be downgraded when source identity or historical coverage is represented incorrectly.

The corpus problem therefore has four parts:

```text
DISCOVERY / RECALL
Did Vantage notice that something happened?

EVENT RECONSTRUCTION
What company, amount, stage, date and participants were involved?

IDENTITY / CONTEXT
Which real company, investor, adviser, fund or actor is this?

EVIDENCE / CONFIDENCE
Why should Vantage believe the resulting claim?
```

No single source is expected to solve all four.

## Source Strategy — Under Evaluation

Vantage is exploring a **heterogeneous evidence network** rather than committing to a larger collection of VC website scrapers.

| Evidence role | Potential avenues |
| --- | --- |
| Candidate generation / recall | structured venture-data APIs, web/news search, broader discovery feeds |
| First-party event evidence | company and investor announcements |
| Regulatory corroboration | SEC / EDGAR, Form D, Companies House and other registries |
| Adviser / fund context | Form ADV / IAPD, fund announcements, regulatory records |
| Historical web recovery | Common Crawl or other archives |
| Entity identity | registries and authoritative identifiers |
| Breadth / enrichment | licensed commercial datasets where justified |
| Fund / track-record context | public LP reporting and other authoritative disclosures where available |

These are **avenues under evaluation, not committed providers or roadmap guarantees**.

A structured provider may be useful simply as a candidate generator:

> **Investigate this event.**

It does not need to become Vantage's truth layer.

```text
CANDIDATE SIGNAL
      ↓
EVIDENCE ACQUISITION
      ↓
NORMALIZED EVIDENCE
      ↓
SEMANTIC INTERPRETATION
      ↓
VALIDATION
      ↓
RECONCILIATION
      ↓
CANONICAL KNOWLEDGE
```

not:

```text
API RESPONSE
     ↓
CANONICAL TRUTH
```

Likewise, a regulatory filing may be authoritative about the filing while still being insufficient by itself to prove a Vantage funding event or investor relationship.

### Evaluating New Sources

Before committing to a new provider or evidence class, measure its marginal value against a defined cohort and period using criteria such as:

- event and investor-participation recall
- precision and lead accuracy
- stage, amount and date accuracy
- historical depth
- provenance and identity quality
- licensing and cost
- incremental information beyond the existing corpus

The goal is not to own every acquisition mechanism.

It is to build the most useful trustworthy observation network for differentiated investor intelligence.

---

# Venture-Capital Domain Grounding

The domain model is governed by:

- `docs/venture_capital_domain_primer.md`

The primer is a semantic constitution, not a feature backlog.

Important enduring invariants include:

```text
investment firm ≠ fund
fund ≠ adviser
organisation ≠ person

company financing ≠ fund close
primary financing ≠ secondary transaction
announcement date ≠ necessarily closing date

round size ≠ investor cheque
fund size ≠ capital deployed

participation ≠ lead
follow-on ≠ automatically positive conviction
activity ≠ performance

observed activity ≠ complete market activity
public thesis ≠ observed strategy

raw taxonomy ≠ canonical taxonomy
coverage change ≠ behavioural change

signal → measured change → canonical events → evidence
```

When ambiguity exists, prefer explicit uncertainty over confidently incorrect canonical knowledge.

---

# Current State

Vantage is no longer an experimental news scraper.

The repository contains a functioning observation, structured-knowledge, behavioural-intelligence and product-intelligence system with a coherent server-rendered product experience.

## Established Foundation

- reusable evidence acquisition and canonical source registry
- incremental and historical source operation
- source probing, fleet execution and `SourceRun` telemetry
- content and publication-date enrichment
- structured LLM extraction and Pydantic contracts
- durable versioned `ExtractionRecord`
- deterministic validation, safe promotion and replay
- company and investor entity resolution
- canonical funding-event resolution and multi-source evidence
- lead-investor relationships
- funds and fund closes
- stage and sector normalization
- reconciliation and integrity tooling
- corpus and source-contribution measurement
- investor behavioural intelligence and temporal confidence
- comparable-cohort market comparison and Sector Momentum V1
- Product Intelligence investigation flow
- intelligence-first product shell and core explorers
- database integrity / repair / backup tooling
- GitHub Actions CI, coverage baselines and targeted invariant testing

The latest full local test run contains **448 passing tests**.

Tests are evidence of engineering discipline, not proof of product correctness.

## Productisation V1 — Complete

Productisation V1 established:

- Intelligence as the default landing experience
- separation between product and system/coverage surfaces
- searchable and sortable Investor / Company / Funding discovery
- canonical financing as the primary investigation object
- evidence as supporting provenance rather than the homepage
- readable signal → event → entity → evidence flows
- consolidated Investor and Company profiles
- consistent breadcrumbs and visual hierarchy

This phase is code-complete, test-complete and empirically exercised locally. It is not yet externally product-validated.

## Current Model Boundary

The implementation is narrower than the emerging investor-centric thesis.

Today:

- `Investor` primarily stores identity, website, description and headquarters
- `Fund` stores investor ownership plus basic strategy, geography and vintage
- `FundClose` stores close events and evidence
- behavioural intelligence is primarily derived from canonical financing history

The richer firm / fund / people / strategy / track-record model remains a **target direction**.

The next move is not to add every possible field. It is to determine which evidence classes and user questions justify each semantic expansion.

---

# Current Constraints

The strongest remaining constraints are **observation quality, investor-context depth, intelligence density and product validation**, rather than missing infrastructure.

Current constraints include:

- public venture activity is incomplete and selectively disclosed
- investor announcements have high provenance but limited recall
- the observation network remains too concentrated in editorial and investor-website evidence
- source identity and canonical investor identity are not always aligned cleanly
- historical capability is uneven
- some large document corpora have low useful event yield
- firm, fund and strategy context is still shallow
- people and organisational context are not first-class objects
- funding rounds remain the most mature analytical primitive
- richer visualisation would currently outrun some underlying intelligence
- the local corpus is valuable and is not stored in Git
- SQLite remains appropriate for the current scale
- continuous deployment, alerts and scheduling are not yet demonstrated product requirements

> **Let demonstrated product need or an observed operational bottleneck justify the next layer of complexity.**

---

# Roadmap

```text
FOUNDATION
Observation platform
Canonical knowledge
Domain grounding
Engineering trust
        ✅ SUFFICIENT

              ↓

PRODUCT INTELLIGENCE MVP
Investor behaviour
Sector momentum
Confidence
Signal → event → evidence
        ✅ IMPLEMENTED

              ↓

PRODUCTISATION V1
Intelligence-first shell
Discovery / investigation flow
Profile consolidation
        ✅ COMPLETE

              ↓

CORPUS / OBSERVATION STRATEGY
Corpus readiness
Source-identity correctness
Evidence-class / provider evaluation
Marginal information value
        ← CURRENT

              ↓

INVESTOR KNOWLEDGE & OBSERVATION EXPANSION
Richer firm and fund context
Stronger event recall and corroboration
Only semantics supported by evidence and product value

              ↓

REAL INTELLIGENCE VALIDATION
Defined investor cohort
Repeated comparable windows
Non-obvious evidence-backed insights

              ↓

PRODUCTISATION V2
Investor-centric visual analytics
Only for validated analytical questions

              ↓

REAL USER VALIDATION / ITERATION
Serious research tasks
Repeated-use discovery

              ↓

OPERATIONAL SCALE
Only when real usage creates the constraint
```

---

# Immediate Priorities

## 1. Corpus Readiness & Source-Strategy Evaluation — Current

Before broad ingestion expansion:

- fix demonstrated source ↔ canonical-entity readiness gaps
- validate historical-discovery gaps where existing evidence suggests cheap upgrades
- distinguish acquisition failures from classification, processing and identity failures
- define a representative investor cohort and comparison period
- evaluate candidate evidence classes and structured providers against that cohort
- measure marginal information value rather than source or row count

The key question is:

> **Can a new source materially improve event recall, investor context or evidence quality without becoming canonical truth or eroding Vantage's differentiated methodology?**

No external provider has yet been selected as the committed corpus strategy.

## 2. Investor Knowledge & Observation Expansion — Next

The next substantive expansion should deepen the investor as the primary research object.

Likely evidence targets include some combination of:

- company first-party financing evidence
- structured venture-data candidate generation
- SEC / EDGAR and Form D
- Form ADV / IAPD for adviser and fund context
- Companies House and other registries
- historical web archives
- search APIs for evidence discovery
- fund announcements and first-party strategy material
- public LP reports or equivalent authoritative disclosures where available
- licensed enrichment where its marginal value is demonstrated

The goal is not simply **more rounds**.

It is:

> **Enough evidence and context to reconstruct investor behaviour, firm strategy, fund context and change through time more credibly.**

## 3. Real Intelligence Validation

Once observation and investor context are stronger, prove that Vantage can repeatedly generate useful intelligence across a defined investor cohort.

The standard is not:

> "The system calculated a delta."

It is:

> **Vantage identified a material change in observed investor behaviour, showed what drove it, placed it in relevant firm or fund context, linked it to canonical events, exposed the evidence, and made the observation limitations clear.**

## 4. Productisation V2

Richer dashboards should follow validated analytical questions rather than decorate thin data.

Potential directions include activity time series, strategy-mix shifts, lead composition, new-vs-follow-on mix, syndicate change, investor-vs-cohort comparison, fund context and evidence / coverage overlays.

## 5. Real User Validation / Iteration

Use serious investigation tasks with venture investment, research, platform or strategy professionals.

A strong milestone is:

> **A venture professional independently uses Vantage to identify and investigate a non-obvious change, trusts the evidence chain, and expresses a concrete desire for repeated use.**

## 6. Operational Scale — Later

PostgreSQL, scheduled ingestion, job queues, richer deployment machinery or more complex frontend architecture should be introduced only when recurring usage or measured workload creates a real constraint.

---

# Future Capabilities

Possible later capabilities include:

- first-class people / partner modelling
- organisational and corporate-parent relationships
- corporate-venture-specific context
- richer fund lifecycle
- public LP / fund-performance evidence where genuinely available
- new-company vs follow-on intelligence
- financing subtype and primary / secondary context
- changing syndicates and investor convergence
- geographic and capital-formation signals
- saved investigations, watchlists, alerts and recurring briefs
- deployed continuous operation

These are directions, not commitments.

---

# Development Principles

1. **Information acquisition → structured knowledge → intelligence → user value.** Every major capability should strengthen this progression.
2. **Evidence is not the product.** News, filings, APIs and announcements are raw material.
3. **Canonical truth is earned.** Source responses and model outputs do not automatically become canonical knowledge.
4. **Preserve provenance.** Important conclusions should remain traceable to evidence.
5. **Measurement before interpretation.** Establish what changed before explaining what it means.
6. **LLMs understand; deterministic systems govern.** Deterministic systems own persistence, identity, validation, canonicalization, confidence and measurement.
7. **Measure the observed universe.** Never imply that Vantage's corpus is the entire market.
8. **Comparable evidence before behavioural claims.** Coverage change must not masquerade as behaviour change.
9. **Firm, fund and observed behaviour are different concepts.** Do not infer strategy mechanically from aggregate activity.
10. **Evidence class and marginal information value outrank source count.**
11. **Companies support the investor thesis.** Build company depth when it materially improves venture-actor intelligence.
12. **Track record requires evidence discipline.** Notable outcomes, fund performance and firm performance are not interchangeable.
13. **Fix failure classes, not isolated records.** Manual review should teach or protect the system, not become the system.
14. **Frameworks must earn their complexity.** Technical sophistication without useful intelligence is not progress.

---

# What Not to Build Yet

Deliberately avoid:

- a broad "PitchBook-lite" private-company database
- exhaustive company enrichment unrelated to investor intelligence
- source expansion merely to increase source count
- scraper-per-site or universal-crawling architecture without demonstrated need
- treating a venture API or commercial dataset as canonical truth
- expensive data licensing before its marginal value is demonstrated
- modelling every concept in the domain primer immediately
- speculative people / organisation graphs without a real analytical question
- inferred fund performance from portfolio headlines or valuations
- opaque AI-generated trend scores
- LLM-generated market conclusions without deterministic measurement
- a frontend rewrite purely for polish
- dashboards whose underlying intelligence is not yet credible
- PostgreSQL, Docker, Celery / Redis, Kafka, microservices or Kubernetes for appearance rather than need
- vector databases or agent frameworks without a demonstrated requirement

Technical sophistication is not the product.

---

# Technical Direction

Current core technologies include:

- Python
- Flask / Jinja
- SQLAlchemy / SQLite / Alembic
- OpenAI structured extraction
- Pydantic
- BeautifulSoup / feedparser / requests
- pytest / Hypothesis
- GitHub Actions
- HTML / CSS

Much of the observation and knowledge system can be operated through:

```text
flask --app app vantage ...
```

The development loop remains intentionally simple:

```text
edit → test → run → measure → inspect
```

Future infrastructure transitions should occur only when demonstrated constraints require them.

---

# Working With ChatGPT

Development collaboration conventions are documented in:

- `docs/WORKING_WITH_CHATGPT.md`

A new ChatGPT conversation should normally begin by reading:

```text
README.md
docs/venture_capital_domain_primer.md
docs/WORKING_WITH_CHATGPT.md
```

The repository is authoritative for implementation state.

The README is authoritative for current product direction unless that direction is explicitly changed.

---

# Brief History

**1. News aggregator.** Vantage began as a Flask application that collected and searched VC news. The article was effectively the product.

**2. Structured venture knowledge.** LLM extraction turned evidence into companies, investors, funding rounds, funds and fund closes. News became input rather than output.

**3. Canonical knowledge and provenance.** Identity, duplication and evidence lineage moved the architecture from `1 article → 1 record` toward `many observations → one real-world event`.

**4. Observation and investor behaviour.** A reusable source platform and first-party investor history shifted the question from "what happened?" to "how is this investor's observed behaviour changing?"

**5. Safe knowledge and market intelligence.** Versioned extraction, deterministic validation, safe promotion, comparable cohorts and Sector Momentum established a trustworthy path from evidence to signals.

**6. Product intelligence and productisation.** Signals were connected to canonical events and evidence. Productisation V1 then made Intelligence the default experience and created coherent Investor, Company, Funding and Evidence investigation flows.

**7. Investor-centric venture intelligence.** The strategic thesis narrowed again: companies remain essential graph objects, but the venture actor is the primary analytical subject. The deeper question is now: **who is this investor, how are the firm and its funds positioned, what does it say it does, what does it appear to do, and how is that changing?**

**8. Current frontier.** Improve the evidence mix and investor context enough that behavioural intelligence becomes consistently non-obvious, credible and useful.

---

# What Success Looks Like

Vantage succeeds if it can reliably:

```text
Observe venture activity
        ↓
Preserve heterogeneous evidence
        ↓
Resolve real entities, funds and events
        ↓
Build trustworthy historical context
        ↓
Understand stated strategy and observed behaviour
        ↓
Measure behavioural change
        ↓
Surface meaningful signals
        ↓
Explain exactly why they exist
        ↓
Help users decide what to investigate or monitor
```

A successful Vantage is not the system with the most companies, sources, infrastructure or AI.

It is the system where a user can ask:

> **How is this venture investor changing, what is driving the change, how does it fit the firm's and funds' strategy, and why should I believe it?**

and receive an answer that is useful at headline depth, powerful at analytical depth, and fully inspectable at evidence depth.
