# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**P5.1 event taxonomy is frozen before feature/model selection. The next task is P5.2 Feature Families under the unchanged `P5.1-EVENT-TAXONOMY-V1` contract. Phase 4 leverage research remains closed; keep production gross at 1.0.**

## Immediate state

```text
LEVERAGE-0039                          STOPPED PRE-RUN / NO RESULT
LEVERAGE-0040                          COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                          COMPLETE / IMMUTABLE / NO_PROMOTION
P4.6 production leverage               NOT ENTERED / BLOCKED BY NO CANDIDATE
production gross cap                   1.0
production_authorized_components       []
P5.1 event taxonomy                    COMPLETE / FROZEN BEFORE FEATURE SELECTION
P5.1 contract                          P5.1-EVENT-TAXONOMY-V1
next task                              P5.2 FEATURE FAMILIES
```

## P5.1 — completed / frozen

The event taxonomy is defined in:

```text
research/cycle_exit/p5_1_event_taxonomy.json
research/cycle_exit/p5_1_event_taxonomy.py
docs/P5_1_EVENT_TAXONOMY.md
```

It freezes the required 2021 and 2025 roadmap cases plus multiple non-top high-volatility controls **before** feature scoring.

Required cases:

- 2021 spring first major top / May crash — nonterminal major top;
- 2021 summer recovery / second-wind transition;
- 2021 November terminal peak / bear transition;
- 2025 June new-high phase;
- 2025 August new-high phase;
- 2025 October new-high / deleveraging phase;
- subsequent late-2025 deterioration.

Only the 2021 November case is explicitly terminal in V1. The 2025 sequence remains differentiated as temporary/second-wind/deleveraging/deterioration rather than being hardcoded as one terminal top.

Calendar search windows are frozen. Anchors are mechanically resolved from canonical P3.1 BTCUSDT UTC daily closes. Feature/model performance may not move event windows or select a prettier nearby anchor.

Evaluation buckets remain:

```text
early_warning    -28 .. -15 days
target_lead      -14 ..  -7 days
near_event        -6 ..   0 days
immediate_after   +1 .. +28 days
medium_after     +29 .. +90 days
```

The 7–14 day bucket measures useful lead; it is not a requirement to force a signal there.

## P5.2 Feature Families — NEXT

Evaluate candidate feature families under one consistent, causal framework and the unchanged P5.1 taxonomy.

### A. BTC trend maturity

- 20d trend;
- 40d trend;
- trend slopes;
- KAMA state / slope;
- distance from high;
- high-level consolidation duration;
- volatility contraction / expansion where defined causally.

### B. Momentum exhaustion

- daily RSI family;
- 4h RSI family;
- price / momentum divergence;
- persistence at extremes;
- failure from extremes;
- daily versus 4h agreement / disagreement.

Do **not** visually preselect daily RSI or 4h RSI. Both must be compared under the same event/control framework.

### C. Leadership migration

- BTC dominance;
- ETH/BTC;
- SOL/BTC;
- BNB/BTC;
- BRRK cross-sectional relative-strength dispersion.

### D. Breadth

- proportion outperforming BTC;
- high-beta participation;
- breadth acceleration;
- breadth contraction after expansion;
- headline strength versus internal deterioration.

### E. Leverage / speculation

Where data quality is sufficient:

- funding;
- open interest;
- basis;
- premium;
- volatility;
- liquidation / leverage proxies.

Missing or unreliable data must be reported rather than filled with a favorable proxy after seeing event results.

## P5.2 evaluation discipline

P5.2 should produce **feature evidence, not the final state model**.

For each feature/family, report at least:

- value/trajectory in each frozen event window;
- value/trajectory in non-top controls;
- separation between terminal / nonterminal / second-wind cases;
- early-warning versus near-event behavior;
- stability across 2021 and 2025;
- missing-data coverage;
- sensitivity to reasonable fixed lookbacks;
- signs of obvious event-specific overfit.

P5.2 may eliminate weak/redundant features. It must not yet hand-tune P5.3 state thresholds to maximize one historical event.

## P5.3 State model — after P5.2

Target state vocabulary remains:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

## P5.4 Required behavior

- BTC high-level consolidation plus falling BTC dominance is not automatically bearish;
- LATE_BULL_ROTATION may raise relative alt weight;
- total gross risk should begin falling as cycle hazard rises;
- hard-risk combinations may force direct FLAT;
- seek useful 7–14 day lead information where supported, but do not force it if evidence does not support it.

## P5.5 Validation

Use leave-one-event-out or comparable event-level validation where feasible.

Required reporting:

- lead/lag distribution;
- false-positive duration;
- missed upside before exit;
- drawdown avoided;
- terminal wealth impact;
- second-wind behavior.

Any rule that requires 2021-specific or 2025-specific hand tuning fails robustness.

## P5.6 Integration

The cycle layer controls **total directional risk state**, not BRRK relative ranking.

```text
BRRK        = which assets
Cycle layer = how much total directional risk
Router      = with which instruments
Execution   = how to reach actual target safely
```

## Downstream after Phase 5

### Phase 6 — integrated shadow system

Use live market/account state with **zero trading authority**. Log target weights, cycle state, gross target, router choice and hypothetical fills. Require drift/reconciliation/data-quality acceptance before any production progression.

### Phase 7 — limited-capital live long

Only after Phase 6 acceptance and explicit user production approval. Preserve Agent/API-only credentials, no automated withdrawals/transfers, hard exposure caps, kill switch, startup reconciliation and human transition gates.

### Phase 8 — bear-short research

Do not prioritize ahead of long/exit production readiness. Begin with BTC/ETH/SOL/BNB; any Top-20 extension requires contemporaneous liquidity/perp/funding/market-structure evidence. First short remains explicitly human-gated.

## Frozen boundaries while Phase 5 proceeds

- BRRK-0011 remains the canonical directional core;
- BTC/ETH/SOL/BNB remain the long target universe;
- XRP remains feature-only;
- Hyperliquid remains the primary venue;
- P4.1 defensive scale remains `[0,1]`;
- production gross remains `1.0`;
- LEVERAGE-0040 and LEVERAGE-0041 are immutable failed studies;
- EXPOSURE-SMOOTH-0038 remains `SHADOW_ONLY / NOT PROMOTED`;
- no automated withdrawal or external transfer capability;
- no ACTIVE hot patching.

## Exact next step

```text
MERGE P5.1 ONLY AFTER FRESH FINAL-HEAD CI/GOVERNANCE
VERIFY NEW MAIN
CREATE A FRESH P5.2 BRANCH FROM THAT MAIN
BUILD CAUSAL FEATURE-FAMILY EVIDENCE UNDER P5.1-EVENT-TAXONOMY-V1
DO NOT MOVE EVENT WINDOWS / ANCHORS AFTER FEATURE RESULTS
DO NOT START P5.3 THRESHOLD/STATE-MODEL SELECTION BEFORE P5.2 EVIDENCE IS REVIEWABLE
```
