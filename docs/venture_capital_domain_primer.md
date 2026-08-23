# Venture Capital Domain Primer

**Project Vantage — Domain Grounding V1**  
**Version:** 1.0  
**Research checked:** 23 August 2026

> **Purpose and scope**
>
> This is a compressed but deliberately rigorous domain primer intended to ground the design and development of **Project Vantage**. It is not a complete account of venture-capital industry knowledge, mechanisms, regulation, accounting, taxation, legal practice, market convention, jurisdictional differences, fund operations, or investment strategy.
>
> It is **not legal, tax, accounting, regulatory, valuation, or investment advice**. Venture-capital structures and terminology vary materially by jurisdiction, fund documents, security terms, market segment, and firm. Regulatory definitions can be narrower than industry usage and can change over time.
>
> The objective is to understand the venture-capital system well enough that Vantage models real economic objects and relationships rather than accidentally treating its first successful data primitive—funding rounds—as the ontology for the entire industry.

---

# Executive Summary

Venture capital is not simply:

```text
Investor
   ↓
invests in
   ↓
Company
```

A more realistic system is:

```text
                    CAPITAL PROVIDERS
          Pension funds / Endowments / Family offices
       Sovereign funds / Insurers / Corporates / Individuals
                           │
                           │ commitments
                           ▼
                    LIMITED PARTNERS
                           │
                           ▼
                    VENTURE FUND
                   ┌───────┴────────┐
                   │                │
              managed by       governed by
                   │                │
                   ▼                ▼
          GP / Adviser /       Fund documents
         Management company      and LPA
                   │
                   │ deploys capital
                   ▼
              PORTFOLIO COMPANIES
                   │
       ┌───────────┼───────────────┐
       ▼           ▼               ▼
    Equity        SAFEs       Convertible / debt
       │           │               │
       └───────────┼───────────────┘
                   ▼
            FINANCING EVENTS
                   │
       ┌───────────┼───────────────┐
       ▼           ▼               ▼
     Lead       Participant      Follow-on
       │           │               │
       └───────────┼───────────────┘
                   ▼
          OWNERSHIP / GOVERNANCE
                   │
                   ▼
          COMPANY VALUE CREATION
                   │
        ┌──────────┼───────────┐
        ▼          ▼           ▼
       M&A        IPO       Secondary
        │          │           │
        └──────────┼───────────┘
                   ▼
               LIQUIDITY
                   │
                   ▼
              DISTRIBUTIONS
                   │
                   ▼
                   LPs
```

Vantage currently observes only part of this system—and that is appropriate.

Its current strongest domain primitives are:

- companies;
- investors / investment firms;
- funds;
- funding rounds;
- fund closes;
- investor participation;
- lead-investor participation;
- evidence and provenance;
- historical activity.

The most important domain lessons for Vantage are:

1. **Investment firm, adviser, GP, management company, fund, and individual partner are related but distinct concepts.**
2. **A startup financing and a VC fundraise are different capital-formation events.**
3. **A funding-round amount is not the amount invested by each investor.**
4. **A reported company valuation is not the same as the fair value of every security held by every investor.**
5. **Investment activity is not investment performance.**
6. **Lead, co-lead, participant, new investor, existing investor, and follow-on investor represent different behaviours.**
7. **Primary capital and secondary liquidity are economically different even when announced together.**
8. **Stage labels such as Seed, Series A, and Growth are useful but non-universal market conventions.**
9. **Fund lifecycle strongly affects observable investor activity and can confound behavioural signals.**
10. **Public data is inherently incomplete and selectively disclosed.**
11. **Regulatory filings can be authoritative about the filing but still be semantically insufficient to prove a Vantage event.**
12. **The correct direction is evidence → claims → canonical entities/events → historical behaviour → signals, not source → database row → conclusion.**

---

# 1. What Venture Capital Is

## 1.1 Economic purpose

Venture capital is a form of private-market risk capital used primarily to finance companies with high growth potential, uncertain future cash flows, limited operating histories, and frequently little or no current profitability.

Unlike conventional bank lending, venture investing typically does not depend primarily on:

- existing cash flow sufficient to service debt;
- hard collateral;
- predictable repayment schedules.

Instead, a venture investor generally accepts substantial risk in exchange for an ownership or ownership-linked economic interest and the possibility of a disproportionately large future outcome.

Traditional venture funds usually invest in privately held operating companies in exchange for equity or equity-linked instruments. The U.S. Securities and Exchange Commission describes private funds as entities that pool money from multiple investors and notes that traditional venture funds typically invest in businesses for equity, often with industry or stage specialisation.[^sec-private-funds]

The economic model therefore combines:

```text
High uncertainty
      +
Illiquidity
      +
Long holding periods
      +
Asymmetric outcomes
      +
Active selection / governance
      ↓
Potentially outsized returns
```

The important word is **potentially**. Venture portfolios contain failures, write-offs, modest outcomes, and occasional outsized winners.

## 1.2 Venture capital versus private equity

The terminology is context-dependent.

In a broad technical sense, **private equity** can refer to equity investments in privately held companies and can encompass venture capital, growth capital, and buyouts.

In ordinary industry conversation, however:

- **venture capital** usually refers to financing younger, high-growth companies;
- **growth equity** usually refers to more mature private companies seeking expansion capital;
- **private equity** often colloquially means buyout investing, commonly involving control transactions and greater use of leverage.

Invest Europe explicitly treats venture, growth, and buyout as distinct investment stages or strategies within the broader private-equity universe.[^invest-europe-stages]

**Vantage implication:** the system should not assume that every entity labelled “private equity” behaves like a venture investor, or that “growth” and “venture” are interchangeable.

## 1.3 Venture capital as both industry term and regulatory term

“Venture capital fund” can have:

1. a **market meaning** — a fund that invests in startup and growth companies; and
2. a **legal/regulatory meaning** — a specifically defined category under a jurisdiction's laws.

For example, the U.S. SEC has a particular regulatory definition of a venture capital fund for purposes of the Investment Advisers Act exemption, including restrictions around qualifying investments, leverage, redemption rights, and how the fund represents its strategy.[^sec-vc-definition]

The EU's EuVECA regime similarly defines a “qualifying venture capital fund” using detailed portfolio and manager criteria.[^eu-euveca]

**Vantage implication:** never use a colloquial classification as if it proved a regulatory status.

A field such as:

```text
strategy = "venture capital"
```

should not imply:

```text
regulatory_status = "qualifying venture capital fund"
```

unless there is separate evidence.

---

# 2. A Compressed History of Modern Venture Capital

## 2.1 Before the modern VC firm

Risk capital existed long before the modern venture-capital industry.

Historically, entrepreneurial ventures were financed through combinations of:

- founders' own capital;
- wealthy families;
- merchant and industrial capital;
- informal partnerships;
- banks where collateral and business stability permitted;
- individual patrons and angel-like investors.

The modern innovation was not the invention of risky investment. It was the **institutionalisation and professionalisation** of specialised capital for high-risk, high-growth private companies.

## 2.2 American Research and Development Corporation

A common landmark in the history of modern institutional venture capital is **American Research and Development Corporation (ARD)**, established in 1946.

Harvard Business School's historical collection describes Georges Doriot as a central figure in the development of the modern VC industry and ARD as one of the first modern venture-capital companies. ARD sought to connect institutional capital with emerging technology companies after World War II.[^hbs-doriot]

This mattered because the model increasingly combined:

- external capital;
- professional investment selection;
- long-term company development;
- active governance and advice;
- portfolio-based risk taking.

## 2.3 The SBIC programme

In 1958, the United States created the **Small Business Investment Company (SBIC)** programme.

The U.S. Small Business Administration describes the programme as a public-private mechanism designed to stimulate and supplement the flow of private equity capital and long-term debt financing to American small businesses.[^sba-sbic]

SBICs are not synonymous with venture capital, but the programme is historically important to the development of institutional private-company finance.

## 2.4 The limited-partnership model

Over subsequent decades, the closed-end limited-partnership structure became a dominant architecture for venture and private-equity funds.

That structure separated:

```text
CAPITAL PROVIDERS
Limited Partners
        │
        │ commit capital
        ▼
FUND VEHICLE
        │
        │ managed by
        ▼
GENERAL PARTNER / MANAGER
```

This model helped create the modern fund economics of:

- capital commitments;
- management fees;
- carried interest;
- defined fund terms;
- investment periods;
- distributions;
- LP governance rights.

## 2.5 Institutionalisation and globalisation

From the late twentieth century onward, venture capital became increasingly institutional:

- pension funds and endowments became major LPs;
- specialist firms developed repeat fund franchises;
- Silicon Valley and other technology clusters became major centres of venture formation;
- venture ecosystems expanded globally;
- funds specialised by stage, sector, geography, and company type;
- larger growth funds emerged alongside traditional early-stage funds;
- corporate venture capital expanded;
- secondary markets became more important;
- seed financing became more standardised;
- SAFEs and other streamlined instruments became common in parts of the early-stage market;
- the boundary between venture, growth, crossover, and public-market capital periodically blurred.

The key lesson for Vantage is that **the market is structurally dynamic**. Labels and behaviours evolve.

---

# 3. The Venture-Capital Ecosystem

## 3.1 Core actors

A useful map is:

```text
LIMITED PARTNERS / CAPITAL PROVIDERS
│
├── pension funds
├── university endowments
├── foundations
├── sovereign wealth funds
├── insurance companies
├── family offices
├── fund-of-funds
├── corporates
└── high-net-worth individuals
          │
          ▼
VENTURE / PRIVATE CAPITAL FUNDS
          │
          ▼
INVESTMENT FIRMS / GPS / ADVISERS
          │
          ▼
PORTFOLIO COMPANIES
          │
          ├── founders
          ├── employees
          ├── boards
          ├── customers
          └── other shareholders
```

Around this core sit:

- angel investors;
- angel syndicates;
- accelerators and incubators;
- corporate venture arms;
- venture debt providers;
- banks;
- investment banks;
- law firms;
- fund administrators;
- auditors;
- valuation advisers;
- placement agents;
- secondary investors;
- stock exchanges;
- regulators;
- company registries;
- data providers;
- media and research organisations.

## 3.2 Founders and operating companies

The operating company is the productive enterprise raising capital.

It may have:

- founders;
- employees;
- common shareholders;
- preferred shareholders;
- option holders;
- warrant holders;
- debt holders;
- convertible-security holders.

The company may raise several types of capital over its lifetime and may conduct multiple transactions under the same broad “round” label.

**Vantage implication:** `Company` is a durable entity. A financing is an event involving the company, not a permanent property of the company.

## 3.3 Angel investors

