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
P1.2 Persistent order ledger
```

P0.1, P0.2 and P1.1 are merged and complete. P1.2 is the only authorized next implementation dependency until its implementation PR, final-head CI, merge and post-merge handoff are complete.

Do not start P1.3 partial-fill lifecycle, P4 leverage work, P5 cycle-exit research or P8 bear-short research early.

---

## P1.2 acceptance boundary

P1.2 must establish durable execution truth keyed by deterministic Hyperliquid CLOID:

- persist economic order intent before network submission;
- persist a durable submission-attempt marker before the submit call;
- persist submission response and OID when available;
- persist status history, fills, fees, average fill price, remaining quantity and cancel/reject reason;
- enumerate unresolved orders after restart and reconcile them against Hyperliquid `orderStatus` and fill truth;
- prefer exchange truth while preserving audit evidence for conflicts;
- fail closed on ledger corruption, ambiguous reads, uncertain reconciliation or unknown CLOID after a durable submission attempt;
- never blind-resubmit because local state is damaged or exchange lookup is uncertain;
- cover persistence, uniqueness, replay, restart and reconstruction with tests.

P1.2 does **not** claim the full P1.3 partial-fill state machine/retry policy, simultaneous multi-process/distributed locking, slicing, reversal safety, multi-asset production execution or production readiness.

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
P1.2 persistent order ledger                              CURRENT
P1.3 partial-fill state machine                           BLOCKED ON P1.2
P1+  continue strictly in roadmap dependency order
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

Production authorization does not change merely because an implementation component passes its engineering gate.
