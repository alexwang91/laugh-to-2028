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
- P1.6 implementation PR #52 merged; squash/main commit `1a8addc6225446d287ab0465f0f9b555242b6739`
- P1.6 final implementation head: `fd8ac395189bd6ce134eaeb5c1ae4bf1ac1a6ae5`

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
P1.7 Restart recovery: NEXT
P1.8+ blocked
```

The unique next implementation task is **P1.7 Restart recovery**.

## Frozen product state

- Long universe: BTC / ETH / SOL / BNB.
- Primary venue: Hyperliquid.
- Initial capital: $2,000; recurring manual contribution about $100/week.
- Daily boundary: 00:00 UTC; intraday automation is risk-reduction only.
- Leverage is model-determined; 70% drawdown remains catastrophic tolerance only.
- FLAT means zero directional exposure; re-entry and first short activation require human approval.
- Trading Agent/API credential only; no master wallet private key, automated withdrawals or external transfers.
- Production authorization remains empty.

## P1.6 PASS / MERGED

PR #52 established account-level post-submit reconciliation:

- each trade-capable cycle fetches exchange open orders, recent fills and fresh clearinghouse state;
- actual position, target gap, account equity and total margin used are included in an account reconciliation report;
- exchange open orders are compared with local active ledger truth;
- malformed/uncorrelatable open-order and fill evidence becomes deterministic blocking reason codes;
- persistent P1.2 unresolved truth propagates into the account-level gate;
- unexplained differences prohibit opening, increasing or reversing directional exposure;
- same-direction reductions and target-to-FLAT remain available when the durable ledger itself is still usable;
- P1.2 `LedgerUncertainState` is converted at service level into a risk-increase blocker rather than globally preventing reduction;
- core account position/equity/margin parse failure remains fail-closed;
- pre/post persistent and account reconciliation are recorded in each cycle payload.

Self-review corrections retained:

1. malformed exchange evidence was changed from a global exception to blocking reason codes so reductions remain available;
2. P1.2 uncertainty was changed from a service-level abort to a P1.6 risk gate input while durable-ledger infrastructure failures remain fail-closed.

`EXEC-POST-SUBMIT-RECON-P1.6 = IMPLEMENTATION_VERIFIED` is registered. Production authorization remains empty.

## P1.6 final evidence

Final implementation head:

```text
fd8ac395189bd6ce134eaeb5c1ae4bf1ac1a6ae5
```

Final evidence:

- `Phase 0 baseline contract` run #40 / Actions `31093119316`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` run #51 / Actions `31093117491`: SUCCESS;
- evidence-only PR-body governance run #52 / Actions `31093191350`: SUCCESS.

PR #52 squash-merged to main as `1a8addc6225446d287ab0465f0f9b555242b6739`.

## Current unique next task: P1.7 Restart recovery

Acceptance criteria:

- cold restart with open order;
- cold restart with partial fill;
- cold restart after network timeout with unknown submit result;
- cold restart with actual position differing from stale local state;
- all cases resolve safely and idempotently.

P1.7 must build on P1.2 durable order truth, P1.3 actual-fill transitions and P1.6 account reconciliation. It must not silently include P1.8 emergency commands or P2 routing.

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
P1.7 Restart recovery
```

Start from current main after this post-merge normalization is merged, on a fresh candidate branch.
