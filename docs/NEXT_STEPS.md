# BRRK Next Steps

Last updated: 2026-08-07

## Current instruction

**PR #90 is merged. LEVERAGE-0040 is closed permanently with immutable `NO_PROMOTION`. The active follow-on research target is the new preregistered experiment `LEVERAGE-0041`; do not rerun or retune LEVERAGE-0040.**

## Immediate state

```text
main                                  14dd9f2fb828d860b8552816814982dc4bd89b10
PR #90                                MERGED
LEVERAGE-0040                         COMPLETE / IMMUTABLE / NO_PROMOTION
LEVERAGE-0041                         PREREGISTERED / NOT RUN
selected research cap                 NONE
selected operating DD budget          NONE
P4.6 production authorization         BLOCKED
production gross cap                  1.0
production_authorized_components      []
```

## LEVERAGE-0041 objective

Find the leverage sweet spot that maximizes expected long-run compounded wealth while keeping survival, tail risk, funding, liquidation and implementation risk inside explicit frozen limits.

`1.20` is a focal design point because LEVERAGE-0040 showed attractive economics there, but it is **not** a selected cap and receives no favorable selection treatment.

Frozen requested-cap grid:

```text
1.00 / 1.05 / 1.10 / 1.15 / 1.20 / 1.25 / 1.30
```

## New architecture under test

`SPOT_FIRST_BASE_PLUS_PERP_OVERLAY_V1`

- reserve 25% of NAV as explicit modeled cash collateral;
- no more than 75% NAV is spot financed;
- BTC / ETH / SOL base longs are spot-first under verified P2.4 identity/capacity/cost evidence;
- BNB remains `PERP_ONLY_DEFAULT`;
- residual base exposure and all incremental exposure above cap=1 are perp;
- funding logic may only reduce the incremental overlay, never increase gross exposure;
- no hidden or external collateral may be assumed.

Funding reducer is frozen before first result:

```text
trailing 168h funding debit <= 5 bps/day      overlay scale 1.0
5 < debit < 10 bps/day                        linear 1.0 -> 0.0
debit >= 10 bps/day                           overlay scale 0.0
missing required funding data                 overlay scale 0.0
```

## Hard gates remain hard

Do not relax the predecessor safety boundaries to obtain a pass:

- defensive scale remains `[0,1]`;
- scenario CVaR/CDaR budget remains 20%;
- operating DD budgets remain 35/40/45/50%;
- catastrophic drawdown boundary remains 70%;
- one-day uniform gap stress still reaches -50%;
- funding spike stress remains 2x/3x/5x debit;
- degraded fill/capacity stress remains mandatory;
- start-date and stationary-block robustness remain mandatory;
- missing required evidence fails closed.

LEVERAGE-0041 strengthens the liquidation-distance requirement: actual routed perp notionals against the explicit collateral reserve must preserve **>55% modeled adverse-move distance to liquidation** for every promotable state.

## Sweet-spot selection rule

A cap may only be selected if it is an interior member of a contiguous all-pass region of at least three caps and both immediate neighbors also pass every hard gate.

Among caps in a qualifying region, maximize matched after-cost CAGR. If candidates in the same passing region are within 1.0 percentage point of annualized CAGR, choose the lower cap.

A boundary cap cannot be selected as the sweet spot.

## Work allowed now

### 1. Merge the LEVERAGE-0041 preregistration only after CI/governance is green

The preregistration must freeze:

- experiment ID;
- exact cap grid;
- spot/perp/collateral architecture;
- funding reducer;
- stress/liquidation rules;
- robustness seed and selection rule;
- explicit non-production boundary.

### 2. After preregistration merge, implement the study without observing candidate economics

Required pre-run work includes:

- implementation contract for route split and collateral accounting;
- exact cap=1 requested-target parity against frozen BRRK-0011;
- funding reducer unit/golden tests;
- liquidation model mapped to actual routed perp notionals plus 25% reserve;
- result schema and immutable-output validator;
- required input evidence and hashes;
- applicable Phase 0 / normalization / P3.2 parity / governance checks.

### 3. Stop at the RUN_ONCE boundary

Preregistration and implementation do **not** authorize execution.

A separate explicit owner `RUN_ONCE` instruction is required after all pre-run gates are green.

## Research integrity boundary

Forbidden:

- rerun, rescue or retune LEVERAGE-0040;
- alter LEVERAGE-0040 immutable result files;
- change LEVERAGE-0041 cap grid, reserve, funding thresholds, hard gates, seed or selection rule after seeing any LEVERAGE-0041 result;
- use funding as alpha or allow funding logic to increase exposure;
- introduce XRP target exposure, new directional alpha, EXPOSURE-SMOOTH-0038 substitution or P5 exit logic;
- treat research CI/merge as production authorization.

## P4.6 boundary

P4.6 remains blocked until a separately preregistered leverage study actually selects an eligible research candidate.

If LEVERAGE-0041 does select a candidate, the cap presented to P4.6 is the **next lower preregistered grid point** and may never exceed 1.20 under LEVERAGE-0041. P4.6 still requires a separate explicit production decision and live/shadow evidence.

## Downstream roadmap

```text
PR #90 merged / LEVERAGE-0040 closed
-> LEVERAGE-0041 preregistration
-> LEVERAGE-0041 implementation + pre-run gates
-> explicit RUN_ONCE decision
-> immutable result + select/fail decision
-> P4.6 only if an eligible candidate exists
-> Phase 5 cycle-top / exit intelligence after leverage dependency is resolved
```