Angel investors are individuals who invest their own capital directly into companies, commonly at very early stages.

They differ structurally from VC funds because:

- the capital may be personal rather than pooled;
- there may be no fund vehicle;
- decision processes can be highly individual;
- cheque sizes and governance rights vary widely.

Angel syndicates may pool multiple individuals into a coordinated investment, sometimes through an SPV.

**Vantage implication:** a future investor ontology may need both **organisation** and **person** investor types. Do not force every investor into a firm-shaped entity.

## 3.4 Venture-capital firms

A venture-capital firm is the organisation through which investment professionals operate.

The public brand—such as a well-known VC name—is often not identical to:

- the legal investment adviser;
- the management company;
- the general partner entity;
- any individual fund;
- the legal entities that actually hold securities.

This is one of the most important distinctions in the entire primer.

## 3.5 Corporate venture capital

Corporate venture capital (CVC) refers broadly to investments made by corporations into external companies, often through:

- a dedicated corporate venture unit;
- a subsidiary;
- the corporate balance sheet;
- a separate fund vehicle.

Objectives may combine:

- financial return;
- strategic access;
- technology scouting;
- ecosystem development;
- commercial partnership;
- defensive positioning.

**Vantage implication:** observable investment behaviour does not always represent purely financial portfolio optimisation.

## 3.6 Growth investors and crossover investors

Growth investors typically invest in more mature private companies. Invest Europe describes growth investment as often minority investment into relatively mature companies seeking primary capital to expand, improve operations, or enter new markets.[^invest-europe-stages]

“Crossover investor” commonly describes an investor active in both private and public markets or an investor whose strategy bridges late-stage private investing and public-market investing.

These categories can change through market cycles.

**Vantage implication:** stage and investor-type classifications should be versioned or evidence-based rather than treated as immutable truths.

## 3.7 Limited Partners

Limited Partners (LPs) are the investors in a fund.

They commit capital to the fund but generally do not manage the fund's day-to-day investment decisions.

Typical institutional LP categories include:

- pension funds;
- endowments;
- foundations;
- insurers;
- sovereign wealth funds;
- family offices;
- funds-of-funds.

An LP's commitment is not normally paid entirely on day one. Capital is generally drawn over time through **capital calls**.

ILPA defines a capital call as the actual transfer of previously committed capital when the fund requires it.[^ilpa-glossary]

---

# 4. Firm, Adviser, GP, Management Company and Fund

## 4.1 Why these concepts are easy to confuse

Public communications often say:

> “Firm X raised a $500 million fund.”

That sentence compresses several legal and economic entities.

A simplified structure might be:

```text
                      BRAND / VC FIRM
                    "Example Ventures"
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
      MANAGEMENT COMPANY         INVESTMENT ADVISER
              │                         │
              └────────────┬────────────┘
                           ▼
                    GENERAL PARTNER
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          FUND I         FUND II      GROWTH FUND
             │             │             │
             ▼             ▼             ▼
         portfolio      portfolio      portfolio
         companies      companies      companies
```

The actual structure can be more complicated.

The SEC explicitly notes that a private fund may have a separate investment adviser and other management entities, each of which may be a separate legal entity.[^sec-starting-fund]

## 4.2 Investment firm

For Vantage, the term **investment firm** is useful as the canonical commercial organisation or investing platform users recognise.

Example conceptual object:

```text
Investor
name = "Example Ventures"
website = "..."
```

This is often the correct level for public behavioural intelligence.

But it should not be mistaken for the full legal structure.

## 4.3 Investment adviser

The investment adviser is the entity that provides investment advice and typically exercises investment discretion for the fund, subject to the governing documents.

In the United States, advisers may be:

- SEC-registered;
- state-registered;
- exempt reporting advisers;
- otherwise subject to applicable exemptions.

The SEC's IAPD system publishes Form ADV information for registered advisers and certain exempt reporting advisers.[^sec-iapd]

## 4.4 General Partner

In a limited-partnership fund, the General Partner (GP) is the party with management responsibilities and obligations under the fund documents.

In industry conversation, “the GP” is also sometimes used loosely to mean the fund manager or sponsor.

That usage can obscure legal distinctions.

## 4.5 Management company

The management company commonly employs staff, pays operating expenses, and receives management fees.

Its ownership may differ from the economic ownership of carried-interest vehicles or GP entities.

ILPA's Principles specifically emphasise transparency around management-company ownership and GP/fund economics.[^ilpa-principles]

## 4.6 Fund vehicle

The fund is the pooled investment vehicle.

A single firm can manage many funds:

```text
Firm
├── Seed Fund I
├── Seed Fund II
├── Core Fund IV
├── Growth Fund II
└── Opportunity Fund I
```

Each fund can have its own:

- investors / LPs;
- size;
- vintage;
- strategy;
- geographic scope;
- investment period;
- portfolio;
- economics;
- legal terms.

### Current Vantage mapping

Project Vantage already makes an important correct distinction:

```text
Investor
   │
   └── has many → Fund
```

The current `Fund` model includes:

- `name`;
- `investor_id`;
- `strategy`;
- `geography`;
- `vintage_year`.

That is directionally correct and should be preserved.

---

# 5. Venture Fund Formation

## 5.1 Fund thesis

Before fundraising, a manager usually defines an investment proposition covering some combination of:

- stage;
- sectors;
- geography;
- cheque size;
- target ownership;
- portfolio size;
- reserve policy;
- follow-on strategy;
- fund size;
- differentiation;
- team;
- prior track record.

The thesis can be explicit or flexible.

A public “investment thesis” should not automatically be treated as a precise mandate. The legal fund documents matter more than marketing language.

## 5.2 Fundraising

The manager solicits commitments from prospective LPs.

A simplified process:

```text
Strategy / target fund size
          ↓
Marketing to LPs
          ↓
Due diligence
          ↓
Subscription documents
          ↓
First close
          ↓
Additional closes
          ↓
Final close
```

Private-fund fundraising itself is a securities offering and is subject to applicable securities law. In the United States, private funds commonly raise capital through exempt offerings, including Regulation D structures.[^sec-private-funds]

## 5.3 Commitment versus cash

Suppose an LP signs for:

```text
$20m commitment
```

That does **not** mean the LP immediately wires $20m.

Instead:

```text
LP commitment = contractual obligation
Called capital = amount requested to date
Paid-in capital = amount actually contributed
Uncalled commitment = remaining committed amount
```

Example:

```text
Original LP commitment        $20m
Capital called so far          $8m
                              ----
Uncalled commitment           $12m
```

**Vantage implication:** `fund_size`, `committed_capital`, `called_capital`, `invested_capital`, `NAV`, and `dry_powder` must never be treated as synonyms.

## 5.4 First close

The **first close** is the point at which the first group of LPs is formally admitted and the fund can generally begin operating under its governing documents.

ILPA defines a fund's first closing as the date on which the first LPs have made commitments and are admitted to the fund.[^ilpa-principles-definitions]

A fund may begin investing before reaching its final target size.

## 5.5 Subsequent and final closes

After the first close, additional LPs may enter through subsequent closes.

The **final close** generally ends the fundraising process for that fund, subject to the governing documents.

Important:

```text
Fund target size ≠ final fund size
First close amount ≠ final fund size
Fund announcement ≠ necessarily final close
```

A press release saying a manager “raises $500m” may refer to:

- a first close;
- a final close;
- total commitments;
- a family of parallel vehicles;
- a fund plus sidecar;
- a target;
- a hard cap.

The evidence must determine which.

### Current Vantage mapping

Vantage's `FundClose` model already distinguishes a canonical fund-close event from a startup financing and captures:

- fund;
- amount;
- currency;
- close type;
- announcement date;
- supporting evidence.

This is a sound domain boundary.

---

# 6. Fund Economics

## 6.1 Management fees

Management fees fund the operation of the investment organisation.

Terms vary materially.

A common pattern in closed-end private funds is:

```text
Investment period:
fee based primarily on committed capital

Later fund life:
fee base steps down or shifts,
often toward invested capital / cost / NAV
depending on the LPA
```

The exact percentage, base, offsets, step-down, and duration are contractual.

The famous shorthand “2 and 20” is not a rule and should not be encoded as one.

## 6.2 Carried interest

**Carried interest**, or **carry**, is the GP's contractual share of investment profits.

ILPA describes carried interest as an agreed share of profits accruing to the GP, with calculation and payment governed by the legal documents and any applicable hurdle.[^ilpa-principles-definitions]

A simplified example:

```text
LP capital returned             $100m
Additional distributable profit $100m

If carry = 20% of applicable profits:

GP carry                         $20m
LP share of profit               $80m
```

Real waterfalls are more complex.

## 6.3 Preferred return / hurdle

Some private-capital funds require LPs to receive a minimum preferred return before the GP earns carry.

This is **not universal**, and venture funds frequently differ from buyout funds in this respect.

Vantage should therefore model a hurdle only when supported by fund-specific evidence.

## 6.4 Catch-up

A catch-up provision can allocate a greater share of distributions to the GP after LPs receive a specified preferred return, until the agreed economic split is reached.

This is a legal/economic term, not necessary for Vantage's immediate product, but important for understanding why fund economics cannot be reduced to:

```text
profit × carry %
```

## 6.5 European / whole-fund versus American / deal-by-deal waterfall

Two broad waterfall concepts are commonly discussed:

### Whole-fund / European-style

Carry is generally calculated after sufficient fund-level returns have been achieved across the portfolio.

### Deal-by-deal / American-style

Carry can be distributed based on realised investments earlier in the fund life, subject to contractual protections.

Actual structures vary.

## 6.6 Clawback

A clawback mechanism can require the GP to return excess carry if early carry distributions ultimately exceed the GP's contractual share of cumulative fund profits.

ILPA treats clawback as an important mechanism preventing the GP from retaining more than the agreed share of cumulative profits.[^ilpa-principles-definitions]

## 6.7 GP commitment

GPs commonly commit their own capital to the fund.

The rationale is alignment:

```text
LP capital
   +
GP capital
   ↓
shared exposure to fund outcome
```

ILPA Principles recommend a meaningful GP equity interest and favour cash contribution as an alignment mechanism.[^ilpa-gp-commitment]

Exact percentages vary.

## 6.8 Recycling

Some fund agreements permit certain proceeds to be reinvested rather than immediately distributed.

Recycling can apply to specified categories such as:

- early investment proceeds;
- returned cost;
- transaction proceeds;
- certain fees.

Terms vary materially.

**Vantage implication:** a simple calculation of “fund size minus investments” may not correctly estimate remaining investable capital.

---

# 7. Fund Lifecycle

A simplified closed-end venture fund lifecycle is:

