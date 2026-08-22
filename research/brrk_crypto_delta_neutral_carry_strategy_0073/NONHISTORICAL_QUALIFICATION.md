# 0073 Stage 5 NONHISTORICAL QUALIFICATION

Research ID: `BRRK-CRYPTO-DELTA-NEUTRAL-CARRY-STRATEGY-0073`

Stage: `NONHISTORICAL QUALIFICATION`

Base implementation merge: `372ece83cda67b74557b32ef19022e9829e2b89f`

## Scope

This stage qualifies implementation mechanics using synthetic fixtures only. It does not open controlled historical/scientific payloads, does not fetch source data, does not create a Stage-8 attempt marker, and does not run the controlled scientific engine.

Frozen science remains unchanged from the merged Stage-3 preregistration and Stage-4 implementation. Exactly three candidates remain in scope: `C1_LONG_SPOT_SHORT_PERPETUAL`, `C2_LONG_SPOT_SHORT_DATED_FUTURE`, and `C3_CROSS_VENUE_SAME_UNDERLYING_HEDGE`, across exactly BTC, ETH, and SOL.

## Qualification contract

Synthetic qualification must verify these mechanics without selecting or tuning on historical outcomes:

1. Same-underlying hedge enforcement rejects cross-underlying pairs.
2. Target pair sizing is +0.50 NAV spot / -0.50 NAV derivative.
3. Rebalance triggers only from the frozen residual-delta threshold, roll-due state, or eligibility change.
4. Residual-delta breach accounting uses the frozen 0.02 NAV maximum and 1% breach-rate gate.
5. Gross exposure cannot exceed 1.00 NAV and margin reserve cannot fall below 0.20 NAV.
6. Dated-future eligibility is 21-120 DTE, with roll due at <=14 DTE.
7. C1_REALISTIC and C2_STRESSED cost mechanics remain frozen, with the stressed multiplier exactly 2.0.
8. Moving-block bootstrap remains synchronized with block length 20, 4000 replicates, PCG64 seed 730073, and 5th-percentile lower bound.
9. DSR trial count remains exactly 3; PBO, when supported, uses CSCV with 8 contiguous slices and minimum 504 eligible days.
10. Classification is limited to `PASS`, `FAIL`, `INCONCLUSIVE_INSUFFICIENT_SUPPORT`, and `INVALID_EXECUTION` under the frozen terminal semantics.

## Governance budgets

- controlled attempt: `0/1`
- controlled scientific/history reads: `0`
- scientific engine calls: `0`
- source-network fetches: `0`
- production authority: `false`
- signature authority: `false`
- order-submission authority: `false`

## Required result

Stage 5 may advance only if all synthetic fixtures pass mechanically with zero controlled reads and zero scientific-engine calls. Any implementation mismatch must be repaired prospectively against the already frozen Stage-3 contract; no historical result may inform that repair.

No Stage 6 CONTROLLED BOUNDARY may be created until Stage 5 is merged through a separate forward PR with standing CI success and an updated `docs/CURRENT_STATE.md` handoff.
