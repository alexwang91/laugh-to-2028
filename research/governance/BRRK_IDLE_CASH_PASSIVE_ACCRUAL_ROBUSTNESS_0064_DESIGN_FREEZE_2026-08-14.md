# BRRK-IDLE-CASH-PASSIVE-ACCRUAL-ROBUSTNESS-0064 — DESIGN FREEZE

Date: 2026-08-14

Research ID: `BRRK-IDLE-CASH-PASSIVE-ACCRUAL-ROBUSTNESS-0064`

Stage: `DESIGN_FROZEN / PREREGISTRATION_ABSENT / IMPLEMENTATION_ABSENT / NOT_RUN`

## Question

Does the unchanged canonical BRRK-0011 path achieve a robust full-cycle net terminal-wealth/CAGR improvement when its already-idle residual cash remains continuously in an interest-bearing balance, after prospectively frozen conservative yield realization and continuous annual account spread/fee, without worsening drawdown?

## Result-informed origin and distinction from 0063

0063 is immutable `FAIL_IDLE_CASH_SWEEP_PRIMARY_ECONOMICS`. Its frozen 50%-DTB3 / 10-bps-per-L1-cash-change primary implementation failed because cumulative transaction-like sweep friction exceeded realized carry. Descriptively, its zero-sweep row had positive relative growth across all four frozen yield-realization levels. Those results are exposed DEVELOPMENT motivation only and cannot satisfy any 0064 gate.

0064 studies a different operational mechanism: risk-asset trades remain exactly the already-committed BRRK-0011 trades, and the residual cash balance stays in the same interest-bearing cash account. No additional trade is created when gross exposure changes. Therefore 0064 charges no transaction-like sweep turnover cost. Instead it applies a continuous annual spread/fee to idle cash principal, plus a realization haircut to the benchmark short-rate yield.

This cost-model change is explicitly result-informed and is legal only under this new research ID.

## Frozen baseline and cash-rate inputs

Unchanged BRRK-0011 committed path:

- `research/results/pit_disp_0015/daily_equity.csv`
- Git blob `82c87f8cb0ff01c728ffd3b717fff17cf5a364f2`
- `research/results/pit_disp_0015/daily_weights.csv`
- Git blob `2f6c8d3a8c25d3cafeaa0128f1c425dac248370b`
- variant `BRRK0011_BASELINE`
- known starting capital USD 10,000
- expected window 2022-12-10 through 2026-08-02

Frozen result-blind DTB3 payload originally captured before 0063 candidate economics:

- path `research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv`
- Git blob `71d50e26f8a9afb6bcb88401d20b97d5fb0a891a`
- SHA256 `4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879`
- FRED series `DTB3`
- no network fetch or replacement in 0064
- researcher-exposed DEVELOPMENT, not independent OOS

The existing bank-discount-to-investment-basis convention remains fixed:

`d = DTB3_percent / 100`

`BEY = 365*d / (360 - 91*d)`

`rf_daily = BEY / 365`

Causal forward-fill only; no strategy-window backfill.

## Frozen passive-accrual economics

For day t:

- `r_t` = unchanged BRRK-0011 daily return
- `g_t` = absolute L1 gross of unchanged BRRK-0011 weights
- `c_t = clip(1-g_t,0,1)` = residual idle-cash fraction
- `rf_t` = causally aligned frozen DTB3 daily investment-basis rate
- `a` = yield-realization fraction
- `s` = annual idle-cash spread/fee in basis points

Net cash rate:

`cash_net_t = a*rf_t - (s/10000)/365.25`

Candidate return:

`r_candidate,t = r_t + c_t*cash_net_t`

There is no floor at zero. If the frozen fee exceeds the realized benchmark yield on a date, the cash contribution may be negative. No transaction or turnover cost is added because 0064 defines the mechanism as continuously interest-bearing residual cash, not an explicit sweep trade.

## Frozen stress geometry

Yield-realization grid:

- 0.25
- 0.50
- 0.75
- 1.00

Continuous annual spread/fee grid:

- 0 bps
- 50 bps
- 100 bps
- 150 bps
- 200 bps

Total stress cells: 20.

### Primary conservative cell

`yield_realization = 0.50`

`annual_spread_fee = 100 bps`

### Core robustness neighborhood

All 9 cells formed by:

- yield realization = 0.50 / 0.75 / 1.00
- annual spread/fee = 50 / 100 / 150 bps

must retain positive full-cycle relative terminal log growth for the stress gate to pass.

Every one of the 20 cells must be persisted losslessly. Historical argmax, winner selection and post-result cell deletion have zero authority.

## Outcome priority

1. full-cycle net terminal wealth and calendar-span net CAGR versus unchanged BRRK-0011
2. max drawdown non-inferiority
3. chronological recurrence of candidate-minus-baseline relative log growth
4. dependence-aware paired uncertainty
5. broad cost/yield robustness

No strategy NAV optimization, signal selection, gross-map optimization, timing rule or re-entry rule is permitted.

## Minimum PASS substance

Numerical preregistration may tighten but may not weaken:

- frozen data/contract identity passes;
- exact baseline path reconstruction/support passes;
- primary 50%-realization / 100-bps annual-fee cell has strictly greater terminal wealth and CAGR than unchanged BRRK-0011;
- primary MDD is not worse than baseline except floating-point equality tolerance;
- at least 3 of 4 prospectively fixed contiguous chronological blocks have strictly positive relative log growth;
- prospectively frozen aligned moving-block-bootstrap one-sided LCB for primary paired relative log-return advantage is strictly positive;
- all 9 core robustness cells have strictly positive full-cycle relative terminal log growth.

Numerical preregistration must freeze exact block construction, MBB block length, replicate count, seed, quantile convention, metrics, classification precedence and exactly-once output schema before historical 0064 candidate economics.

## Intended classification family

- `INVALID_EXECUTION`
- `MEASUREMENT_INCONCLUSIVE_DATA_IDENTITY`
- `FAIL_PASSIVE_CASH_PRIMARY_ECONOMICS`
- `FAIL_PASSIVE_CASH_DRAWDOWN`
- `FAIL_PASSIVE_CASH_TEMPORAL_ROBUSTNESS`
- `FAIL_PASSIVE_CASH_DEPENDENCE_ROBUSTNESS`
- `FAIL_PASSIVE_CASH_STRESS_ROBUSTNESS`
- `PASS_PASSIVE_CASH_ACCRUAL_ROBUSTNESS`

A PASS is robust DEVELOPMENT evidence that the passive idle-cash accrual mechanism improves the already-existing BRRK-0011 full-cycle net CAGR under the frozen cost geometry. It is not independent OOS evidence and does not automatically modify canonical or production state.

## Forbidden after 0064 outcome access

- changing the primary 50% / 100-bps cell;
- changing the realization or annual-fee grid;
- introducing a floor to cash net yield;
- adding sweep-turnover cost or deleting fee terms;
- changing DTB3 source or payload;
- changing BRRK-0011 signals, weights, gross or window;
- selecting favorable blocks or stress cells;
- relaxing MDD, temporal, MBB or stress gates;
- same-ID rerun, recomputation, retune or rescue.

Any distinct continuation requires a new ID.

## Program stop relation

If 0064 passes its fully frozen primary economic, drawdown, temporal, dependence and stress gates, it satisfies the program's DEVELOPMENT-stage requirement for a low-complexity, robust full-cycle net-CAGR improvement over canonical BRRK-0011. Independent future-only confirmation remains a separate higher evidentiary tier and cannot be fabricated from already exposed history.

## Authority

Canonical BRRK-0011: `NO_CHANGE`.

Phase 6: `NO_CHANGE`.

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`

Spot only; no leverage; no shorting.

## Exact next step

After 0063 immutable closeout merges, open and merge this DESIGN through fresh standing CI. Then perform owner-first numerical/data preregistration using the already frozen DTB3 payload, followed by synthetic-only implementation, separate controlled boundary, exactly one historical attempt, and immutable closeout.
