# BRRK Current State

Last updated: 2026-08-07
Status: **authoritative current-state handoff**

> GitHub `main` remains the canonical merged ref. PR #90 contains the completed LEVERAGE-0040 immutable research evidence and the P4.5 no-promotion decision. Research completion does not imply production authorization.

## Executive state

```text
Phase 0                         COMPLETE / MERGED
Phase 1                         COMPLETE / MERGED
Phase 2                         COMPLETE / MERGED
Phase 3                         COMPLETE / MERGED
P4.1 defensive scaler          COMPLETE / MERGED / frozen [0,1]
P4 architecture + cap1         COMPLETE / MERGED
P4 margin/liquidation prereqs  COMPLETE / MERGED
LEVERAGE-0040                  COMPLETE / IMMUTABLE RESULT
P4.5 select/fail decision      FAIL_STOP / NO_PROMOTION
P4.6 production leverage gate  BLOCKED / no eligible candidate
P5 exit intelligence           NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

## LEVERAGE-0040 final evidence

Research PR / branch:

- PR #90;
- `p4-4/leverage-0040-one-time-study-v2`.

Canonical main base:

`3690f64a6179a759a60d9759c214d59cf604869e`

Immutable result commit:

`bd256e77a9800556e97769858fbb3ba5054c4389`

Immutable summary SHA256:

`3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`

Final immutable selection:

```text
status                                  ONE_TIME_PREREGISTERED_STUDY_COMPLETE
selection.status                        NO_PROMOTION
selected_research_cap                   NONE
selected_operating_max_drawdown_budget  NONE
production_authorized                   false
production_authorized_components        []
```

At 5 bps execution cost:

```text
cap 1.00  CAGR 65.31%  MDD -33.53%  Sharpe 1.3561  comparator
cap 1.10  CAGR 71.92%  MDD -36.67%  Sharpe 1.3548  final FAIL
cap 1.20  CAGR 78.51%  MDD -39.63%  Sharpe 1.3550  final FAIL
cap 1.30  CAGR 85.68%  MDD -42.58%  Sharpe 1.3618  final FAIL
```

P4.5 therefore records `FAIL_STOP / NO LEVERAGE PROMOTION` for LEVERAGE-0040.

## Why higher historical CAGR did not promote

The P4.5 rule was frozen before result observation: do not choose leverage from the best in-sample CAGR alone. A candidate must survive the full hard-gate suite and show a robust parameter region.

For cap 1.10 and 1.20, the decisive failures were:

- native Hyperliquid funding stress;
- liquidation-distance gate;
- synthetic-gap gate.

Cap 1.30 also failed the historical proxy catastrophe gate.

This result must not be rewritten as “1.20 is bad.” The correct interpretation is narrower: **the specific LEVERAGE-0040 leverage implementation architecture did not satisfy all preregistered safety/robustness gates.**

## Research integrity boundary

LEVERAGE-0040 is now closed.

Forbidden under the same experiment ID:

- changing caps or thresholds and rerunning;
- deleting failed gates because 1.20 looks attractive;
- changing funding, liquidation, stress, seed, benchmark or selection semantics to rescue a candidate;
- treating 1.20 as selected merely because its CAGR/Calmar were attractive;
- treating the research result as production authorization.

All R1→R5 execution/recovery evidence and immutable result files remain part of the audit trail.

## Follow-on leverage research direction

The owner has accepted the next **planning direction**: search for the leverage “sweet spot” that maximizes long-run compounded wealth while preserving acceptable survival / tail-risk / implementation properties.

Important planning interpretation:

- **1.20 is a focal design point**, because LEVERAGE-0040 showed materially higher CAGR with broadly stable Sharpe/Calmar;
- 1.20 is **not** a selected research cap;
- 1.20 is **not** production-authorized;
- exact candidate grid, margin architecture and gates for the next study are not frozen yet;
- the follow-on study must use a **new experiment ID** and must be preregistered before execution.

The follow-on hypothesis should specifically separate economic gross exposure from implementation mechanics, including:

- base spot versus incremental perp exposure;
- cross-margin collateral reserve and liquidation buffer;
- funding-aware dynamic risk reduction;
- synthetic-gap survivability;
- explicit margin-account mapping consistent with real Hyperliquid mechanics;
- neighboring-cap robustness around the eventual sweet spot.

The objective remains the Master Plan objective: maximize expected long-run compounded wealth **subject to** operating drawdown, catastrophic, liquidation, cost and implementation-robustness constraints.

## Frozen architecture and product constraints

### Directional strategy

- canonical directional research target: **BRRK-0011**;
- target/tradable assets: **BTC / ETH / SOL / BNB**;
- XRP is **feature-only** where required by the frozen BRRK regime feature model;
- primary venue: Hyperliquid;
- cadence: daily;
- canonical decision boundary: 00:00 UTC.

### Execution / safety

- FLAT = zero directional exposure;
- FLAT -> LONG / SHORT requires human approval;
- intraday automation may reduce risk but may not autonomously add directional exposure;
- bot credentials are trading Agent/API credentials only;
- master wallet private key, automated withdrawals and automated external transfers remain outside the approved boundary;
- MERGED / CI VERIFIED does not imply PRODUCTION AUTHORIZED.

### Leverage boundary

P4.1 defensive scale remains strictly `[0,1]`.

Current production gross cap remains:

`1.0`

No operating drawdown budget was selected by LEVERAGE-0040.

`70% drawdown` remains catastrophic tolerance, not an operating target.

## Historical truth that must remain unchanged

### LEVERAGE-0039

```text
STOPPED PRE-RUN
NO RESULT
DO NOT REUSE EXPERIMENT ID
```

### LEVERAGE-0040

```text
COMPLETE
IMMUTABLE RESULT
NO_PROMOTION
DO NOT RETUNE OR REUSE EXPERIMENT ID
```

### EXPOSURE-SMOOTH-0038

`SHADOW_ONLY / NOT PROMOTED`

## Documentation authority

Read current state in this order:

1. root `README.md`;
2. `docs/CURRENT_STATE.md`;
3. `docs/NEXT_STEPS.md`;
4. `docs/MASTER_PLAN_2026-08-05.md`;
5. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`;
6. `config/decision_registry.json`;
7. `docs/README.md`.

## Exact next action

```text
P4.5 FORMAL DECISION = COMPLETE / FAIL_STOP / NO_PROMOTION
RUN FINAL-HEAD POST-RESULT CI + GOVERNANCE ON PR #90
KEEP PRODUCTION GROSS CAP = 1.0
KEEP P4.6 BLOCKED
DO NOT RETUNE LEVERAGE-0040
AFTER RESEARCH EVIDENCE IS MERGED, PREREGISTER A NEW LEVERAGE-ARCHITECTURE / SWEET-SPOT EXPERIMENT
```

PR #90 should not be interpreted or merged as a production-leverage authorization. Any merge only preserves the research implementation, audit trail, immutable result and P4.5 decision.
