# BRRK-IDLE-CASH-SWEEP-ROBUSTNESS-0063 — DESIGN FREEZE

Date: 2026-08-14

Research ID: `BRRK-IDLE-CASH-SWEEP-ROBUSTNESS-0063`

Stage: `DESIGN_FROZEN / PREREGISTRATION_ABSENT / IMPLEMENTATION_ABSENT / NOT_RUN`

## Question

Does a mechanically yield-bearing idle-cash sleeve, applied to the unchanged canonical BRRK-0011 risk-asset path, retain a positive full-cycle net wealth/CAGR advantage after prospectively frozen conservative yield-realization and cash-sweep-friction stresses, without worsening drawdown?

F27 R2 is exposed DEVELOPMENT motivation only. Its reported historical uplift cannot satisfy any 0063 gate and is not independent OOS evidence.

0063 is not a BTC-to-Cash timing model. It adds no risk signal, threshold, gross map, re-entry rule, hysteresis, leverage, shorting, or directional parameter.

## Immutable baseline inputs

- `research/results/pit_disp_0015/daily_equity.csv`, blob `82c87f8cb0ff01c728ffd3b717fff17cf5a364f2`
- `research/results/pit_disp_0015/daily_weights.csv`, blob `2f6c8d3a8c25d3cafeaa0128f1c425dac248370b`
- variant prefix `BRRK0011_BASELINE__`
- known starting capital USD 10,000 for first-day return reconstruction
- expected committed evaluation window 2022-12-10 through 2026-08-02

The raw baseline reconstruction must reproduce the existing calendar-span BRRK-0011 anchor within a preregistered numerical tolerance. Strategy refit, target recomputation, weight modification, alternate baseline, or window substitution is forbidden.

## Result-blind DTB3 capture

The prior F27 script fetched FRED at runtime and did not persist its raw input as a separately immutable 0063 dataset. Before numerical preregistration is finalized, 0063 must perform one result-blind capture:

- provider FRED
- series `DTB3`
- raw FRED graph CSV
- requested range 2022-11-30 through 2026-08-02
- first complete valid capture only
- persist raw bytes, SHA256 and Git blob before scientific execution
- capture may validate schema/date/value fields but may not compute 0063 candidate economics
- no alternative rate series or post-hoc replacement

Convert bank-discount DTB3 to investment basis with the already-defined repository convention `BEY = 365*d/(360-91*d)`, then accrue `BEY/365`. Calendarization uses causal forward fill. Backfill inside the strategy window is forbidden.

## Frozen economics

For date t:

- `r_t`: unchanged reconstructed BRRK-0011 daily return
- `g_t`: absolute L1 gross from committed BRRK-0011 weights
- `c_t = clip(1-g_t,0,1)`
- `rf_t`: captured DTB3 investment-basis daily return
- `a`: yield-realization fraction
- `f`: sweep friction per unit change in cash sleeve

Candidate return:

`r_candidate,t = r_t + c_t*a*rf_t - f*abs(c_t-c_(t-1))`

First-observation cash-sleeve turnover is fixed to zero.

Yield-realization grid: `0.25 / 0.50 / 0.75 / 1.00`.

Sweep-friction grid: `0 / 5 / 10 / 20 bps` per unit L1 cash-sleeve change.

Total stress cells: 16.

Primary conservative cell: `a=0.50`, `f=10 bps`.

These are robustness stresses, not tunable strategy candidates. Historical argmax has no authority. The full grid must be persisted.

## Outcome priority

1. same-window net terminal wealth / net CAGR versus unchanged BRRK-0011
2. MDD / drawdown damage
3. sweep turnover / friction
4. chronological recurrence
5. dependence-aware paired uncertainty

Sharpe/Calmar may be secondary diagnostics only after formula freeze. They cannot replace the primary wealth/CAGR gates.

## Minimum PASS substance

The later preregistration may be stricter but may not weaken these requirements:

- contract/data identity passes;
- primary 50%-realization/10-bps-friction cell has strictly higher full-cycle net terminal wealth and CAGR than baseline;
- primary-cell MDD is not worse than baseline except floating-point tolerance;
- at least 3/4 prospectively fixed contiguous chronological blocks have strictly positive candidate-minus-baseline relative log growth;
- a prospectively frozen aligned moving-block-bootstrap one-sided LCB for the primary paired advantage is strictly positive;
- robustness is not a one-cell knife edge: every 50%/75%/100% realization cell at 0/5/10 bps must have positive full-cycle relative terminal wealth; the full 25% row and 20-bps column remain reported.

Numerical preregistration must freeze the exact block partition, bootstrap statistic, block length, replicate count, seed, quantile convention, any simultaneous correction, exact metric formulas, classification precedence and lossless schema before historical 0063 candidate economics.

## Forbidden within 0063 after outcome access

No change to the rate source, yield grid, primary cell, friction grid, baseline path/window, signal/weights/gross, statistical gates, selected calendar blocks, or output scope. No same-ID rerun, recomputation, retuning or rescue after a durable attempt marker. Any distinct continuation requires a new ID.

## Intended classification family

`INVALID_EXECUTION`

`MEASUREMENT_INCONCLUSIVE_DATA_IDENTITY`

`FAIL_IDLE_CASH_SWEEP_PRIMARY_ECONOMICS`

`FAIL_IDLE_CASH_SWEEP_DRAWDOWN`

`FAIL_IDLE_CASH_SWEEP_TEMPORAL_ROBUSTNESS`

`FAIL_IDLE_CASH_SWEEP_DEPENDENCE_ROBUSTNESS`

`FAIL_IDLE_CASH_SWEEP_STRESS_ROBUSTNESS`

`PASS_IDLE_CASH_SWEEP_ROBUSTNESS`

A PASS is DEVELOPMENT evidence only. It does not constitute independent OOS validation or production promotion.

## Program stop condition

If 0063 passes its fully frozen economic, stress, temporal and dependence gates, it satisfies the DEVELOPMENT-stage goal of a low-complexity full-cycle net-CAGR improvement over canonical BRRK-0011. Future-only validation remains separately required for independent confirmation.

If 0063 fails, close it immutably and continue under a new research ID without rescuing the grid.

## Authority

Canonical BRRK-0011: `NO_CHANGE`.

Phase 6: `NO_CHANGE`.

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`

Spot only; no leverage; no shorting.

## Exact next step

Merge DESIGN through standing governance CI. Then perform the result-blind DTB3 capture, freeze numerical/data preregistration, merge it, implement using synthetic-only tests, merge implementation, freeze/merge a controlled-execution boundary, perform exactly one historical attempt, and immutably close out.
