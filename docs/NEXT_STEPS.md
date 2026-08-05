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
P1.4 Reversal safety
```

P0.1, P0.2, P1.1, P1.2 and P1.3 are merged and complete. P1.4 is now the only authorized next implementation dependency.

Do not start P1.5 precision/metadata, P2 router work, P4 leverage work, P5 cycle-exit research or P8 bear-short research early.

---

## P1.4 acceptance boundary

Roadmap requirement:

> No non-atomic long-to-short or short-to-long assumption.

Acceptance criteria:

- reduction and new-direction opening are distinct intents;
- reduce-only is used where applicable;
- failure during reversal cannot accidentally double directional risk.

P1.4 should consume P1.2 durable order truth and P1.3 actual-fill transition truth. It must not assume that a reversal close leg fully filled merely because it was requested or submitted.

The key unresolved boundary handed forward from P1.3 is deliberate: a reversal-open leg currently has no trustworthy `position_before_qty` until fresh state proves the close leg result. P1.4 must solve that safety problem explicitly rather than assigning an optimistic zero baseline.

Unless the roadmap is formally changed, P1.4 does **not** automatically include or claim:

- P1.5 metadata-driven size/price precision;
- P1.6 full post-submit account reconciliation;
- P1.7 complete restart-recovery matrix;
- P1.8 emergency/kill paths;
- simultaneous multi-process/distributed locking;
- production readiness.

---

## P1.3 closure baseline

P1.3 Partial-fill correctness is `PASS / MERGED` through PR #46.

Final implementation head:

```text
68bd96f86945ab0fd42ad977142fdacef6a2642d
```

Final-head evidence:

- `Phase 0 baseline contract` run #27 / Actions `31055589418`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` run #35 / Actions `31055589427`: SUCCESS;
- evidence-only PR-body governance run #36 / Actions `31055704431`: SUCCESS.

Squash/main commit:

```text
fe663a0e8115baaa5c2ae9f1a59338e8f4a0c868
```

`EXEC-PARTIAL-FILL-P1.3` is registered as `IMPLEMENTATION_VERIFIED`.

P1.3 established:

- zero / partial / full fill classification from actual reconciled fills;
- signed position movement from actual fills and order side;
- fill-implied actual position and target gap when a trustworthy baseline exists;
- separate live resting remainder versus canceled unfilled remainder;
- fail-closed local/exchange quantity consistency;
- explicit baseline-unavailable state rather than invented exposure truth;
- reversal-close actual-fill progress toward zero while leaving fresh reversal-open baseline safety to P1.4.

It did not authorize production risk and did not complete P1.4.

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
P1.3 partial-fill correctness                             COMPLETE
P1.4 reversal safety                                      CURRENT / NEXT
P1.5 precision / metadata                                 BLOCKED ON P1.4
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

P1.3 being engineering-verified and merged does not authorize live deployment, leverage expansion, new-asset execution, shorting, cycle-exit production or strategy cutover.

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

The exact next action after this handoff normalization is merged is to start **P1.4 Reversal safety** from current main on a fresh candidate branch.
