# BRRK Current State

Last updated: 2026-08-07
Status: **authoritative current-state handoff**

> GitHub `main` is the canonical merged ref. PR #90 is merged. LEVERAGE-0040 is complete and immutable with `NO_PROMOTION`. LEVERAGE-0041 is the new preregistered research target; preregistration does not authorize a run or production leverage.

## Executive state

```text
Phase 0                         COMPLETE / MERGED
Phase 1                         COMPLETE / MERGED
Phase 2                         COMPLETE / MERGED
Phase 3                         COMPLETE / MERGED
P4.1 defensive scaler          COMPLETE / MERGED / frozen [0,1]
P4 architecture + cap1         COMPLETE / MERGED
P4 margin/liquidation prereqs  COMPLETE / MERGED
LEVERAGE-0040                  COMPLETE / IMMUTABLE / NO_PROMOTION
P4.5 select/fail decision      COMPLETE / FAIL_STOP
LEVERAGE-0041                  PREREGISTERED / NOT RUN
P4.6 production leverage gate  BLOCKED
P5 exit intelligence           NOT STARTED
production authorization       NONE
```

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## Canonical merged base

`14dd9f2fb828d860b8552816814982dc4bd89b10`

This is the merge commit for PR #90.

## LEVERAGE-0040 historical truth

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
```

At 5 bps execution cost:

```text
cap 1.00  CAGR 65.31%  MDD -33.53%  Sharpe 1.3561  comparator
cap 1.10  CAGR 71.92%  MDD -36.67%  Sharpe 1.3548  FAIL
cap 1.20  CAGR 78.51%  MDD -39.63%  Sharpe 1.3550  FAIL
cap 1.30  CAGR 85.68%  MDD -42.58%  Sharpe 1.3618  FAIL
```

Do not rerun, rescue, reinterpret or reuse LEVERAGE-0040.

## LEVERAGE-0041 preregistered hypothesis

Experiment ID:

`LEVERAGE-0041`

Question: can a new implementation architecture realize a safely sustainable leverage sweet spot around the economically attractive 1.20 region without weakening the frozen BRRK signal/defensive layer or hard survival/tail-risk constraints?

Frozen requested-cap grid:

```text
1.00 / 1.05 / 1.10 / 1.15 / 1.20 / 1.25 / 1.30
```

`1.20` is a focal design point only, not a selected cap.

### Architecture

`SPOT_FIRST_BASE_PLUS_PERP_OVERLAY_V1`

- explicit cash collateral reserve = 25% NAV;
- spot financing budget <=75% NAV;
- BTC / ETH / SOL base longs use verified P2.4 spot-first routing when feasible;
- BNB remains `PERP_ONLY_DEFAULT`;
- residual base exposure and all incremental leverage are perp;
- no hidden external collateral;
- funding logic may only reduce incremental overlay.

Frozen funding reducer:

```text
168h trailing debit <=5 bps/day    overlay scale 1
5-10 bps/day                       linear 1 -> 0
>=10 bps/day                       overlay scale 0
missing required data              overlay scale 0
```

### Hard constraints

Unchanged:

- defensive scenario CVaR/CDaR budget = 20%;
- operating DD candidates = 35/40/45/50%;
- catastrophic boundary = 70%;
- synthetic uniform gap stress through -50%;
- funding spikes 2x/3x/5x;
- degraded-fill/capacity, start-date and bootstrap robustness gates.

Stricter implementation condition:

- actual routed perp notionals against the explicit reserve must preserve modeled adverse-move distance to liquidation **>55%** for every promotable state.

### Broad-region rule

A selected sweet spot must be an interior cap with an immediate lower and higher cap that also pass every hard gate, within a contiguous all-pass region of at least three caps.

Among qualifying caps, maximize matched after-cost CAGR. If annualized CAGR differs by <=1.0 percentage point inside the same passing region, prefer the lower cap.

## Frozen product / strategy boundaries

- canonical directional research target: BRRK-0011;
- target/tradable assets: BTC / ETH / SOL / BNB;
- XRP is feature-only;
- primary venue: Hyperliquid;
- cadence: daily, 00:00 UTC boundary;
- FLAT = zero directional exposure;
- FLAT -> LONG / SHORT requires human approval;
- intraday automation may reduce risk but may not autonomously add directional exposure;
- bot uses trading Agent/API credentials only;
- master wallet private key, automated withdrawals and automated external transfers remain outside scope;
- P4.1 defensive scale remains `[0,1]`.

## Authority boundaries

`LEVERAGE-0041 = PREREGISTERED` does not mean:

- implemented;
- tested;
- CI verified;
- RUN_ONCE authorized;
- research promoted;
- production authorized.

The one-time run requires a separate explicit owner `RUN_ONCE` instruction after implementation and all pre-run gates are green.

If a future LEVERAGE-0041 result selects an eligible research cap, P4.6 remains a separate production decision. The prospective cap presented to P4.6 is the next lower preregistered grid point and may not exceed 1.20 under LEVERAGE-0041.

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
MERGE LEVERAGE-0041 PREREGISTRATION ONLY AFTER FRESH CI/GOVERNANCE
THEN IMPLEMENT STUDY CONTRACT + ROUTE/COLLATERAL/FUNDING/LIQUIDATION LOGIC
PROVE CAP=1 REQUESTED-TARGET PARITY
FREEZE RESULT SCHEMA / INPUT HASHES / VALIDATOR
RUN ALL PRE-RUN GATES
STOP AT EXPLICIT OWNER RUN_ONCE BOUNDARY
KEEP PRODUCTION GROSS CAP = 1.0
KEEP P4.6 BLOCKED
```
