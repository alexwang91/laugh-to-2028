# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- Master plan: `docs/MASTER_PLAN_2026-08-05.md`
- Roadmap: `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
- Governance: `docs/PROJECT_GOVERNANCE_2026-08-05.md`
- Continuity protocol: `docs/CONTEXT_CONTINUITY_PROTOCOL.md`
- P1.1 implementation PR #42 + handoff #43: PASS / MERGED
- P1.2 implementation PR #44 + handoff #45: PASS / MERGED
- P1.3 implementation PR #46 + handoff #47: PASS / MERGED
- P1.4 implementation PR #48 + handoff #49: PASS / MERGED
- P1.5 implementation PR #50 + handoff #51: PASS / MERGED
- Current main before P1.6: `181ebe60cb5d74649ee24c518ca05317ca1c7012`
- P1.6 implementation PR: #52 open
- P1.6 candidate branch: `p1-6/post-submit-reconciliation`

## Current roadmap position

```text
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: PASS / MERGED
P1.3 Partial-fill correctness: PASS / MERGED
P1.4 Reversal safety: PASS / MERGED
P1.5 Precision / metadata: PASS / MERGED
P1.6 Post-submit reconciliation: IMPLEMENTATION VERIFIED / FINAL-HEAD CI PENDING / NOT MERGED
P1.7+ blocked
```

The only active implementation task is **P1.6 Post-submit reconciliation**.

## Frozen product state

- Long universe: BTC / ETH / SOL / BNB.
- Primary venue: Hyperliquid.
- Initial capital: $2,000; recurring manual contribution about $100/week.
- Daily boundary: 00:00 UTC; intraday automation is risk-reduction only.
- Leverage is model-determined; 70% drawdown remains catastrophic tolerance only.
- FLAT means zero directional exposure; re-entry and first short activation require human approval.
- Trading Agent/API credential only; no master wallet private key, automated withdrawals or external transfers.
- Production authorization remains empty.

## P1.5 closure baseline

P1.5 removed hardcoded execution precision, consumes Hyperliquid `meta.universe.szDecimals`, formats size conservatively with Decimal/ROUND_DOWN, provides metadata-driven price formatting, and passed BTC/ETH/SOL/BNB formatting tests. `EXEC-PRECISION-METADATA-P1.5 = IMPLEMENTATION_VERIFIED`.

## P1.6 implementation verified on candidate

Roadmap requirement: after every trading cycle fetch open orders, fills, positions and account equity/margin, then compare them with local ledger and current target.

PR #52 candidate:

- adds an account-level reconciliation report containing actual position, target gap, account equity, total margin used, exchange open-order CLOIDs, local active CLOIDs, recent-fill count and deterministic blocking reason codes;
- fetches Hyperliquid open orders, recent fills and fresh clearinghouse state around each trade cycle in addition to the existing persistent order reconciliation;
- compares exchange open orders with local active ledger truth;
- treats malformed/uncorrelatable open-order and fill evidence as explicit reconciliation blockers rather than silently ignoring it;
- carries P1.2 persistent unresolved truth into the account-level gate;
- classifies whether the planned target transition increases directional risk;
- any unexplained difference blocks opening, increasing or reversing directional exposure;
- same-direction reduction and target-to-FLAT remain available when exchange discrepancies exist;
- `LedgerUncertainState` from P1.2 is converted by the service into a risk-increase blocker so reduce-risk execution can still proceed when the durable ledger itself remains usable;
- core account position/equity/margin parse failure still fails closed because safe risk classification is impossible;
- post-submit persistent and account reconciliation are both recorded in the cycle payload.

`EXEC-POST-SUBMIT-RECON-P1.6 = IMPLEMENTATION_VERIFIED` is registered in `config/decision_registry.json`. This is candidate engineering verification only; P1.6 is not merged and production authorization remains empty.

## P1.6 self-review corrections

1. Initial design treated malformed exchange open-order/fill evidence as a global exception. That would also block reductions, violating P1.6. It was corrected to deterministic blocking reason codes that prohibit risk increase but preserve same-direction reductions.
2. Initial service path still let P1.2 `LedgerUncertainState` abort the cycle before target classification. It was corrected so this uncertainty feeds the P1.6 risk gate; durable-ledger infrastructure failure is not relaxed.

## Candidate test coverage

- clean reconciliation allows risk increase;
- unknown exchange open order blocks risk increase;
- local active order missing from exchange blocks risk increase;
- P1.2 unresolved truth propagates into the account gate;
- open order without CLOID and malformed rows become blocking reason codes;
- recent fill without OID/TID becomes a blocking reason code;
- risk classifier covers increase, decrease, FLAT and reversal cases;
- service test proves unexplained reconciliation blocks an increase;
- service test proves the same uncertainty still permits same-direction reduction;
- missing core margin truth fails closed.

## Candidate CI evidence

Candidate head before registry/evidence finalization:

```text
dde987bf89b92aa75621fad91bb6a53eda738576
```

That head passed:

- `Phase 0 baseline contract` run #38 / Actions `31092971639`: SUCCESS;
- execution tests inside the contract: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` run #49 / Actions `31092972019`: SUCCESS.

The branch now also contains the decision-registry record and this evidence update. A new final-head CI run is required before merge.

## Deliberately not solved

P1.6 does not claim P1.7 restart matrix, P1.8 emergency/kill paths, cross-process locking, order slicing, P2 router completion, multi-asset production readiness or production authorization.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

P1.6 is the exact roadmap dependency after P1.5 and changes no strategy economics or product authorization.

## Exact next action

```text
final-head CI on PR #52 -> merge -> normalize handoff to P1.7
```