```text
Formation
   ↓
Fundraising
   ↓
First close
   ↓
Investment period
   ↓
Initial investments
   ↓
Follow-ons / reserves
   ↓
Portfolio maturation
   ↓
Exits / liquidity
   ↓
Distributions
   ↓
Extensions / wind-down
```

## 7.1 Investment period

The investment period or commitment period is the contractual period during which the fund can generally make new investments, subject to the LPA.

ILPA defines the commitment period as the period in which the fund can make investments under its LPA.[^ilpa-glossary]

A fund can continue supporting existing portfolio companies after the new-investment period ends, depending on its terms.

## 7.2 Fund term

Traditional venture funds are often structured as long-duration closed-end vehicles.

A frequently encountered market pattern is approximately:

```text
~10-year initial term
+ possible extensions
```

but this is not universal.

Company maturation and exit timing can materially exceed original expectations.

## 7.3 Vintage year

Vintage year is used to group funds formed or beginning investment around a similar time so performance is compared against roughly similar market conditions.

Definitions vary.

ILPA's glossary relates vintage to fund formation and/or first capital draw, while Invest Europe and other industry standards can apply their own precise methodology.[^ilpa-glossary]

**Vantage implication:** store the source definition if comparing externally reported vintage data.

## 7.4 Dry powder

“Dry powder” commonly means capital available for future investment.

But it is not a perfectly standardised accounting term.

It can be approximated differently depending on:

- uncalled commitments;
- reserves;
- recycling;
- fund expenses;
- financing facilities;
- legal investment restrictions.

Vantage should not infer exact dry powder from a headline fund size.

## 7.5 Why fund lifecycle matters for behavioural signals

Suppose an investor makes:

```text
Year 1: 25 new investments
Year 2: 30 new investments
Year 3: 24 new investments
Year 4: 10 new investments
```

A naive signal might conclude:

> “Investor activity is collapsing.”

But possible explanations include:

- the fund's investment period is ending;
- the firm is reserving capital for follow-ons;
- a successor fund has not yet closed;
- cheque sizes increased;
- portfolio concentration increased;
- the team moved from seed to growth;
- the firm is fundraising;
- public disclosure behaviour changed.

**Vantage implication:** fund-cycle context can eventually become an important explanatory variable for Investor Activity Acceleration.

---

# 8. Portfolio Construction

## 8.1 Why venture funds build portfolios

Venture outcomes are highly dispersed.

A small number of investments can drive a disproportionate share of portfolio value.

This creates a portfolio-construction problem:

```text
How many companies?
      ×
Initial cheque size
      ×
Target ownership
      ×
Expected dilution
      ×
Follow-on reserves
      ×
Fund size
```

These variables constrain one another.

## 8.2 Initial cheque size

The initial cheque is the fund's first investment into a company.

It is distinct from:

- the total funding round;
- the investor's total eventual exposure;
- the fund's ownership value;
- future follow-ons.

## 8.3 Target ownership

Many venture firms think explicitly about ownership.

Example:

```text
Fund wants ~10% ownership
Company post-money valuation = $50m

Approximate investment required
to purchase 10% at that financing
≈ $5m
```

Real calculations depend on:

- security terms;
- option-pool changes;
- pre-existing convertibles;
- dilution;
- transaction structure.

## 8.4 Reserves

A fund may reserve capital for future rounds of existing portfolio companies.

Example:

```text
$200m fund

Initial deployment pool     $120m
Follow-on reserves           $60m
Fees / expenses / other      $20m
```

Illustrative only.

Reserve strategy can materially change observable behaviour.

A firm that does fewer new investments but more follow-ons is not necessarily becoming less active economically.

## 8.5 Concentration

Some funds construct broad portfolios.

Others concentrate capital into fewer companies.

Two investors can deploy the same fund size through very different strategies:

```text
Investor A
50 initial companies × smaller ownership

Investor B
15 initial companies × larger ownership
```

Raw deal counts alone cannot tell which strategy is “more active” in every economically relevant sense.

---

# 9. How a VC Investment Happens

A generic workflow is:

```text
Sourcing
   ↓
Initial screening
   ↓
Meetings
   ↓
Diligence
   ↓
Internal debate
   ↓
Investment decision / IC
   ↓
Term sheet
   ↓
Legal documentation
   ↓
Closing
   ↓
Portfolio support / governance
   ↓
Follow-on decisions
   ↓
Exit
```

The actual process varies by firm and deal.

## 9.1 Sourcing

Deals can originate through:

- founder outreach;
- investor networks;
- portfolio referrals;
- other VCs;
- accelerators;
- universities;
- corporate relationships;
- thematic research;
- outbound sourcing;
- data-driven sourcing;
- conferences;
- personal networks.

Sourcing quality is a major part of a VC firm's competitive edge.

## 9.2 Screening

Early screening commonly asks:

- Is the market large enough?
- Is the team exceptional?
- Is there evidence of product-market fit?
- Is the technology differentiated?
- Is the timing right?
- Can the company become large enough to matter to the fund?
- Does the opportunity fit stage / sector / geography?
- Can the fund achieve sufficient ownership?
- Is the price acceptable?

## 9.3 Due diligence

Diligence can include:

- market analysis;
- product assessment;
- technology diligence;
- customer calls;
- reference calls;
- financial review;
- legal diligence;
- intellectual-property analysis;
- security / privacy review;
- regulatory analysis;
- cap-table review;
- competitive analysis;
- founder background;
- cohort / unit economics;
- governance review.

Depth varies strongly by stage.

## 9.4 Investment Committee

Some firms have formal Investment Committees (ICs).

Others use partnership votes or less formal consensus mechanisms.

Therefore:

> “IC approval” is not a universal venture event.

Vantage should not model it as though every firm has one.

## 9.5 Term sheet

A term sheet sets out the principal proposed economic and governance terms of a transaction.

It is generally followed by definitive legal documentation.

For U.S.-style priced venture financings, the NVCA model-document framework includes documents such as:

- Certificate of Incorporation;
- Stock Purchase Agreement;
- Investors' Rights Agreement;
- Voting Agreement;
- Right of First Refusal and Co-Sale Agreement.[^nvca-model-docs]

The existence of multiple documents demonstrates why a funding round is not merely:

```text
amount + date + investor
```

It also establishes rights, governance, ownership, information access, and future transaction mechanics.

---

# 10. Startup Financing Instruments

## 10.1 Common equity

Common stock is the basic residual ownership security in a corporation.

Founders and employees commonly hold common equity, directly or through options.

Common equity usually sits economically behind preferred securities in liquidation priority, subject to the specific capital structure.

## 10.2 Preferred equity

Institutional venture financings commonly issue preferred shares.

Preferred stock can include rights such as:

- liquidation preference;
- conversion rights;
- anti-dilution protection;
- voting rights;
- protective provisions;
- information rights;
- pro rata rights;
- board rights.

Specific rights vary by financing.

## 10.3 Priced equity round

In a priced round, the parties agree a price for the new equity security.

A simplified transaction:

```text
Agreed pre-money valuation     $80m
New primary investment         $20m
                               ----
Post-money valuation          $100m
```

Ignoring other changes, new investors collectively purchase approximately 20% of the post-money company.

However, actual ownership calculations must incorporate the full capitalisation structure.

## 10.4 SAFE

A SAFE is a **Simple Agreement for Future Equity**.

Y Combinator introduced the original SAFE in 2013 as an alternative to convertible notes and later developed the post-money SAFE framework.[^yc-safe]

A SAFE is generally not shares at issuance.

Instead, it is a contractual instrument that converts into equity based on specified future events and terms.

Common variables include:

- valuation cap;
- discount;
- most-favoured-nation provisions;
- pro rata side rights;
- conversion mechanics.

**Vantage implication:** a SAFE financing is capital formation but does not necessarily map cleanly to a traditional priced `FundingRound`.

## 10.5 Convertible note

A convertible note is debt that may convert into equity under specified conditions.

It can involve:

- principal;
- interest;
- maturity;
- valuation cap;
- discount;
- conversion events.

Unlike a SAFE, it is debt.

## 10.6 Venture debt

Venture debt is debt financing provided to venture-backed companies.

It can include:

- term loans;
- revolving facilities;
- equipment financing;
- warrants;
- covenants;
- interest;
- maturity.

It is economically different from equity financing and can coexist with an equity round.

**Vantage implication:** do not automatically categorise every “$50m financing” as an equity funding round.

## 10.7 Tranched financing

A financing can be committed in tranches, with capital funded over time based on:

- dates;
- milestones;
- investor discretion;
- company performance.

NVCA's updated model documents explicitly incorporate mechanics for tranched financings.[^nvca-model-docs]

Therefore:

```text
headline committed round size
```

may differ from:

```text
cash funded at initial closing
```

---

# 11. Primary versus Secondary Capital

This distinction is foundational.

## 11.1 Primary transaction

In a primary financing, the company issues new securities and receives the proceeds.

```text
Investor cash
     ↓
Company
     ↓
New securities
     ↓
Investor
```

The company gains capital.

Existing holders are diluted unless they participate or other adjustments apply.

## 11.2 Secondary transaction

In a secondary transaction, an existing shareholder sells existing securities.

```text
Buyer cash
    ↓
Existing shareholder

Existing shares
    ↓
Buyer
```

The company generally does **not** receive the sale proceeds.

## 11.3 Mixed primary + secondary round

A transaction can contain both.

Example:

```text
Announced transaction: $100m

$70m primary capital → company
$30m secondary       → existing shareholders
```

Calling this simply “company raised $100m” would be economically misleading.

**Future Vantage implication:** eventually distinguish:

```text
transaction_total
primary_amount
secondary_amount
```

when evidence supports it.

Do not invent the split when it is undisclosed.

---

# 12. Financing Stages

## 12.1 Stage is useful but fuzzy

Common startup-market labels include:

```text
Pre-seed
Seed
Series A
Series B
Series C
Series D+
Late-stage
Growth
Pre-IPO
```

These labels are not governed by a universal global standard.

They describe market convention and company maturity imperfectly.

A Series A in one market cycle can resemble a Series B in another by:

- amount;
- valuation;
- revenue;
- headcount;
- product maturity.

## 12.2 Alternative institutional stage definitions

Invest Europe uses development-stage concepts such as:

- Seed;
- Start-up;
- Later-stage venture;
- Growth.[^invest-europe-stages]

Its definitions are based more on company development than lettered financing rounds.

That demonstrates why:

```text
raw announced round label
```

and:

```text
canonical analytical stage
```

should remain distinct.

### Current Vantage mapping

Vantage already retains:

```text
round_type
canonical_round_type
```

This is the correct direction.

