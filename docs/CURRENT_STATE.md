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
- P1.6 implementation PR #52 + handoff #53: PASS / MERGED
- Current main before P1.7: `ed5cf7ab8818e26583d8140c6ad7b8303655ac6c`
- P1.7 candidate branch: `p1-7/restart-recovery`

## Current roadmap position

```text
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: PASS / MERGED
P1.3 Partial-fill correctness: PASS / MERGED
P1.4 Reversal safety: PASS / MERGED
P1.5 Precision / metadata: PASS / MERGED
P1.6 Post-submit reconciliation: PASS / MERGED
P1.7 Restart recovery: CANDIDATE / NOT MERGED
P1.8+ blocked
```

The only active implementation task is **P1.7 Restart recovery**.

## Frozen product state

- Long universe: BTC / ETH / SOL / BNB.
- Primary venue: Hyperliquid.
- Initial capital: $2,000; recurring manual contribution about $100/week.
- Daily boundary: 00:00 UTC; intraday automation is risk-reduction only.
- Leverage is model-determined; 70% drawdown remains catastrophic tolerance only.
- FLAT means zero directional exposure; re-entry and first short activation require human approval.
- Trading Agent/API credential only; no master wallet private key, automated withdrawals or external transfers.
- Production authorization remains empty.

## P1.6 closure baseline

P1.6 cross-checks open orders, recent fills, actual position, equity and margin against durable local truth/current target. Unexplained differences block risk-increasing transitions while same-direction reductions remain available when the durable ledger is usable. `EXEC-POST-SUBMIT-RECON-P1.6 = IMPLEMENTATION_VERIFIED`.

## P1.7 candidate implementation

Roadmap acceptance matrix:

- cold restart with open order;
- cold restart with partial fill;
- cold restart after network timeout with unknown submit result;
- cold restart with actual position differing from stale local state;
- all cases resolve safely and idempotently.

Current candidate:

- adds `beta_bot/restart_recovery.py` as the explicit cold-start recovery orchestrator;
- recovery has no submit, cancel, resize or leverage-write capability;
- reuses P1.2 `reconcile_unresolved_orders()` to replay deterministic CLOID/OID/order/fill truth;
- durable asset order history is exposed read-only so the newest fill-implied local position expectation can be compared with fresh clearinghouse position;
- open orders are classified as `COLD_OPEN_ORDER_RECOVERED` and remain blocking unresolved risk rather than being duplicated;
- partial fills are reconstructed from exchange order size plus deduplicated TID fills and classified as `COLD_PARTIAL_FILL_RECOVERED`;
- a prior durable submission attempt with previously unknown result is classified as `COLD_UNKNOWN_SUBMIT_RESULT_RECOVERED` if the CLOID later becomes known at exchange;
- if that prior submit is still `unknownOid`, recovery returns `COLD_UNKNOWN_SUBMIT_RESULT_BLOCKED`, preserves the unresolved row and forbids blind retry;
- fresh clearinghouse position overrides a differing stale fill-implied local expectation and is classified as `COLD_STALE_POSITION_OVERRIDDEN_BY_EXCHANGE`;
- repeated recovery calls are economically idempotent: no order submission occurs and fill persistence remains deduplicated by TID;
- `run_strategy` now uses P1.7 as the single pre-trade replay orchestrator; P1.6 account reconciliation remains the downstream risk gate;
- post-trade P1.2/P1.6 reconciliation remains unchanged.

## P1.7 self-review correction

Initial integration layered P1.7 after the existing P1.6 pre-trade persistent reconciliation. That duplicated exchange reads and could consume an unknown-submit recovery before P1.7 classified it. The service was corrected so P1.7 is the single pre-trade replay orchestrator and internally calls the established P1.2 reconciliation. P1.6 account-level reconciliation remains the next independent safety layer.

## Candidate test coverage

- cold restart with a live open order restores OID/status and remains blocking without duplicate submission;
- repeated open-order recovery is economically idempotent;
- cold restart with partial fill reconstructs fill quantity and resting remainder;
- repeated partial-fill recovery keeps one deduplicated fill event;
- network-timeout/unknown-submit later becoming known by CLOID is recovered without resubmission;
- still-unknown submit remains explicitly blocked across repeated recoveries;
- fully reconciled local fill-implied position differing from fresh clearinghouse position is overridden by fresh account truth;
- repeated stale-position recovery produces the same safe classification;
- prior P1.6 service risk-gate tests remain isolated and preserved.

Authoritative GitHub Actions evidence is pending.

## Deliberately not solved

P1.7 does not implement P1.8 cancel-all, reduce-only emergency close, emergency FLAT or disable-new-risk command paths. It does not solve cross-process/distributed locking, order slicing, P2 routing or production readiness.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

P1.7 is the exact dependency after P1.6 and changes no BRRK economics or authorization.

## Exact next action

```text
open P1.7 PR -> authoritative CI -> fix same PR -> final-head CI -> merge -> normalize to P1.8
```
