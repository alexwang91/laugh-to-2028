# LEVERAGE-0040 P4.5 Decision — 2026-08-07

Status: **FAIL_STOP / NO_PROMOTION**

This document records the Phase 4.5 selection decision after the immutable LEVERAGE-0040 one-time study result was produced and validated.

## Immutable evidence

- experiment: `LEVERAGE-0040`
- result commit: `bd256e77a9800556e97769858fbb3ba5054c4389`
- summary SHA256: `3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`
- result status: `ONE_TIME_PREREGISTERED_STUDY_COMPLETE`
- selection status: `NO_PROMOTION`
- selected research cap: `null`
- selected operating max-drawdown budget: `null`
- production authorized: `false`
- `production_authorized_components = []`

## Candidate evidence at 5 bps execution cost

| Gross cap | CAGR | Max drawdown | Sharpe | Calmar | P4.5 outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| 1.00 | 65.31% | -33.53% | 1.3561 | 1.9477 | comparator |
| 1.10 | 71.92% | -36.67% | 1.3548 | 1.9616 | FAIL |
| 1.20 | 78.51% | -39.63% | 1.3550 | 1.9809 | FAIL |
| 1.30 | 85.68% | -42.58% | 1.3618 | 2.0122 | FAIL |

**Metric convention.** LEVERAGE-0040 is immutable and its study-local annualization uses an observation-count year (`len(returns) / 365.25`). The 65.31% cap-1.00 comparator is therefore not the same metric quantity as a calendar-span BRRK CAGR reported elsewhere; for example, corrected F27 R2 reports BRRK raw calendar-span CAGR `65.1661%`. This convention difference does not alter the LEVERAGE-0040 decision because every row in the table was computed under the same frozen study-local convention. No immutable result is recomputed or restated by this footnote.

## Selection-rule application

P4.5 was preregistered to avoid choosing leverage from the best in-sample CAGR alone. Promotion requires a robust region with strong terminal wealth, robust Calmar/Sharpe, acceptable drawdown sensitivity, neighboring-parameter support and all mandatory safety/implementation gates.

The immutable result shows:

### 1.10

Failed mandatory gates:

- native Hyperliquid funding stress;
- liquidation distance;
- synthetic gap.

### 1.20

Failed mandatory gates:

- native Hyperliquid funding stress;
- liquidation distance;
- synthetic gap.

### 1.30

Failed mandatory gates:

- native Hyperliquid funding stress;
- liquidation distance;
- synthetic gap;
- historical proxy catastrophe.

Therefore no >1 candidate satisfies the frozen selection rule.

## Formal P4.5 decision

```text
LEVERAGE-0040                 FAIL_STOP / NO_PROMOTION
selected research cap         NONE
selected operating DD budget  NONE
production gross cap          1.0
P4.6                          BLOCKED
production authorization      NONE
```

The experiment ID is closed and must not be reused or retuned after result observation.

## Interpretation of 1.20

The decision does **not** claim that 1.20 is economically unattractive.

The 1.20 candidate produced materially higher historical CAGR than cap 1.00 while Sharpe remained approximately unchanged and Calmar was slightly higher. That makes 1.20 an important economic focal point for future research.

However, P4.5 must distinguish:

- **economic attractiveness**, from
- **promotion eligibility under the tested implementation architecture**.

LEVERAGE-0040 only establishes that its tested implementation architecture did not pass all mandatory safety/robustness gates at 1.20.

## Accepted follow-on hypothesis

The owner accepted a new planning direction on 2026-08-07:

> Search for the safely sustainable leverage sweet spot that maximizes expected long-run compounded wealth, with 1.20 treated as an important focal design point rather than an already selected cap.

This is a **new research hypothesis**, not a reinterpretation of LEVERAGE-0040.

The next study must:

- use a new experiment ID;
- be preregistered before execution;
- freeze its candidate grid before results are observed;
- explicitly model base spot versus incremental perp exposure;
- define collateral/margin reserve and liquidation buffer;
- test funding-aware deleveraging;
- test synthetic-gap survivability;
- use realistic Hyperliquid account/margin mechanics;
- preserve broad-region / neighboring-parameter robustness;
- retain a separate P4.6 production-authorization gate.

No production leverage is authorized by this follow-on planning decision.
