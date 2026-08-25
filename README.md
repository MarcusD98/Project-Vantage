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

Where is lead-investor behaviour shifting?

How is an investor's observed strategy changing over time?

Which investors are converging around the same themes?

Which syndicates are forming or changing?

What real-world events support those conclusions?

How much should a user trust the conclusion given Vantage's observation coverage?

The objective is not:

"AI says cybersecurity is hot."

It is:

Here is the measured change, who drove it, the canonical events behind it, the evidence supporting those events, and the limitations of the observed corpus.

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

The system also models funds and fund closes. Broader venture concepts should be added only when product value and domain understanding justify them.

The governing domain rule is:

Add a domain object when it is necessary to represent valuable observable truth that the current model cannot express safely.

How Vantage Works

The current architecture has five connected product layers.

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

Safe Knowledge Pipeline

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
CANONICAL KNOWLEDGE

ExtractionRecord preserves an append-oriented history of what a specific extractor version believed about a specific piece of evidence.

Replay creates a new extraction record rather than overwriting historical machine interpretation.

Only validated PROMOTE results are permitted to reach canonical persistence.

Failed promotions remain observable and retryable.

Knowledge-integrity safeguards now also include targeted quarantine and candidate-detection mechanisms for recurring failure classes such as aggregate historical financing claims and cross-currency duplicate financing events.

These safeguards should remain conservative.

Detection does not automatically imply canonical mutation.

3. Behavioural Intelligence

Question: How is observed investor behaviour changing?

Canonical historical events support investor-level behavioural analysis.

For a given investor, Vantage can compare equal periods:

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

Market intelligence aggregates canonical behaviour across a comparable observed cohort rather than blindly comparing whatever Vantage happened to discover in each period.

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

Sector Momentum now sits alongside investor-level behavioural change in the first Product Intelligence MVP.

Further signal families are not automatic roadmap items.

They should be added only when product validation demonstrates that a new analytical question is materially valuable.

5. Product Intelligence

Question: What changed, why, and why should I trust it?

The first Product Intelligence MVP turns existing behavioural and market intelligence into an investigation workflow.

The core chain is:

WHAT CHANGED?
      ↓
WHO / WHAT DROVE IT?
      ↓
WHICH CANONICAL EVENTS PRODUCED IT?
      ↓
WHY SHOULD I TRUST IT?
      ↓
SHOW ME THE EVIDENCE

Current product capabilities include:

investor activity-shift cards

confidence-qualified current vs previous comparisons

Sector Momentum

contributor context

current and previous canonical event links

canonical funding-event investigation pages

participating and lead investors

multi-source supporting evidence

direct links to original evidence

explicit corpus and methodology context

This is the first version of Vantage that should be treated as a genuine Product Intelligence MVP, rather than only an engineering or data-platform prototype.

Observation Coverage and Confidence

Vantage observes a subset of the venture ecosystem.

It must never confuse:

Observed activity

with:

Total real-world market activity

Changes in the observation network can otherwise be mistaken for changes in the market.

Behavioural comparisons increasingly account for:

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

Coverage gates should be scoped to the analytical question.

Venture-Capital Domain Grounding

The domain model is governed by:

docs/venture_capital_domain_primer.md

The primer exists to prevent the software ontology from growing faster than Vantage's understanding of the venture-capital system.

It is a semantic constitution, not a feature backlog.

Important enduring invariants include:

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

When ambiguity exists, prefer explicit uncertainty over confidently incorrect canonical knowledge.

Near-wedge semantic improvements that may become valuable include:

new-company vs follow-on participation

financing subtype

primary vs secondary transaction context

fund-cycle context

richer participation relationships

They should be built only when product use justifies them.

Corpus Observability

Vantage measures important characteristics of its own observation network and corpus.

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

The product question is:

What can Vantage actually see, and how much should we trust comparisons based on it?

Corpus observability may become a stronger visual product surface during Productisation V1 where it improves user trust and interpretation.

Current State

Vantage is no longer an experimental news scraper.

The repository now contains a functioning observation, structured-knowledge, behavioural-intelligence and product-intelligence platform.

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
                         │
                         ▼
               PRODUCT INTELLIGENCE
                         │
                         ▼
             EVENT → EVIDENCE INVESTIGATION

Established Foundation

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

aggregate historical-financing quarantine

conservative cross-currency duplicate detection

source contribution measurement

