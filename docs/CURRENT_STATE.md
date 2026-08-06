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
- P1.7 implementation PR #54: PASS / MERGED
- P1.7 final implementation head: `56cc6d6a4547297dae93e33c390c26570c364bf6`
- P1.7 squash/main commit: `03ee46bf234175bb54745de79b225711ecbc740b`

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
P1.7 Restart recovery: PASS / MERGED
P1.8 Kill and emergency paths: NEXT
P2+ blocked
```

The unique next implementation task is **P1.8 Kill and emergency paths**.

## Frozen product state

- Long universe: BTC / ETH / SOL / BNB.
- Primary venue: Hyperliquid.
- Initial capital: $2,000; recurring manual contribution about $100/week.
- Daily boundary: 00:00 UTC; intraday automation is risk-reduction only.
- Leverage is model-determined; 70% drawdown remains catastrophic tolerance only.
- FLAT means zero directional exposure; re-entry and first short activation require human approval.
- Trading Agent/API credential only; no master wallet private key, automated withdrawals or external transfers.
- Production authorization remains empty.

## P1.7 PASS / MERGED

PR #54 closed the required restart-recovery matrix:

- cold restart with open order;
- cold restart with partial fill;
- cold restart after network timeout with unknown submit result;
- cold restart with actual position differing from stale local state;
- repeated recovery is economically idempotent and never blind-resubmits unknown prior submissions.

Fresh clearinghouse position overrides stale fill-implied local expectation. Open/partial unresolved orders remain blocking until exchange lifecycle resolution. `run_strategy` uses the recovery orchestrator before the downstream P1.6 account reconciliation gate.

`EXEC-RESTART-RECOVERY-P1.7 = IMPLEMENTATION_VERIFIED` is registered.

## P1.7 review corrections retained

1. Removed duplicate pre-trade persistent reconciliation so P1.7 is the single cold-start replay orchestrator and P1.6 remains the downstream account gate.
2. Fixed unknown-submit lineage so repeated recovery reports remain idempotent after an exchange OID becomes visible.

## P1.7 final evidence

Final implementation head:

```text
56cc6d6a4547297dae93e33c390c26570c364bf6
```

passed:

- `Phase 0 baseline contract` #46 / Actions `31095951858`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #60 / Actions `31095951582`: SUCCESS.

PR #54 squash-merged to main as:

```text
03ee46bf234175bb54745de79b225711ecbc740b
```

## Current unique next task: P1.8 Kill and emergency paths

Implement:

- cancel-all;
- reduce-only close;
- emergency FLAT;
- disable-new-risk switch.

Acceptance criteria:

- testnet / controlled test proves each path;
- emergency path does not depend on the normal target engine being healthy.

P1.8 must not silently include P2 routing or production authorization.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
P1.8 Kill and emergency paths
```

Start from current main after this post-merge normalization is merged, on a fresh candidate branch.
