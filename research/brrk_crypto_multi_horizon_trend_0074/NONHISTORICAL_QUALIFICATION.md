# BRRK-CRYPTO-MULTI-HORIZON-TREND-0074 — NONHISTORICAL QUALIFICATION

Status: STAGE 5 / SYNTHETIC-ONLY QUALIFICATION

## Authority and scope

This stage qualifies only the merged Stage-4 implementation against synthetic fixtures and frozen Stage-3 mechanics. It grants no scientific result, no historical evidence credit, and no production/signature/order authority.

Lifecycle lineage:
- Stage 1 OWNER-FIRST merge: `2af445a26e2a1d08b38a1cc9f6c853b29c828cde`.
- Stage 2 DESIGN merge: `08eafc22c3772bd021bc7e3c201c5dc63ac81e64`.
- Stage 3 PREREGISTRATION merge: `beae11d807886bfec65aa5cc8a26f79e92e5a0e9`.
- Stage 4 IMPLEMENTATION merge: `b74263cd6ab2bddd37544702fec0a187b7433151`.

Frozen budgets at Stage-5 entry:
- controlled attempt: `0/1`;
- controlled scientific/history reads: `0`;
- scientific engine calls: `0`;
- scientific source-network fetches: `0`.

## Frozen qualification assertions

Qualification must use synthetic fixtures only and must demonstrate deterministic agreement with the merged implementation contract for all of the following:

1. Universe is exactly BTC, ETH and SOL; exactly three selectable candidate families remain present.
2. Past-return-sign horizons remain exactly 20/60/180 observations.
3. SMA-spread pairs remain exactly 10/40, 20/80 and 60/240.
4. Breakout horizons remain exactly 20/60/180 and compare close `t` only against the prior completed window excluding `t`.
5. Horizon votes combine by equal vote with exact-zero sum mapped to flat.
6. Lagged volatility uses the prior 20 executable daily log returns, annualized by `sqrt(365)`, with 20% target and 5% floor in the denominator.
7. Per-asset absolute weight cap remains `1/3`; portfolio gross cap remains `1.0`.
8. Exposure decided at close `t` applies first to the `t -> t+1` return interval; no same-bar lookahead is permitted.
9. Turnover remains `sum(abs(w_t-w_{t-1}))` and C0/C1/C2 one-way turnover costs remain 0/10/30 bps.
10. Positive funding means long pays short and contribution remains `-position_notional * funding_rate`.
11. Missing/malformed required inputs fail closed for the affected asset-day; no forward fill is introduced.
12. No fixture or test may change Stage-3 support minima, G0-G11 thresholds, bootstrap parameters, DSR trial count, CSCV/PBO semantics, neighborhood stresses, terminal classifications, or representative-candidate priority.

## Required synthetic fixture families

At minimum, qualification must cover:
- monotone-up and monotone-down price paths;
- flat paths and exact-tie vote cases;
- breakout boundary chronology excluding the current close;
- volatility-floor and volatility-cap behavior;
- multi-asset gross-cap enforcement;
- turnover/cost arithmetic under C0/C1/C2;
- positive and negative funding-sign accounting for long and short positions;
- ineligible/missing-value fail-closed behavior;
- chronology tests proving a `t` close cannot influence the same `t-1 -> t` interval.

## PASS / BLOCKED semantics

`QUALIFICATION_PASS_SYNTHETIC_ONLY` requires all frozen mechanical assertions above to pass on synthetic fixtures with no controlled historical content read and no scientific-engine call.

Any mechanical discrepancy that can be fixed without changing frozen Stage-3 science is a Stage-4 implementation defect and must be corrected prospectively before Stage-5 merge. Any proposed change to source identity, candidate family, horizon, threshold, support rule, cost/funding semantics, inference constant, or terminal classification is out of scope and must fail closed rather than be repaired here.

## Post-qualification boundary

Stage 6 may begin only after this Stage-5 contract and its synthetic qualification evidence merge. Stage 6 must prospectively enumerate exact authorized historical object identities and read budgets before any controlled content read. Stage 7 remains zero-result metadata/identity preflight. Stage 8 remains the only controlled DEVELOPMENT-history attempt and still requires contemporaneous explicit user authorization plus durable marker-before-read.

## Stage-5 accounting

- controlled scientific/history reads: `0`;
- scientific engine calls: `0`;
- scientific source-network fetches: `0`;
- controlled attempt: `0/1`;
- production_authorized=false;
- signature_authorized=false;
- order_submission_authorized=false.