The raw evidence should not be destroyed merely because an analytical taxonomy exists.

## 12.3 Extensions and bridges

Companies can raise:

- seed extensions;
- Series A extensions;
- bridge rounds;
- insider rounds;
- continuation financings;
- unpriced convertible rounds.

These may not represent a clean progression in stage.

**Vantage implication:** stage-change analytics need to avoid interpreting every sequential transaction as a strategy move up the stage ladder.

---

# 13. Valuation and Ownership

## 13.1 Pre-money and post-money

At its simplest:

```text
Post-money valuation
=
Pre-money valuation
+
New primary capital
```

Example:

```text
Pre-money       $80m
New money       $20m
Post-money     $100m
```

This identity can become more complicated in practice due to:

- secondary components;
- option-pool changes;
- SAFEs;
- convertible notes;
- warrants;
- tranched closings;
- different security rights.

## 13.2 Price per share

A priced round ultimately establishes a price for a defined security.

Headline company valuation is an abstraction built from:

- negotiated price;
- share count;
- treatment of options;
- converted securities;
- fully diluted assumptions.

Different calculations can produce different “valuation” numbers.

## 13.3 Cap table

A capitalisation table records the securities and ownership interests in a company.

It can include:

- founder common stock;
- employee common stock;
- preferred shares by series;
- options;
- unallocated option pool;
- warrants;
- SAFEs;
- convertible notes;
- other convertible instruments.

ILPA's glossary describes a cap table as a record of the securities issued by a company and their associated capitalisation.[^ilpa-glossary]

## 13.4 Fully diluted ownership

“Fully diluted” generally attempts to reflect ownership assuming relevant options, warrants, and convertible securities are exercised or converted.

Definitions can vary by transaction document.

Therefore a public statement that an investor “owns 10%” can require context.

## 13.5 Dilution

When a company issues new shares, existing shareholders' percentage ownership generally falls unless they buy enough new shares or other contractual mechanisms apply.

Example:

```text
Before financing:
Investor owns 10 / 100 shares = 10%

Company issues 25 new shares.

After financing:
Investor owns 10 / 125 shares = 8%
```

Economic value may still rise even while percentage ownership falls.

## 13.6 Pro rata rights

Pro rata rights can allow an investor to participate in future financing so it can maintain some or all of its ownership percentage, subject to the documents.

A follow-on investment can therefore mean:

- maintaining ownership;
- increasing ownership;
- participating below pro rata;
- opportunistically adding capital.

Those behaviours are not equivalent.

## 13.7 Option pools

Companies reserve shares for employee options.

Option-pool increases can affect ownership economics and financing negotiations.

This is one reason simplistic valuation formulas can mislead.

---

# 14. Liquidation Preferences and Security Economics

## 14.1 Why headline valuation is not enough

Two investors can invest in the same company at the same headline valuation but own securities with different economic rights.

Venture securities can differ in:

- liquidation priority;
- participation;
- conversion;
- dividends;
- anti-dilution;
- redemption;
- voting;
- protective provisions.

Therefore:

> **Company headline valuation is not equivalent to the fair value of every security.**

## 14.2 Liquidation preference

A liquidation preference determines how proceeds are distributed in specified liquidity events before or instead of common-stock participation.

A simplified non-participating 1x preference might allow an investor to choose between:

```text
Receive original preference amount
             OR
Convert to common and take common-share proceeds
```

The actual documents control.

## 14.3 Participating preferred

Participating preferred can allow the holder to:

1. receive a preference; and
2. participate further in remaining proceeds,

subject to caps or specific terms.

This can materially change outcomes.

## 14.4 Seniority

Different preferred series can rank:

- senior;
- pari passu;
- junior;

relative to other securities.

A company's exit value therefore does not translate mechanically into pro-rata shareholder proceeds.

## 14.5 Anti-dilution

Anti-dilution provisions can adjust conversion economics when shares are issued at lower prices.

Common conceptual forms include:

- weighted-average anti-dilution;
- full-ratchet anti-dilution.

The details are legal-document specific.

---

# 15. Lead Investors, Participants and Syndicates

## 15.1 Lead investor

A lead investor commonly plays a larger role in:

- negotiating price and terms;
- diligence;
- coordinating the round;
- setting the financing structure;
- taking a board seat;
- signalling quality to other investors.

But the term is not perfectly standardised.

There can be:

- one lead;
- co-leads;
- no explicitly announced lead.

### Current Vantage mapping

Vantage already separates:

```text
investors
lead_investors
```

on canonical funding rounds.

This is valuable and should remain.

## 15.2 Participant

A participant invests in the round without necessarily leading it.

Participation alone says less about:

- cheque size;
- ownership;
- governance influence;
- conviction;
- decision timing.

## 15.3 New versus existing investor

A round may include:

- new investors;
- existing investors;
- both.

This distinction can be behaviourally informative.

Example:

```text
Investor participates in first company round
→ new relationship

Investor invests again two years later
→ follow-on relationship
```

## 15.4 Syndicate

A syndicate is a group of investors participating in the same deal.

ILPA's glossary uses co-investment / syndication concepts for transactions involving multiple investors.[^ilpa-glossary]

Potential Vantage graph:

```text
Investor A ─┐
Investor B ─┼── Financing Event ── Company
Investor C ─┘
```

Across time:

```text
Investor A ── repeated co-investment ── Investor B
```

can become a behavioural relationship.

But repeated co-investment does not automatically prove:

- formal partnership;
- shared strategy;
- information sharing;
- causal influence.

---

# 16. Follow-on Investing and Reserves

## 16.1 Follow-on investment

A follow-on occurs when an existing investor invests again in a company it already backed.

Possible reasons include:

- maintaining ownership;
- increasing ownership;
- supporting a strong performer;
- protecting a distressed company;
- participating in an inside round;
- exercising contractual rights.

Therefore:

> **Follow-on ≠ automatically positive conviction.**

Context matters.

## 16.2 Insider round

An insider round is primarily funded by existing investors.

It can signal:

- strong internal conviction;
- speed;
- lack of need for new investors;
- difficult external fundraising;
- bridge financing.

The same observable structure can support different interpretations.

## 16.3 Reserves and activity signals

A fund with large reserves can appear to shift from:

```text
many new-company investments
```

to:

```text
fewer new companies
+
larger follow-ons
```

A Vantage investor-activity signal should eventually distinguish these dimensions.

---

# 17. Governance and Board Involvement

VC investing often includes governance rights.

Possible rights include:

- board seat;
- board observer;
- voting rights;
- protective provisions;
- information rights;
- approval rights over major actions.

Not every investor receives these rights.

Board participation can be a meaningful behavioural signal, but reliable public data is often incomplete.

**Future Vantage implication:** if board-role data is added, it should be evidence-backed and temporally scoped because board membership changes.

---

# 18. SPVs, Opportunity Funds and Co-Investment Vehicles

## 18.1 Special Purpose Vehicle

An SPV can pool capital for a specific investment or set of investments.

Example:

```text
Main Fund
   │
   ├── invests $8m
   │
SPV / sidecar
   │
   └── invests $12m
```

Public announcements may attribute both to the same investment firm.

This can obscure which legal vehicle actually invested.

## 18.2 Opportunity fund

An opportunity fund is commonly a separate vehicle used to invest additional capital in later-stage or high-performing portfolio companies.

This can allow a firm to:

- protect ownership;
- invest larger amounts;
- avoid concentration constraints in a core fund;
- continue backing mature winners.

## 18.3 Co-investment vehicles

LPs may sometimes invest alongside a main fund through co-investment structures.

The economics can differ from the main fund.

**Vantage implication:** the public investment firm should remain the primary behavioural entity for now, but future fund-level precision may require vehicle attribution.

---

# 19. Secondary Markets and Liquidity

Private-company ownership is illiquid, but liquidity can occur before IPO or acquisition.

## 19.1 Direct secondary

An existing shareholder sells shares to another investor.

Potential sellers:

- founders;
- employees;
- early angels;
- VC funds;
- other institutions.

## 19.2 Tender offer

A company or investor may organise a structured process allowing eligible shareholders to sell shares.

Tender offers can provide employee/founder liquidity without a public listing.

## 19.3 Fund secondary

An LP can sell its interest in a private fund to another investor.

This is different from selling shares in a portfolio company.

## 19.4 GP-led secondary / continuation vehicle

A fund manager can structure liquidity around portfolio assets through a new continuation vehicle.

This is more common in broader private equity but increasingly relevant across private markets.

## 19.5 Vantage implication

“Secondary” requires object-level clarity:

```text
Company-share secondary
≠
LP fund-interest secondary
≠
GP-led continuation transaction
```

Do not create one generic secondary event without specifying what changed ownership.

---

# 20. Exits

## 20.1 Acquisition

A company can be acquired for:

- cash;
- shares;
- mixed consideration;
- other structures.

The announced transaction value may differ from equity value received by shareholders after:

- debt;
- liquidation preferences;
- transaction costs;
- earn-outs;
- escrows;
- contingent consideration.

## 20.2 IPO

An IPO lists shares on a public market.

An IPO does not necessarily mean existing VC investors immediately realise their investment.

They can remain subject to:

- lock-ups;
- selling restrictions;
- market conditions.

Fund distributions can occur later.

## 20.3 Direct listing and other public-market paths

Companies can become publicly traded through structures other than a traditional IPO.

The relevant domain concept is broader:

```text
private → public liquidity / market access
```

## 20.4 Write-off / shutdown

Not every company exits successfully.

A company can:

- wind down;
- enter insolvency;
- sell assets;
- return little or nothing to shareholders.

For performance analysis, negative outcomes matter as much as winners.

---

# 21. Venture Fund Performance

## 21.1 Activity is not performance

This distinction is critical for Vantage.

```text
Investor made 40 investments
```

tells us about activity.

It does not tell us:

```text
Return on invested capital
```

To measure performance properly, one generally needs:

- investment cost;
- ownership;
- timing of cash flows;
- distributions;
- remaining fair value;
- fees;
- carry;
- fund-level cash flows.

Much of this information is private.

## 21.2 Gross versus net

### Gross performance

Performance before fund-level fees, carried interest, and some expenses, depending on the metric and reporting convention.

### Net performance

Performance to LPs after applicable fund economics.

ILPA distinguishes gross and net IRR in its reporting terminology.[^ilpa-glossary]

## 21.3 MOIC

**Multiple on Invested Capital (MOIC)** broadly compares value generated with invested cost.

At deal level:

```text
MOIC =
Realised + remaining value
---------------------------
Invested cost
```

Example:

```text
Invested cost     $10m
Current value     $30m

MOIC              3.0x
```

MOIC ignores time.