corpus observability metrics

investor behavioural intelligence

temporal corpus confidence

comparable-cohort market comparison

Sector Momentum V1

Product Intelligence overview

canonical funding-event investigation

evidence drill-down

reproducible local environment

environment-driven configuration

database integrity / repair tooling

database backup / restore tooling

GitHub Actions CI

coverage baselines

targeted property and invariant testing

Flask / Jinja operational UI

Flask CLI operational tooling

The current local test suite contains 444 passing tests.

That is useful evidence of engineering discipline, but test count alone is not proof of correctness.

Current Constraints

Vantage now has a sufficiently strong engineering and knowledge foundation to support product development without a major infrastructure redesign.

The most important remaining constraints are increasingly product, observation and semantic constraints, rather than missing platform machinery.

Current constraints include:

SQLite remains the active datastore by design; there is no demonstrated need to migrate yet

the accumulated local evidence corpus remains a valuable local asset and is not stored in Git

public venture evidence is inherently incomplete and selectively disclosed

first-party temporal coverage remains uneven across the full configured investor universe

funding rounds remain the most mature analytical event primitive

broader venture-domain concepts should not be added until they are needed to represent valuable observable truth safely

the current UI is functionally coherent but needs a bounded professional productisation pass before external validation

recurring deployment, scheduling, alerts and continuous operation are not yet demonstrated product requirements

Further engineering hardening should be driven by demonstrated failure risk rather than test-count accumulation.

The governing rule remains:

Let demonstrated product need or an observed operational bottleneck justify the next layer of complexity.

Roadmap

The roadmap is now product-led rather than feature-sequence-led.

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
Professional frontend / UX consolidation
Information architecture
Navigation
Visual consistency
Investigation workflow
        ← NEXT

              ↓

REAL USER VALIDATION
Structured investigation tasks
5–8 target-user sessions
Repeated-use discovery

              ↓

VALIDATION-DRIVEN EXPANSION
Only build the capability the evidence justifies

              ↓

OPERATIONAL SCALE
Only when real usage creates the constraint

Completed Foundation

Observation & Knowledge Foundation — Complete

Established evidence ingestion, content retrieval, structured entities, funding rounds, funds, fund closes, entity resolution, event resolution, provenance and historical operations.

Source Platform V1 — Complete

Established the canonical source registry, reusable RSS / sitemap / HTML discovery, incremental and historical modes, source validation, fleet execution, persistent source runs, failure isolation and measurement.

Investor Intelligence V1 — Complete / MVP Established

Established investor profiles, activity, lead behaviour, sector / stage / geographic exposure, co-investors, temporal comparison and confidence-qualified intelligence.

Scalable Knowledge Pipeline — Complete / Foundation Established

Established versioned extraction, deterministic validation, safe promotion, replay, measurement and canonical event integrity.

Further changes here should be driven by recurring systemic failures rather than isolated records.

Engineering Trustworthiness V1 — Complete Enough

Established:

reproducible environment configuration

deferred external API clients

environment-driven application configuration

SQLite foreign-key enforcement

integrity and repair tooling

database backup / restore

GitHub Actions CI

coverage baselines

targeted property and invariant testing

Further hardening should be driven by demonstrated risk rather than test-count accumulation.

Test Trustworthiness V1 — Complete Enough

Critical truth-producing paths have been strengthened with coverage analysis and targeted property / invariant testing.

Test quality should continue to improve when new failure classes expose meaningful gaps.

Venture-Capital Domain Grounding V1 — Complete

docs/venture_capital_domain_primer.md defines the semantic boundaries and enduring invariants that should constrain future product and ontology expansion.

The primer is a semantic constitution, not a feature backlog.

Observation Scale V1 — Current Objective Achieved

The investor observation network has been materially broadened using generic acquisition mechanisms.

Further source expansion is not the default priority.

New sources should be added when they materially improve the observable universe, introduce a strategically useful evidence class, or expose a reusable acquisition gap.

Product Intelligence MVP — Implemented

Vantage now exposes behavioural and market intelligence as an investigation workflow.

This slice is code-complete, test-complete and empirically exercised against the local corpus.

External product validation has not yet occurred.

Immediate Priorities

1. Productisation V1 — Next

Before external product validation, bring the existing Flask / Jinja application together into one coherent professional product experience.

The objective is not a frontend rewrite.

It is:

Make the existing intelligence product intentional, navigable, credible and easy enough to use that external feedback is about the intelligence rather than avoidable UI friction.

The productisation pass should assess:

information architecture

primary navigation

default landing experience

relationship between Intelligence, Investors, Companies, Funding, Sources and Data Quality

hierarchy between primary intelligence and supporting operational surfaces

investor investigation workflow

market-signal investigation workflow

canonical event / evidence drill-down

visual consistency

typography, spacing, cards, labels and badges

low-confidence and empty states

laptop-scale usability

demotion of legacy news-aggregator presentation where appropriate

Flask / Jinja remains the default frontend architecture.

A React rewrite is not a prerequisite.

Productisation V1 should remain bounded.

It is a consolidation pass, not a new product programme.

2. Real User Validation

After Productisation V1, test Vantage with a narrow target user group such as venture investment, research, platform or strategy professionals.

Use real investigation tasks rather than feature demonstrations.

Core questions:

Can a user identify a meaningful investor or market change?

Can they understand what drove the change?

Can they inspect the underlying events?

Can they verify the original evidence?

Do they understand the confidence and observation limitations?

Did Vantage reveal something useful enough to change or accelerate their workflow?

What would they want Vantage to monitor repeatedly?

A strong next milestone is:

A venture professional independently uses Vantage to identify and investigate a non-obvious change, trusts the evidence chain, and expresses a concrete desire for repeated use.

Run approximately 5–8 serious target-user sessions before making the next major roadmap commitment.

3. Validation-Driven Expansion

The next engineering capability should be chosen from observed product need.

Possible directions include:

Better behavioural semantics

new-company vs follow-on participation

financing subtype

primary vs secondary context

fund-cycle context

richer lead / participation relationships

Better observation

company first-party expansion

structured regulatory adapters

SEC / EDGAR evidence

Form ADV / IAPD

Companies House or other registries

other authoritative structured feeds

licensed commercial enrichment

Source expansion should be by evidence class and marginal information value, not source count.

Structured data should enter through:

SOURCE-SPECIFIC ACQUISITION
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

not:

API
 ↓
CANONICAL TRUTH

Recurring workflow

If users ask Vantage to keep watching something, that can justify:

watchlists

alerts

recurring intelligence briefs

saved investigations

New intelligence

Additional signal families should be built only when users demonstrate a valuable unanswered question.

Possible analytical directions remain:

stage / lead shifts

investor strategy change

changing syndicates

investor convergence

geographic momentum

fund-context intelligence

These are hypotheses, not commitments.

4. Operational Scale — Later

Do not introduce infrastructure simply because the application is becoming more sophisticated.

Potential future changes such as:

PostgreSQL

deployment automation

scheduled ingestion

job queues

richer frontend architecture

monitoring infrastructure

should be introduced only when recurring usage or measured workload creates a real operational constraint.

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

17. The domain primer is a constraint, not a backlog

Domain sophistication should improve semantic correctness before it expands ontology breadth.

18. Product workflow outranks backend accumulation

Prefer end-to-end professional investigation workflows over adding capabilities with no demonstrated user path.

What Not to Build Yet

Deliberately avoid:

source expansion merely to increase source count

scraper-per-site architecture

universal crawling

headless-browser infrastructure without a demonstrated source need

historical processing merely to clear every backlog

validators or parsers for isolated one-off anomalies

a giant generic event ontology

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

Hypothesis

GitHub Actions

HTML / CSS

Much of the observation and knowledge system can also be operated through the:

flask --app app vantage ...

CLI.

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

Working With ChatGPT

Development collaboration conventions are documented in:

docs/WORKING_WITH_CHATGPT.md

A new ChatGPT conversation should normally begin by reading:

README.md
docs/venture_capital_domain_primer.md
docs/WORKING_WITH_CHATGPT.md

The repository is authoritative for implementation state.

The README is authoritative for current product direction unless that direction is explicitly changed.

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

How is that observed behaviour changing?

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

8. Product Intelligence

The next transition connected signals to a professional investigation flow:

Signal
  ↓
Driver
  ↓
Canonical event
  ↓
Evidence
  ↓
Confidence

This established the first Product Intelligence MVP.

The current frontier is no longer:

Can Vantage build structured venture knowledge?

It is:

Can Vantage turn accumulated historical knowledge into a professional intelligence product that users repeatedly value?

Productisation V1 is the immediate bridge to answering that question with real users.

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