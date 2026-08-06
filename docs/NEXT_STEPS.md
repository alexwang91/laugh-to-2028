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
P1.5 Precision / metadata
```

P0.1, P0.2, P1.1, P1.2, P1.3 and P1.4 are merged and complete. P1.5 is now the only authorized next implementation dependency.

Do not start P1.6 post-submit reconciliation, P2 router work, P3 target-engine work, P4 leverage work, P5 cycle-exit research or P8 bear-short research early.

---

## P1.5 acceptance boundary

Roadmap requirement:

> Remove hardcoded size and price precision.

Acceptance criteria:

- asset metadata drives valid order formatting;
- all BRRK instruments pass formatting tests.

P1.5 should introduce a canonical metadata-driven formatting layer for BTC / ETH / SOL / BNB. It must remove the current hardcoded BTC order-size rounding assumption from execution code.

P1.5 does **not** by itself authorize multi-asset production execution. Product-universe membership and formatting correctness are separate from P2 routing/identity validation and later production authorization.

Unless the roadmap is formally changed, P1.5 does not include or claim:

- P1.6 full post-submit account reconciliation;
- P1.7 complete restart recovery;
- P1.8 emergency/kill paths;
- P2 route selection;
- P3 production-quality BRRK target generation;
- P4 leverage research completion;
- P5 cycle-top research completion;
- production readiness.

---

## P1.4 closure baseline

P1.4 Reversal safety is `PASS / MERGED` through PR #48.

Final implementation head:

```text
879ce2da3b1e4382473037650c3fca30cda7f63f
```

Final-head evidence:

- `Phase 0 baseline contract` run #32 / Actions `31078243843`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` run #41 / Actions `31078243847`: SUCCESS;
- evidence-only PR-body governance run #42 / Actions `31078303601`: SUCCESS.

Squash/main commit:

```text
7acb093af59825c39fd092f232573666682197d8
```

`EXEC-REVERSAL-SAFETY-P1.4` is registered as `IMPLEMENTATION_VERIFIED`.

P1.4 established:

- distinct `reduce` and `increase` intents during reversal;
- reduce-only close semantics;
- fresh account-position verification after the close leg;
- no new-direction open until old-direction exposure is proven flat;
- fail-closed behavior for partial close, unexpected cross-through, malformed state and fresh-state read failure.

P1.4 did not authorize production risk and did not implement P1.5.

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
P1.4 reversal safety                                      COMPLETE
P1.5 precision / metadata                                 CURRENT / NEXT
P1.6 post-submit reconciliation                           BLOCKED ON P1.5
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

P1.4 engineering verification does not authorize live deployment, leverage expansion, new-asset execution, shorting, cycle-exit production or strategy cutover.

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

The exact next action after this handoff normalization is merged is to start **P1.5 Precision / metadata** from current main on a fresh candidate branch.