A 3.0x return in three years and a 3.0x return in twelve years have very different annualised economics.

## 21.4 IRR

**Internal Rate of Return (IRR)** is a time-sensitive return measure based on cash flows.

It is the discount rate that sets the net present value of relevant cash flows to zero.

IRR can be sensitive to:

- timing;
- early distributions;
- subscription facilities;
- interim valuations;
- irregular cash flows.

It should never be interpreted without understanding the cash-flow convention.

## 21.5 DPI

**Distributed to Paid-In Capital (DPI)** measures realised distributions relative to paid-in capital.

Conceptually:

```text
DPI =
Cumulative distributions
------------------------
Paid-in capital
```

Higher DPI indicates more capital has actually been returned.

## 21.6 RVPI

**Residual Value to Paid-In Capital (RVPI)** measures remaining unrealised value relative to paid-in capital.

```text
RVPI =
Residual NAV
------------
Paid-in capital
```

## 21.7 TVPI

**Total Value to Paid-In Capital (TVPI)** combines realised and residual value:

```text
TVPI =
Distributions + residual value
------------------------------
Paid-in capital
```

Conceptually:

```text
TVPI = DPI + RVPI
```

ILPA defines TVPI as remaining value plus distributions relative to paid-in capital.[^ilpa-glossary]

## 21.8 PME

**Public Market Equivalent (PME)** refers to families of methods that compare private-market cash flows with a public-market benchmark.

There is not one universal PME calculation.

Vantage should not introduce a single `pme` field without defining methodology.

## 21.9 J-curve

Private-fund performance often exhibits a “J-curve” pattern:

```text
Early fund life:
fees + immature investments
       ↓
weak / negative reported return

Later:
portfolio appreciation + exits
       ↓
potentially stronger returns
```

This is a tendency, not a guaranteed shape.

## 21.10 Vintage-year comparison

Fund returns are commonly compared with funds of similar vintage because market conditions differ dramatically by investment period.

A 2021 vintage fund and a 2009 vintage fund entered very different environments.

---

# 22. Private-Company Valuation

## 22.1 Financing valuation versus fair value

A financing round establishes a transaction price for a specific security at a specific point in time.

A fund later needs to estimate the fair value of its investment for reporting.

These are related but not identical tasks.

## 22.2 IPEV fair-value framework

The International Private Equity and Venture Capital Valuation Guidelines are a major industry reference for private-capital valuation.

The 2025 IPEV Guidelines define the objective as determining **Fair Value** and emphasise:

- valuation at each measurement date;
- market-participant assumptions;
- current facts and circumstances;
- calibration;
- appropriate valuation techniques;
- the principle that a recent transaction price is not automatically fair value forever.[^ipev-guidelines]

This matters enormously for Vantage.

A funding article stating:

```text
Company valued at $1bn
```

does not prove:

```text
Investor's stake fair value = ownership × $1bn
```

because:

- security rights differ;
- time has passed;
- market conditions change;
- ownership may be unknown;
- dilution may have occurred;
- preference structures matter.

## 22.3 Unrealised marks

Funds periodically mark portfolio investments.

These marks can influence:

- NAV;
- TVPI;
- RVPI;
- fundraising narratives;
- LP portfolio reporting.

But unrealised value is not cash.

## 22.4 Realised value

Realised value results from actual liquidity such as:

- sale;
- distribution;
- repayment;
- other monetisation.

DPI therefore carries a different informational meaning from RVPI.

---

# 23. LP Reporting and Fund Operations

Private-market funds produce extensive operational data that is rarely public.

Typical categories include:

- capital-account statements;
- capital calls;
- distributions;
- fees;
- expenses;
- carried interest;
- NAV;
- portfolio-company data;
- valuations;
- investment schedules;
- fund performance;
- compliance reporting.

ILPA has developed standardised Reporting and Performance Templates to improve consistency around fees, expenses, carried interest, cash flows, and return calculations.[^ilpa-reporting][^ilpa-performance]

This illustrates an important information asymmetry:

```text
What LPs / GPs know privately
             ≫
What public web sources disclose
```

Vantage's public-data intelligence must therefore be explicit about the boundary of observation.

---

# 24. Regulation: High-Level Grounding

## 24.1 Why Vantage needs regulatory literacy

Regulation affects:

- what funds are;
- how they raise capital;
- how advisers register;
- what data is public;
- what data is confidential;
- what companies file;
- what terminology means.

But Vantage should not become a legal-rule engine unless the product requires it.

## 24.2 United States — private funds

In the United States, private funds generally rely on exclusions from registration as investment companies and raise fund interests through securities-law exemptions.

The SEC distinguishes:

```text
Fund
Adviser
Capital raise
```

as different regulatory layers.[^sec-private-funds]

This mirrors an important Vantage conceptual separation.

## 24.3 Investment advisers and Form ADV

Investment advisers file **Form ADV** to register or report with the SEC and/or states.

The SEC's IAPD service makes public information about advisers and certain private funds available from these filings.[^sec-iapd]

Potential Vantage uses:

- canonical adviser identity;
- legal firm names;
- regulatory status;
- business operations;
- private-fund references;
- historical firm metadata.

Form ADV is therefore a strong candidate for a future structured regulatory adapter.

## 24.4 Regulation D and Form D

**Form D** is a notice filing for offerings relying on Regulation D.

The SEC states that Form D is filed after the first sale of securities and is publicly available through EDGAR.[^sec-form-d]

Crucially:

> **Form D is evidence of an exempt securities offering. It is not automatically evidence of a venture funding round.**

A filing can relate to:

- startup financing;
- a private fundraise;
- real estate;
- private equity;
- debt;
- pooled investment vehicles;
- other exempt offerings.

Therefore:

```text
Form D
   ↓
authoritative evidence of filing / offering facts
   ≠
automatic FundingRound
```

This is exactly how a future Vantage regulatory adapter should behave.

## 24.5 Form PF

Form PF contains information about certain private funds but is generally confidential and not an investor-facing public dataset.[^sec-form-pf]

**Vantage implication:** not every high-value regulatory dataset is publicly usable for entity-level intelligence.

## 24.6 European Union

The EU's **Alternative Investment Fund Managers Directive (AIFMD)** regulates managers of alternative investment funds, subject to its scope and national implementation.[^eu-aifmd]

The **EuVECA** regime establishes a designation and regulatory framework for qualifying European venture-capital funds.[^eu-euveca]

Again:

```text
European VC fund
```

in ordinary language does not automatically mean:

```text
EuVECA
```

as a legal designation.

## 24.7 United Kingdom

The UK has its own post-Brexit alternative-investment-fund regime, supervised in relevant areas by the FCA.

The FCA distinguishes authorised and registered AIFMs and includes registered venture-capital-fund manager categories within its framework.[^fca-aifm]

UK rules are evolving, and in 2026 the FCA is consulting on reforms to the UK AIFM regime.[^fca-aifm-reform]

**Vantage implication:** regulatory attributes should be time-stamped and jurisdiction-specific.

---

# 25. Public Information Sources in Venture Capital

Vantage's intelligence quality depends on understanding not just what a source says, but **what type of source it is capable of being**.

## 25.1 First-party investor sources

Examples:

- portfolio announcements;
- investment theses;
- fund announcements;
- partner essays;
- portfolio pages.

Strengths:

- direct;
- often authoritative about the firm's own public statement;
- useful for attribution;
- useful for strategy language;
- valuable for historical investor behaviour.

Weaknesses:

- selective;
- promotional;
- can omit investments;
- may remove old pages;
- may publish after the actual transaction;
- may describe firm-level participation without fund-level precision.

**Vantage rule:** first-party investor evidence is high precision for what the firm publicly claims, not proof of complete real-world activity.

## 25.2 First-party company sources

Examples:

- financing announcements;
- press releases;
- blog posts;
- investor pages.

Strengths:

- often direct on round amount and participants;
- can clarify product, geography, and use of proceeds.

Weaknesses:

- marketing language;
- incomplete terms;
- inconsistent round labels;
- can mix primary and secondary capital;
- can omit valuation.

## 25.3 Regulatory sources

Examples:

- SEC Form D;
- Form ADV / IAPD;
- Companies House;
- national company registries;
- EU / national fund registers.

Strengths:

- authoritative filing;
- structured;
- stable identifiers;
- legal names;
- dates;
- potentially machine-readable.

Weaknesses:

- filing semantics can be narrower than commercial meaning;
- amendments complicate interpretation;
- filing date can differ from economic event date;
- not every transaction is filed publicly;
- regulatory categories do not map one-to-one to product concepts.

## 25.4 Editorial sources

Examples:

- specialist technology media;
- financial press;
- trade publications.

Strengths:

- contextual;
- can aggregate multiple sources;
- can identify investors and market meaning;
- can reveal transactions not published on investor websites.

Weaknesses:

- secondary reporting;
- errors;
- syndicated duplication;
- paywalls;
- corrections;
- headline compression;
- reliance on unnamed sources.

## 25.5 Commercial structured data

Examples include specialist private-market databases.

Strengths:

- broad coverage;
- normalised entities;
- transaction histories;
- structured query;
- often human-curated.

Weaknesses:

- licensing restrictions;
- cost;
- opaque methodology;
- conflicting classifications;
- survivorship / coverage bias;
- provider-specific identifiers;
- uncertain provenance for individual fields.

**Vantage principle:** commercial data can enrich Vantage but should not erase provenance or become unquestioned canonical truth.

---

# 26. Evidence Quality Is Multidimensional

There is no single universal source-quality ranking.

A source can be authoritative for one claim and weak for another.

Example:

```text
Form D
```

may be highly authoritative for:

- issuer legal name;
- filing existence;
- offering amount fields;
- filing date.

But weak for:

- whether the market calls it a Series A;
- which investor led;
- final transaction size;
- company sector;
- why the investment matters.

A useful conceptual evidence scorecard is:

| Dimension | Question |
|---|---|
| Authority | Who is making the claim? |
| Directness | Is this first-hand or reported through others? |
| Specificity | Does it directly support the exact field/event? |
| Temporal fit | Does the date correspond to the economic event? |
| Completeness | Could material information be omitted? |
| Independence | Is this corroboration or duplicated syndication? |
| Stability | Is the source durable and recoverable? |
| Licensing | Can Vantage legally store/use the information? |
| Machine readability | Can it be reliably extracted? |
| Historical continuity | Can comparable evidence be obtained over time? |

This is a better model than:

```text
regulatory > first-party > media
```

for every possible claim.

---

# 27. Current Project Vantage Domain Model

As of Domain Grounding V1, Vantage's current canonical model already contains several strong domain boundaries.

## 27.1 Company

Current company-level concepts include:

