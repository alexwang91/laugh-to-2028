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
- P1.7 implementation PR: #54 open
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
P1.7 Restart recovery: IMPLEMENTATION VERIFIED / FINAL-HEAD CI PENDING / NOT MERGED
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

## P1.7 implementation verified on candidate

PR #54 implements the four-case cold-start matrix:

- `COLD_OPEN_ORDER_RECOVERED`: live exchange order is restored by deterministic CLOID/OID and remains blocking instead of being duplicated;
- `COLD_PARTIAL_FILL_RECOVERED`: fill quantity and resting remainder are reconstructed from exchange order size and deduplicated TID fill truth;
- `COLD_UNKNOWN_SUBMIT_RESULT_RECOVERED`: durable attempt with no locally persisted submission response is recovered if exchange later exposes the CLOID;
- `COLD_UNKNOWN_SUBMIT_RESULT_BLOCKED`: if the exchange still returns `unknownOid`, the durable row remains unresolved and blind retry is forbidden;
- `COLD_STALE_POSITION_OVERRIDDEN_BY_EXCHANGE`: fresh clearinghouse position overrides a differing stale fill-implied local position expectation.

The recovery orchestrator has no submit/cancel/resize/leverage-write capability. `run_strategy` uses it as the single pre-trade persistent replay path, followed by the independent P1.6 account reconciliation/risk gate. Repeated recovery is economically idempotent and fill events remain deduplicated by TID.

`EXEC-RESTART-RECOVERY-P1.7 = IMPLEMENTATION_VERIFIED` is registered. This is candidate engineering verification only; P1.7 is not merged and production authorization remains empty.

## P1.7 self-review / CI corrections

1. Initial service integration layered P1.7 after the previous pre-trade P1.6 persistent reconciliation. This duplicated reads and could consume an unknown-submit recovery before P1.7 classified it. Corrected so P1.7 is the single pre-trade replay orchestrator and internally reuses P1.2 reconciliation; P1.6 account reconciliation remains downstream.
2. First authoritative Phase 0 run #42 / Actions `31094167207` failed execution tests because the unknown-submit recovery label was not report-idempotent: after first exchange discovery, the newly persisted OID caused the second recovery to lose the original unknown-submit lineage. Corrected lineage semantics to `submission_attempt_timestamp_ms != null && submission_response_timestamp_ms == null`; exchange OID now determines recovered-vs-blocked state without erasing lineage.

## Candidate test coverage

- open-order cold restart and repeated recovery;
- partial-fill cold restart and repeated fill deduplication;
- unknown submit later recovered by CLOID;
- still-unknown submit remains blocked across repeated recovery with no blind retry;
- fresh actual position overrides stale local expectation;
- repeated stale-position recovery returns the same classification;
- prior P1.6 risk-increase and reduce-risk service gate remains preserved.

## Candidate CI evidence

Corrected candidate head before registry/evidence finalization:

```text
8e8f600cec1af1c3c9262f827275bdcc25562ed0
```

That head passed:

- `Phase 0 baseline contract` run #43 / Actions `31094408611`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` run #55 / Actions `31094408568`: SUCCESS.

The branch now also contains the P1.7 decision-registry record and this evidence update. A new final-head CI run is required before merge.

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
final-head CI on PR #54 -> merge -> normalize handoff to P1.8
```
