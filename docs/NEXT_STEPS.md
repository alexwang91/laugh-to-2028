# Next Steps

> **Forward source of truth changed on 2026-08-05.**
>
> Read these in order before starting new work:
>
> 1. `docs/MASTER_PLAN_2026-08-05.md`
> 2. `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
> 3. `docs/PROJECT_GOVERNANCE_2026-08-05.md`
> 4. `docs/CONTEXT_CONTINUITY_PROTOCOL.md`
> 5. `docs/CURRENT_STATE.md`
> 6. `config/product.json`
> 7. `config/decision_registry.json`
>
> GitHub current state wins over stale handoff text. Do not reopen already-decided product or research questions without a new registered decision.

---

## Current authorized task

```text
P1.3 Partial-fill correctness — IMPLEMENTATION VERIFIED / FINAL-HEAD CI PENDING / NOT MERGED
```

P0.1, P0.2, P1.1 and P1.2 are merged and complete. P1.3 remains the only active dependency on PR #46.

The exact next action is:

```text
final-head CI on PR #46
-> fix only P1.3 findings on the same PR if required
-> final-head CI green
-> merge PR #46
-> normalize handoff to P1.4
```

Do not start P1.4 reversal safety, P2 router work, P4 leverage work, P5 cycle-exit research or P8 bear-short research early.

---

## P1.3 acceptance boundary

Roadmap requirement:

> Implement position transition from actual fills, not requested notional.

Acceptance criteria:

- 0%, partial and full fill cases all reconcile correctly;
- resting remainder is visible;
- target versus actual exposure is continuously calculable.

The P1.3 implementation consumes durable P1.2 order/fill truth rather than replacing it with requested order size or optimistic submission assumptions.

Implemented candidate behavior:

- persist a trustworthy pre-trade position baseline and target for same-direction economic orders;
- derive signed position progress only from reconciled actual fills;
- classify zero / partial / full fill explicitly;
- expose exchange remaining quantity, live resting remainder and total unfilled quantity separately;
- expose `actual_position_qty_from_fills` and `target_gap_qty` whenever the pre-trade position baseline is known;
- fail closed if local submitted-minus-fill truth disagrees with the exchange remaining quantity;
- do not invent a position baseline for the reversal open leg before P1.4 provides fresh reversal-state reconciliation.

Initial candidate head `c75cd51ba2d73a6b629fb7402e6948326756c0af` passed execution tests and research integration in Phase 0 baseline contract run #24 / Actions `31055367127`. Corrected PR handoff governance run #32 / Actions `31055420052` also passed. `EXEC-PARTIAL-FILL-P1.3` is registered as `IMPLEMENTATION_VERIFIED`.

P1.3 is still **not merged**. The current branch head includes decision-registry and handoff evidence updates, so final-head CI must pass before merge.

Unless the roadmap is formally changed, P1.3 does **not** include or claim:

- P1.4 reversal safety;
- P1.5 metadata-driven precision;
- P1.6 full post-submit account reconciliation;
- P1.7 complete restart-recovery matrix;
- P1.8 emergency/kill paths;
- simultaneous multi-process/distributed locking;
- production readiness.

---

## P1.2 closure baseline

P1.2 Persistent order ledger is `PASS / MERGED` through PR #44, squash/main commit:

```text
a4e1ebc98039ffee7e53f2acd7c38feaebbb2769
```

Its exact final implementation head `62fab73baef86970954afe55831305f4328dee20` passed execution pytest, research integration and PR handoff governance before merge.

P1.2 established:

- durable intent before economic-order network submission;
- durable submission-attempt marker before the submit call;
- deterministic CLOID linkage to Hyperliquid truth;
- submission/OID/status/fill/fee/average-fill/remaining/cancel-reject persistence;
- unresolved-order restart reconstruction;
- exchange-truth precedence with audit history;
- fail-closed behavior for corruption, ambiguous reconciliation and unknown result after a durable submission attempt;
- no blind resubmission under uncertain execution truth.

It did not authorize production risk and did not complete P1.3.

---

## Product baseline that remains frozen

```text
Long universe: BTC / ETH / SOL / BNB
Primary venue: Hyperliquid
Initial capital: $2,000 cash/stablecoin
Recurring manual contribution: about $100/week
Normal decision frequency: daily
Canonical daily boundary: 00:00 UTC
Intraday channel: risk reduction only
Leverage: model-determined, not a fixed user multiple
Catastrophic drawdown tolerance: 70% boundary, not operating target
FLAT: zero directional exposure
FLAT -> LONG/SHORT: human approval required
First short exposure in a new bear phase: human approval required
Production upgrades: candidate/shadow + manual blue-green cutover
Bot credential: trading Agent/API only; no master wallet private key; no automated withdrawals or external transfers
```

Current BTC-only executor capability does not redefine the BTC/ETH/SOL/BNB product universe.

---

## Frozen historical decisions that remain in force

- BRRK-0011 remains the canonical directional research target unless a future registered replacement passes its gates.
- Dynamic PIT alpha remains stopped on the tested sample.
- TSMOM-ALPHA-0029 remains rejected; do not rescue it by retuning the failed sample.
- all-perp implementation remains rejected as the default; instrument routing remains required.
- CARRY remains stopped after corrected risk-free-cash economics failed; do not rescue stopped carry variants.
- historical ASYM-BETA extra sleeve is evidence, not new leverage authorization.
- spot identity cannot be inferred from PnL.

---

## Ordered forward program

```text
P0  canonical product/state registry                       COMPLETE
P1.1 deterministic order identity                         COMPLETE
P1.2 persistent order ledger                              COMPLETE
P1.3 partial-fill correctness                             VERIFIED / FINAL-HEAD CI PENDING / NOT MERGED
P1.4 reversal safety                                      BLOCKED ON P1.3 MERGE
P1.5 precision / metadata                                 BLOCKED
P1.6 post-submit reconciliation                           BLOCKED
P1.7 restart recovery                                     BLOCKED
P1.8 kill and emergency paths                             BLOCKED
P2  Hyperliquid BRRK instrument router                    BLOCKED
P3  production-quality daily BRRK target engine           BLOCKED
P4  dynamic leverage extension and operating-risk study   BLOCKED
P5  cycle-top / late-bull / exit model                    BLOCKED
P6  integrated live-data shadow system                    BLOCKED
P7  limited-capital live long program                     BLOCKED
P8  future bear-short research                            BLOCKED
```

The detailed task definitions and acceptance gates are in `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`.

---

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

P1.3 engineering verification does not authorize live deployment, leverage expansion, new-asset execution, shorting, cycle-exit production or strategy cutover.

---

## Correction loop

Every material task follows:

```text
main
-> fresh candidate branch
-> implement
-> test
-> self-review
-> update CURRENT_STATE / decision registry as required
-> PR
-> CI
-> fix inside the same PR
-> final-head CI
-> merge
-> normalize post-merge handoff if needed
```

Current execution is at the **P1.3 final-head CI gate**. P1.4 remains blocked.