- name;
- website;
- description;
- raw sector;
- canonical sector;
- headquarters;
- city;
- country;
- founded year.

This is an appropriate durable entity.

## 27.2 Investor

Current investor-level concepts include:

- name;
- website;
- description;
- headquarters.

For now, this functions primarily as the canonical public investment organisation / firm.

That is appropriate for the investor-behaviour product wedge.

Future legal-entity precision should not be forced into this model prematurely.

## 27.3 Fund

Current `Fund` is explicitly linked to an `Investor` and carries:

- name;
- strategy;
- geography;
- vintage year.

This correctly recognises:

```text
investment firm ≠ fund
```

## 27.4 FundingRound

Current financing-event concepts include:

- company;
- round amount;
- currency;
- raw round type;
- canonical round type;
- announcement date;
- investors;
- lead investors;
- multiple evidence articles.

This is a strong first event primitive.

## 27.5 FundClose

Current fund-close concepts include:

- fund;
- amount;
- currency;
- close type;
- announcement date;
- evidence.

This correctly separates:

```text
company raises capital
```

from:

```text
investment fund raises commitments
```

---

# 28. What Vantage Does Not Yet Model — and Should Not Rush to Model

The domain is much larger than the current schema.

Potential future concepts include:

```text
Person
General Partner legal entity
Investment Adviser
Management Company
Limited Partner
Fund Commitment
Capital Call
Distribution
Security
SAFE
Convertible Note
Venture Debt
Ownership Position
Valuation Observation
Board Seat
Pro Rata Right
Follow-on Participation
Secondary Transaction
Acquisition
IPO
Write-off
LP Interest
SPV
Co-investment Vehicle
Fund Performance Observation
```

This does **not** mean Vantage should add all of these.

The correct rule is:

> Add a domain object when it is necessary to represent valuable observable truth that the current model cannot express safely.

---

# 29. A Future Vantage Ontology — Conceptual, Not an Implementation Plan

A richer future system could eventually resemble:

```text
ORGANISATIONS
│
├── Company
├── Investment Firm
├── Adviser
├── Management Company
└── LP Organisation
         │
         ▼
PEOPLE
│
├── Founder
├── Partner
├── Board Member
└── Investment Professional
         │
         ▼
FUND VEHICLES
│
├── Venture Fund
├── Growth Fund
├── Opportunity Fund
└── SPV
         │
         ▼
EVENTS
│
├── Company Financing
├── Fund Close
├── Secondary
├── Acquisition
├── IPO
├── Shutdown
└── Governance Change
         │
         ▼
RELATIONSHIPS / POSITIONS
│
├── Investor Participation
├── Lead Role
├── Fund Management
├── Board Role
├── Ownership
└── LP Commitment
         │
         ▼
OBSERVATIONS
│
├── Valuation
├── Strategy Claim
├── Fund Performance
└── Portfolio Metric
```

The important architectural distinction is:

```text
ENTITY
something that persists

EVENT
something that happened

RELATIONSHIP
a connection between entities

OBSERVATION
a measured/reported state at a point in time

SIGNAL
an analytical conclusion derived from history
```

These should not collapse into one generic `Event` table merely for abstraction.

---

# 30. Canonical Event Types Vantage May Eventually Need

## 30.1 Company Financing Event

Already substantially implemented.

Potential extensions:

- priced equity;
- SAFE financing;
- convertible note;
- venture debt;
- bridge;
- extension;
- mixed primary / secondary;
- tranche.

## 30.2 Fund Formation / Fund Close Event

Already substantially implemented.

Potential extensions:

- target announced;
- first close;
- interim close;
- final close;
- successor fund;
- strategy / mandate;
- fund size changes.

## 30.3 Liquidity Event

Potential future types:

- acquisition;
- IPO;
- direct listing;
- company secondary;
- tender;
- write-off.

## 30.4 Governance Event

Potential future types:

- board appointment;
- board departure;
- executive appointment;
- partner departure;
- investment-team change.

These should only be added if they serve intelligence use cases.

---

# 31. Relationships Are Often More Valuable Than Extra Event Types

Consider a single funding event.

A naive record is:

```text
Company = X
Amount = $50m
Stage = Series B
```

A richer behavioural representation is:

```text
FundingEvent
├── Company = X
├── Stage = Series B
├── Amount = $50m
├── Investor A
│   ├── role = lead
│   ├── relationship = new
│   └── prior portfolio exposure = none
├── Investor B
│   ├── role = participant
│   ├── relationship = follow-on
│   └── prior rounds = Seed, Series A
└── Evidence
    ├── company announcement
    ├── investor announcement
    └── publication
```

This is where Vantage's intelligence advantage can develop.

---

# 32. Domain Implications for Vantage Signals

## 32.1 Sector Momentum

Current concept:

```text
How is observed financing activity changing by sector?
```

Key confounders:

- source cohort change;
- canonical-sector taxonomy change;
- stage mix;
- very large multi-investor rounds;
- sparse sectors;
- catch-all taxonomy values;
- fund-cycle effects.

Correct principle:

> Measure comparable canonical events first; interpret second.

## 32.2 Investor Activity Acceleration

A naive metric:

```text
current deal count
vs
previous deal count
```

is useful but incomplete.

Eventually distinguish:

- new-company investments;
- follow-ons;
- lead investments;
- total participations;
- stage mix;
- sector mix;
- company count;
- fund-cycle context.

Possible interpretation table:

| Observation | Possible meanings |
|---|---|
| More total deals | higher activity, better disclosure, wider source coverage |
| More new-company deals | broader origination / deployment |
| More follow-ons | reserve deployment / portfolio support |
| More leads | stronger ownership/governance posture |
| Fewer deals + later stages | larger-cheque strategy |
| Fewer new deals + more follow-ons | mature fund cycle |

Do not collapse these into one opaque “activity score”.

## 32.3 Stage Shift

A stage shift can reflect:

- genuine strategy movement;
- successor fund;
- fund-size growth;
- market-stage inflation;
- company-round labels;
- portfolio follow-ons;
- temporary opportunity set.

A strategy claim should require persistence across multiple events, not one anomalous round.

## 32.4 Lead-Activity Shift

Lead behaviour can be more informative than participation count because leading often implies deeper involvement.

But public announcements do not always identify leads consistently.

Therefore coverage must be measured.

## 32.5 Strategy Change

Potential evidence:

```text
Observed investment history
        +
stage distribution
        +
sector distribution
        +
geography
        +
new vs follow-on
        +
lead behaviour
        +
public thesis statements
        +
fund strategy
```

A robust strategy-change signal should distinguish:

```text
what investor says
```

from:

```text
what investor does
```

and then compare the two.

---

# 33. “Conviction” Is Not a Directly Observable Variable

Venture commentary often uses the word **conviction**.

But Vantage should treat conviction as an inferred construct.

Potential proxies:

- lead role;
- repeated follow-ons;
- ownership increase;
- board involvement;
- larger known cheque;
- repeated thematic investment;
- concentration;
- public thesis.

Each is imperfect.

Therefore Vantage should prefer language such as:

> “Observed behaviour consistent with increased focus”

over:

> “Investor conviction increased”

unless the methodology is explicit.

---

# 34. Capital Deployed Is a Dangerous Metric

This deserves an explicit invariant.

Suppose:

```text
Company raises $100m
Investors:
- Investor A
- Investor B
- Investor C
```

Without cheque-level disclosure:

```text
Investor A deployed $100m   ❌
Investor B deployed $100m   ❌
Investor C deployed $100m   ❌
```

Even:

```text
Each deployed $33.3m        ❌
```

is unsupported.

The only safe statement is:

```text
Each participated in a $100m financing.
```

### Vantage invariant

> **Never treat total financing-round size as individual investor capital deployed.**

The existing investor-intelligence logic already follows this principle and it should remain a hard semantic rule.

---

# 35. Geography Is Also Ambiguous

A company can have:

- legal domicile;
- headquarters;
- founding city;
- principal operations;
- primary market;
- engineering centre;
- incorporation jurisdiction.

An investor can have:

- legal headquarters;
- offices;
- fund domicile;
- investment mandate;
- team geography.

Therefore:

```text
Company country
```

is not automatically:

```text
market served
```

and:

```text
Investor headquarters
```

is not automatically:

```text
investment geography
```

Vantage should maintain explicit definitions for geographic analytics.

---

# 36. Sector Is a Taxonomy, Not an Objective Fact

Companies are multi-dimensional.

A company can reasonably be described as:

```text
AI
Cybersecurity
Developer Tools
Fintech Infrastructure
Enterprise Software
```

depending on taxonomy and analytical goal.

Therefore:

- preserve raw source labels;
- maintain canonical analytical taxonomy;
- version taxonomy changes;
- avoid interpreting taxonomy reclassification as market change.

---

# 37. Time Is More Complicated Than Publication Date

Potential dates include:

- signing date;
- first closing date;
- final closing date;
- funds-transfer date;
- announcement date;
- article publication date;
- regulatory filing date;
- amendment date;
- effective date.

A source publication date is not always the economic-event date.

Vantage should eventually distinguish:

```text
observed_at
published_at
announced_at
effective_at
filed_at
```

where the source supports them.

---

# 38. The Importance of Provenance

Every important canonical field should conceptually be answerable with:

> Why do we believe this?

Example:

```text
Funding round
Company: Acme
Amount: $30m
Stage: Series B
Lead: Example Ventures
```

Desired traceability:

```text
Amount
 └── Company announcement

Stage
 ├── Company announcement
 └── Investor announcement

Lead
 └── Investor announcement

Event identity
 ├── company announcement
 ├── investor announcement
 └── editorial corroboration
```

This is stronger than treating provenance only at whole-record level.

Vantage does not need claim-level provenance immediately, but the architecture should not prevent it.

---

# 39. Domain Invariants for Vantage

These should be treated as enduring semantic guardrails.

## Entity invariants

1. **Investment firm ≠ fund.**
2. **Fund ≠ adviser.**
3. **Organisation ≠ person.**
4. **Company brand ≠ necessarily legal issuer.**
5. **Alias resolution must not erase canonical identity history.**

## Event invariants

6. **Company financing ≠ fund close.**
7. **Funding announcement ≠ necessarily one simple priced round.**
8. **Form D ≠ automatically a funding round.**
9. **First close ≠ final close.**
10. **Announcement date ≠ necessarily transaction closing date.**
11. **Primary financing ≠ secondary transaction.**

## Capital invariants

12. **Round size ≠ investor cheque.**
13. **Fund size ≠ invested capital.**
14. **Committed capital ≠ paid-in capital.**
15. **Uncalled commitments ≠ exact investable dry powder.**
16. **Company valuation ≠ investor stake fair value.**

