# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**Phase 4 leverage research is closed for the current program after LEVERAGE-0040 and LEVERAGE-0041 both returned immutable `NO_PROMOTION`. Keep production gross at 1.0. The next forward roadmap program is Phase 5 cycle-top / late-bull / exit research.**

## Immediate state

```text
LEVERAGE-0039                          STOPPED PRE-RUN / NO RESULT
LEVERAGE-0040                          COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                          COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041 result commit            8ea784830cfffbf892a258cb329d437725d41982
LEVERAGE-0041 summary SHA256           e41a5895263e7aa9206df9fa99fcbb71e5f937abc4746a567fbeb462cca88d17
selected research cap                  NONE
selected operating DD budget           NONE
P4.6 production leverage               NOT ENTERED / BLOCKED BY NO CANDIDATE
production gross cap                   1.0
production_authorized_components       []
next forward phase                     PHASE 5
```

## Why Phase 4 stops here

LEVERAGE-0041 tested the independent follow-on architecture rather than retuning LEVERAGE-0040. All requested caps above 1.0 failed before the broad-region stage. No research cap was selected and no prospective P4.6 cap exists.

The frozen liquidation-distance threshold was `>55%`. Under the corrected explicit-reserve / actual-routed-perp accounting, measured minimum distances were below that threshold for every grid point, including 42.52% at cap 1.05 and 32.33% at cap 1.20. Therefore there is no basis to cross into production leverage authorization.

Any future leverage revisit must use a new registered hypothesis/experiment ID. It is not the immediate roadmap dependency.

## Next program — Phase 5 cycle-top / late-bull / exit model

Phase 5 is a **new research program**, not a BRRK retune and not a leverage rescue.

### P5.1 Event taxonomy — NEXT

Create labeled event windows while avoiding the mistake of treating every local top as a terminal top.

Minimum required cases from the roadmap:

- 2021 spring first major top / May crash;
- 2021 summer recovery / second-wind transition;
- 2021 November terminal peak / bear transition;
- 2025 June new-high phase;
- 2025 August new-high phase;
- 2025 October new-high / deleveraging phase;
- subsequent late-2025 deterioration;
- non-top high-volatility controls.

P5.1 should freeze event definitions before evaluating candidate feature/model performance against them.

### P5.2 Feature families

Evaluate under one consistent validation framework:

- BTC trend maturity: 20d/40d trends, slopes, KAMA state/slope, distance from high, consolidation duration;
- momentum exhaustion: daily and 4h RSI families, divergence, persistence/failure from extremes;
- leadership migration: BTC dominance, ETH/BTC, SOL/BTC, BNB/BTC, cross-sectional relative-strength dispersion;
- breadth: BTC outperformance breadth, high-beta participation, acceleration/contraction, headline-vs-internal deterioration;
- leverage/speculation: funding, OI, basis, premium, volatility, liquidation proxies where data quality is sufficient.

Do not visually preselect daily vs 4h RSI or hand-pick a single favored top indicator before validation.

### P5.3 State model

Target state vocabulary:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

### P5.4 Required behavior

- BTC consolidation + falling dominance is not automatically bearish;
- late-bull rotation may increase relative alt weight;
- total gross risk should fall as cycle hazard increases;
- hard-risk combinations may force direct FLAT;
- seek useful 7–14 day lead information where supported, but do not force a lead-time target unsupported by evidence.

### P5.5 Validation

Use leave-one-event-out or comparable event-level validation where feasible.

Required reporting:

- lead/lag distribution;
- false-positive duration;
- missed upside before exit;
- drawdown avoided;
- terminal wealth impact;
- second-wind behavior.

Any rule that requires 2021-specific or 2025-specific hand tuning fails robustness.

### P5.6 Integration

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
MERGE THE CURRENT PHASE-4 CLOSEOUT ONLY AFTER FRESH FINAL-HEAD CI/GOVERNANCE
VERIFY THE NEW MAIN SHA
CREATE A FRESH P5.1 BRANCH FROM THAT MAIN
IMPLEMENT / FREEZE EVENT TAXONOMY ONLY
DO NOT START P5.2 MODEL SELECTION BEFORE P5.1 EVENT DEFINITIONS ARE REVIEWABLE
```