## Behaviour invariants

17. **Participation ≠ lead.**
18. **Follow-on ≠ automatically positive conviction.**
19. **Deal count ≠ capital deployed.**
20. **Activity ≠ performance.**
21. **Observed activity ≠ complete market activity.**
22. **Public thesis ≠ observed strategy.**

## Analytical invariants

23. **Raw taxonomy ≠ canonical taxonomy.**
24. **Stage label ≠ universal maturity definition.**
25. **Coverage change must not masquerade as behavioural change.**
26. **Signal must remain traceable to measured change and evidence.**
27. **Unknown / catch-all taxonomy should not become unsupported intelligence.**

---

# 40. Domain Anti-Patterns Vantage Should Avoid

## 40.1 FundingRound as universal event

Bad:

```text
Everything notable → FundingRound
```

Correct:

```text
Financing event
Fund close
Exit
Secondary
Governance change
...
```

when product value justifies each.

## 40.2 Generic Event too early

Also bad:

```text
Event
type = anything
payload = JSON
```

for every domain concept.

This removes useful domain constraints and creates an opaque schema.

## 40.3 Over-precise unsupported fields

Bad:

```text
investor_cheque = 12,500,000
```

because an article says:

```text
company raised $25m from Investor A and Investor B
```

Correct:

```text
round_amount = 25m
investors = [A, B]
individual_cheques = unknown
```

## 40.4 Treating marketing claims as fact

Bad:

```text
Investor strategy = "AI-first"
```

forever because one 2025 website page said so.

Correct:

```text
strategy claim
source
effective / observed date
+
behavioural history
```

## 40.5 Treating a provider taxonomy as reality

Bad:

```text
Provider says "Fintech"
→ eternal canonical truth
```

Correct:

```text
raw classification
+
Vantage canonical taxonomy
+
taxonomy version
```

---

# 41. Recommended Domain Expansion Order

If future product requirements justify new concepts, a sensible order is:

## Tier 1 — near the current wedge

```text
Financing subtype
New vs follow-on participation
Primary vs secondary financing component
Fund strategy / successor relationship
Known investor cheque when explicitly disclosed
```

## Tier 2 — major intelligence expansion

```text
Exit / acquisition
IPO
Company secondary
Board / governance role
Investment professional
SPV / vehicle attribution
```

## Tier 3 — deeper private-markets intelligence

```text
LP
Fund commitment
Capital call
Distribution
Ownership snapshot
Fund performance
Security-level economics
```

Tier 3 data is substantially less public and may require customer/private-data workflows or licensed sources.

---

# 42. Recommended Data-Source Expansion for Vantage

The current web observation network should eventually expand by **evidence class**, not source count.

A rational progression is:

```text
CURRENT
Investor first-party web
Company/publication evidence
        ↓
NEXT
Public regulatory structured data
        ↓
THEN
Other structured authoritative feeds
        ↓
OPTIONAL
Commercial licensed data
        ↓
LATER
Private customer / LP / CRM data
```

## 42.1 First structured regulatory pilot: SEC data

A good architectural pilot could combine:

### Form ADV / IAPD

Useful for:

- investment adviser identity;
- firm metadata;
- private-fund relationships;
- regulatory history.

### Form D / EDGAR

Useful for:

- offering notices;
- issuer identity;
- filing dates;
- offering fields.

But the adapter must implement:

```text
REGULATORY RECORD
      ↓
NORMALIZED EVIDENCE
      ↓
SEMANTIC CLASSIFICATION
      ↓
VALIDATION
      ↓
RECONCILIATION
      ↓
CANONICAL EVENT
```

not:

```text
Form D
  ↓
FundingRound
```

---

# 43. A Proposed Vantage Evidence Envelope

Without committing to implementation, future adapters would benefit from normalising source observations into a common conceptual envelope:

```text
source_family
source_name
source_type

external_id
source_url

observed_at
published_at
filed_at
effective_at

document_type

raw_payload_reference
content_hash

issuer / publisher identity

extracted claims

jurisdiction

licensing / usage metadata

provenance
```

Not every source populates every field.

The important principle is that **source-specific acquisition ends before canonical truth begins**.

---

# 44. How Domain Knowledge Should Affect Product Design

The best Vantage interface should not simply display database objects.

It should answer professional questions.

Example:

```text
WHAT CHANGED?
Investor A increased Series A lead activity.

WHO DROVE IT?
Investor A led 7 comparable rounds vs 3 previously.

WHAT KIND OF CHANGE?
Mostly new-company investments in cybersecurity.

WHAT COULD EXPLAIN IT?
A new early-stage fund closed before the observed increase.

HOW STRONG IS THE CLAIM?
Corpus-supported for the measured first-party cohort.

SHOW THE EVENTS.
[event list]

SHOW THE EVIDENCE.
[source list]
```

That is domain-aware intelligence.

---

# 45. A Professional User's Mental Model

A venture professional is rarely asking only:

> “What happened?”

They may actually be asking:

### Investor questions

- What is this firm really investing in?
- Is its behaviour changing?
- Is it leading or following?
- Is it doing new deals or protecting the existing portfolio?
- Has its stage moved?
- Has its cheque size changed?
- Which partners are active?
- Who does it repeatedly syndicate with?

### Company questions

- Who financed the company?
- Which investors followed on?
- Was the latest financing primary, secondary, or mixed?
- Is this an extension or new stage?
- What is the capital structure?
- What changed in ownership?
- Is the company approaching liquidity?

### Fund questions

- What fund is currently deploying?
- When did it close?
- What strategy does it have?
- Is a successor fund being raised?
- Is the firm between fund cycles?
- How large is the fund relative to prior vintages?

### LP questions

- What has been committed?
- What has been called?
- What has been distributed?
- How much value is realised?
- How much is unrealised?
- What fees and carry have been charged?
- How does performance compare with peers?

Vantage currently serves the **public investor-behaviour** subset of these questions.

That is a sensible wedge.

---

# 46. What Vantage Can Infer Safely Today

With sufficiently complete evidence, Vantage can reasonably infer or measure:

- observed investment frequency;
- observed lead frequency;
- observed sector mix;
- observed stage mix;
- observed company geography under explicit definitions;
- co-investor frequency;
- comparable-period change;
- fund-close history;
- evidence coverage;
- source contribution;
- historical corpus completeness.

---

# 47. What Vantage Should Not Pretend to Know Yet

Without additional data, Vantage should generally avoid asserting:

- exact investor cheque size;
- exact ownership;
- exact capital deployed;
- exact reserves;
- fund dry powder;
- investment returns;
- DPI / TVPI / IRR;
- portfolio fair value;
- internal IC decisions;
- actual investment conviction;
- undisclosed fund allocation;
- LP identity or commitment;
- board rights;
- precise legal security economics;
- complete real-world investment activity.

This boundary is a product strength, not a weakness.

---

# 48. Implications Matrix for Project Vantage

| Venture-capital reality | Vantage implication |
|---|---|
| A VC firm can manage many funds | Keep `Investor` and `Fund` distinct |
| Adviser, GP, management company, and brand can differ | Do not force legal entities into the current public `Investor` abstraction |
| A fund raises commitments from LPs | `FundClose` is distinct from company financing |
| First close and final close are different | Preserve `close_type` |
| LP commitment is not immediate cash | Do not equate fund commitments with paid-in capital |
| Fund size is not deployed capital | Avoid “capital deployed” from fund announcements |
| Round amount is total financing, not investor cheque | Never attribute total round size to each investor |
| A financing can mix primary and secondary | Future financing model may need transaction components |
| SAFEs and notes are not priced preferred equity | Financing subtype may eventually matter |
| Venture debt is not equity | Avoid broad “funding” semantics that erase instrument type |
| Stage names are conventions | Preserve raw and canonical stage |
| Sector is a taxonomy | Preserve raw and canonical sector |
| Lead and participant roles differ | Maintain separate lead relationships |
| New and follow-on investments differ | Add relationship history before inventing strategy scores |
| Follow-on can mean support or distress | Avoid equating follow-on with positive conviction |
| Fund cycle affects investment pace | Activity signals eventually need fund-context interpretation |
| A new fund can change cheque/stage capacity | Fund history can explain behavioural shifts |
| Syndicates carry network information | Co-investor graph is a future intelligence surface |
| Company valuation is not security fair value | Do not derive portfolio value from headlines |
| Activity is not performance | Keep behavioural intelligence separate from return analytics |
| Unrealised marks are not realised proceeds | If performance is added, separate DPI/RVPI/TVPI |
| Form D is a filing, not a semantic event verdict | Regulatory adapters must pass through validation |
| Form ADV can identify adviser/fund structure | Strong candidate for structured identity enrichment |
| Public web data is incomplete | Coverage/confidence must remain first-class |
| Source types disagree | Preserve provenance |
| Publication date can differ from event date | Keep temporal semantics explicit |
| Strategy statements can change | Treat thesis as time-scoped evidence |
| Legal/regulatory definitions vary by jurisdiction | Store jurisdiction and source-specific meaning |
| Private-market truth changes through new evidence | Canonical history should remain inspectable |

---

# 49. Glossary

## Adviser
Entity that provides investment advice and often investment discretion to a fund, subject to legal and contractual requirements.

## AIF
Alternative Investment Fund. A regulatory category used in the EU/UK framework; exact legal meaning is jurisdiction-specific.

## AIFM
Alternative Investment Fund Manager.

## Angel
Individual investing personal capital directly in companies, typically at early stages.

## Anti-dilution
Contractual protection that can adjust preferred-stock conversion economics after certain lower-priced issuances.

## Board observer
Person allowed to attend board meetings without necessarily holding formal director voting rights.

## Capital call / drawdown
Request for LPs to fund part of their previously committed capital.

## Capital commitment
LP's contractual commitment to provide capital to a fund.

## Cap table
Record of a company's equity and equity-linked securities and ownership.

## Carry / carried interest
GP's contractual share of investment profits.

## Catch-up
Waterfall mechanism that can allocate distributions to the GP after specified LP return conditions.

## Closing — fund
Point at which LP commitments are admitted to a fund. A fund can have first, interim, and final closes.

## Closing — financing
Completion of a company financing transaction under the applicable documents.

## Co-investment
Investment alongside a fund or another investor in the same underlying transaction.

## Co-lead
One of multiple investors publicly or contractually acting as lead investors.

## Commitment period
Period during which a fund can generally make new investments under its governing documents.

## Common stock
Basic residual ownership security in a corporation.

## Convertible note
Debt instrument that can convert into equity under specified terms.

## CVC
Corporate Venture Capital.

## DPI
Distributed to Paid-In Capital.

## Dry powder
Informal term for capital considered available for future investment; methodology varies.

## Exit
Liquidity or realisation event such as acquisition, IPO, or sale.

## Fair value
Valuation objective based on an orderly transaction between market participants at the measurement date under relevant standards/guidance.

## Final close
Final fundraising close of a fund under its governing process.

## Follow-on
Additional investment by an existing investor into a portfolio company.

## Form ADV
U.S. investment-adviser registration/reporting form, portions of which are publicly available.

## Form D
U.S. notice filing for certain exempt securities offerings under Regulation D.

## Fund
Pooled investment vehicle.

## Fund-of-funds
Fund that invests primarily in other investment funds.

## GP
General Partner; commonly the managing partner/entity of a limited-partnership fund.

## Growth equity
Private investment in relatively mature companies seeking expansion capital, often through minority positions.

## Hurdle / preferred return
Specified return threshold relevant to carry economics in some funds.

## Investment Committee / IC
Formal decision body used by some investment firms.

## Investment period
Period during which the fund makes new investments under its governing terms; terminology may overlap with commitment period.

## Investor
Generic term for an entity/person providing capital. In Vantage today, generally the canonical investment organisation.

## IPO
Initial Public Offering.

## IRR
Internal Rate of Return.

## LPA
Limited Partnership Agreement.

## LP
Limited Partner; investor in a limited-partnership fund.

## LPAC
Limited Partner Advisory Committee, generally involved in specified governance/conflict matters under the LPA.

## Liquidation preference
Contractual priority or election affecting distribution of proceeds in specified liquidity events.

## Management company
Operating entity associated with the investment manager, commonly employing staff and receiving management fees.

## Management fee
Fee paid to support fund management operations; formula governed by fund documents.

## MOIC
Multiple on Invested Capital.

## NAV
Net Asset Value.

## New investment
First investment by an investor/fund into a company relationship.

## Option pool
Shares reserved for employee or other equity compensation.

## Opportunity fund
Separate vehicle often used for larger or later follow-on investments.

## Paid-in capital
Capital actually contributed by LPs.

## PME
Public Market Equivalent; family of methods comparing private-market cash flows with public-market benchmarks.

## Portfolio company
Company in which a fund or investor holds an investment.

## Post-money valuation
Company valuation immediately after the relevant new financing under the transaction's valuation convention.

## Preferred stock
Equity security with negotiated rights senior or distinct from common stock.

## Pre-money valuation
Company valuation immediately before the relevant new primary investment.

## Primary transaction
Issuance of new securities where proceeds go to the company.

## Pro rata
Right or participation intended to maintain some ownership proportion in a later financing.

## Recycling
Reinvestment of specified proceeds under a fund's governing terms.

## Reserve
Capital deliberately retained for future investments, commonly follow-ons.

## RVPI
Residual Value to Paid-In Capital.

## SAFE
Simple Agreement for Future Equity.

## Secondary transaction
Sale of existing securities where proceeds generally go to the selling shareholder rather than the company.

## Seed
Early development-stage financing category; definitions vary.

## Series A / B / C
Market labels for sequential priced financings; not universal maturity standards.

## Sidecar
Vehicle investing alongside another fund or transaction.

## SPV
Special Purpose Vehicle.

## Syndicate
Group of investors participating in a common transaction.

## Term sheet
Document summarising principal proposed economic and governance terms.

## Tranched financing
Financing funded in multiple instalments subject to contractual timing or conditions.

## TVPI
Total Value to Paid-In Capital.

## Uncalled commitment
Committed LP capital not yet drawn.

## Venture debt
Debt financing designed for venture-backed companies.

## Vintage year
Year used to classify a fund for performance comparison; methodology varies.

## Warrant
Security giving the holder the right to acquire equity under specified terms.

## Write-off
Reduction of an investment's carrying value, potentially to zero, commonly associated with failure or loss.

---

# 50. Reference Architecture Resulting from Domain Grounding V1

The long-term architecture implied by this primer remains:

```text
                         OBSERVATION NETWORK
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
      Web / RSS       Structured APIs      Regulatory
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                   IMMUTABLE RAW EVIDENCE
                             ▼
                   NORMALISED OBSERVATION
                             ▼
                     CLAIM EXTRACTION
                             ▼
                    VERSIONED RECORD
                             ▼
                       VALIDATION
                             ▼
                    ENTITY RESOLUTION
                             ▼
                    EVENT RECONCILIATION
                             ▼
                   CANONICAL KNOWLEDGE
                             ▼
                     HISTORICAL STATE
                             ▼
                  BEHAVIOURAL MEASUREMENT
                             ▼
                       SIGNAL ENGINE
                             ▼
                    INTELLIGENCE PRODUCT
```

Domain grounding changes **what the boxes mean**, not the need to add more boxes.

---

# 51. Domain Grounding V1 Conclusions

Project Vantage's current architecture is directionally strong.

It has already avoided several major conceptual mistakes by separating:

```text
Company
Investor
Fund
FundingRound
FundClose
Evidence
```

and by keeping:

```text
Investor participation
```

distinct from:

```text
Lead-investor participation
```

The next challenge is not to model the entire venture-capital industry.

It is to preserve these distinctions as Vantage expands.

The governing domain principle should be:

> **Model the economic reality that matters to the intelligence product, at the minimum level of complexity required to represent it truthfully.**

Or, more operationally:

```text
Observe first
      ↓
Understand the domain meaning
      ↓
Preserve evidence
      ↓
Canonicalise carefully
      ↓
Measure behaviour
      ↓
Only then interpret
```

Funding rounds remain an excellent first wedge.

They must not become the accidental ontology of venture capital.

---

# Selected Authoritative and Industry References

The references below were used to ground this primer. They are intentionally weighted toward regulators, industry standard-setters, trade associations, and primary model-document providers.

[^sec-private-funds]: U.S. Securities and Exchange Commission, **Private Funds**. https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/private-funds

[^sec-starting-fund]: U.S. Securities and Exchange Commission, **Starting a Private Fund**. https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/starting-private-fund

[^sec-vc-definition]: U.S. Securities and Exchange Commission, **SEC Adopts Dodd-Frank Act Amendments to Investment Advisers Act** — regulatory venture-capital-fund definition and adviser exemptions. https://www.sec.gov/news/press/2011/2011-133.htm

[^sec-form-d]: U.S. Securities and Exchange Commission, **What is Form D?** https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/what-form-d

[^sec-iapd]: SEC / IAPD, **Investment Adviser Public Disclosure** — Form ADV and adviser information. https://adviserinfo.sec.gov/

[^sec-form-pf]: U.S. Securities and Exchange Commission, **Form PF** materials — Form PF is confidential regulator-facing reporting for covered private-fund advisers. https://www.sec.gov/rules-regulations/2026/04/s7-2026-13

[^hbs-doriot]: Harvard Business School Baker Library, **Georges F. Doriot — ARD / Innovation and Venture Capital**. https://www.library.hbs.edu/hc/doriot/innovation-vc/ard/

[^sba-sbic]: U.S. Small Business Administration, **Small Business Investment Companies**. https://www.sba.gov/for-partners/small-business-investment-companies/

[^ilpa-glossary]: Institutional Limited Partners Association, **Private Equity Glossary**. https://ilpa.org/resources-tools/private-equity-101/private-equity-glossary/

[^ilpa-principles]: Institutional Limited Partners Association, **ILPA Principles 3.0**. https://ilpa.org/industry-guidance/principles-best-practices/ilpa-principles/

[^ilpa-principles-definitions]: Institutional Limited Partners Association, **ILPA Principles 3.0 — Definitions**. https://ilpa.org/wp-content/uploads/2019/06/ILPA-Principles-3.0_2019.pdf

[^ilpa-gp-commitment]: Institutional Limited Partners Association, **ILPA Principles 3.0 — Fund Term and Structure / GP Commitment**. https://ilpa.org/wp-content/flash/ILPA%20Principles%203.0/inc/html/17.html

[^ilpa-reporting]: Institutional Limited Partners Association, **ILPA Reporting Template**. https://ilpa.org/industry-guidance/templates-standards-model-documents/ilpa-templates-hub/ilpa-reporting-template/

[^ilpa-performance]: Institutional Limited Partners Association, **ILPA Performance Template**. https://ilpa.org/industry-guidance/templates-standards-model-documents/ilpa-templates-hub/ilpa-performance-template/

[^nvca-model-docs]: National Venture Capital Association, **Model Legal Documents**. https://nvca.org/model-legal-documents/

[^yc-safe]: Y Combinator, **Post-Money SAFE User Guide / Primer**. https://www.ycombinator.com/assets/ycdc/Primer%20for%20post-money%20safe%20v1.1-2af8129e12effd9638eeab383b7309142c8f415e5cdb0bc210d573f779177a1c.pdf

[^invest-europe-stages]: Invest Europe, **Private Equity at Work — Investment Stages** and investor-reporting glossary. https://www.investeurope.eu/publications/private-equity-at-work-2026-report/about-private-equity-24530.html

[^ipev-guidelines]: International Private Equity and Venture Capital Valuation Board, **2025 IPEV Valuation Guidelines**. https://www.privateequityvaluation.com/Valuation-Guidelines

[^eu-aifmd]: European Commission, **Alternative Investment Fund Managers Directive / Investment Funds**. https://finance.ec.europa.eu/financial-markets/financial-markets-policy/investment-funds_en

[^eu-euveca]: EUR-Lex, **Regulation (EU) No 345/2013 on European venture capital funds (EuVECA)**. https://eur-lex.europa.eu/eli/reg/2013/345/2024-01-09/eng

[^fca-aifm]: UK Financial Conduct Authority, **Apply to be a registered AIFM**. https://www.fca.org.uk/firms/aifmd/apply-registered-aifm

[^fca-aifm-reform]: UK Financial Conduct Authority, **CP26/28: The UK AIFM Regime**. https://www.fca.org.uk/publications/consultation-papers/cp26-28-uk-aifm-regime

---

# Suggested Next Domain Work — Only When Needed

Domain Grounding V1 is deliberately sufficient to continue engineering.

If product development later requires deeper treatment, the most valuable follow-on documents would probably be:

```text
docs/
├── venture_capital_domain_primer.md          ← this document
├── vantage_domain_model.md                   ← future implementation-facing ontology
└── venture_data_source_taxonomy.md           ← future source/evidence semantics
```

`vantage_domain_model.md` should be written **only when an implementation decision requires it**.

Until then, this primer should serve as the domain constraint:

> **Do not add a model merely because the concept exists in venture capital. Add it when Vantage needs to represent that concept to produce more truthful or more useful intelligence.**
