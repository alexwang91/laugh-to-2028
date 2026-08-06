# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- Master plan: `docs/MASTER_PLAN_2026-08-05.md`
- Roadmap: `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
- Governance: `docs/PROJECT_GOVERNANCE_2026-08-05.md`
- Continuity protocol: `docs/CONTEXT_CONTINUITY_PROTOCOL.md`
- P1.1 through P1.8: PASS / MERGED
- P1.8 implementation PR: #56 PASS / MERGED
- P1.8 final implementation head: `3d1715dafda8edc5d8a37d1de7a2a2de56b0e587`
- P1.8 squash/main commit: `765fc53dfcb3699ffc1de530717349cf926b42ed`

## Current roadmap position

```text
P0.1-P0.2: PASS / MERGED
P1.1-P1.8: PASS / MERGED
Phase 1 Account and execution truth: COMPLETE
P2.1 Canonical instrument registry: NEXT
P2.2+ blocked
```

The unique next implementation task is **P2.1 Canonical instrument registry**.

## Frozen product state

- Long universe: BTC / ETH / SOL / BNB.
- Primary venue: Hyperliquid.
- Initial capital: $2,000; recurring manual contribution about $100/week.
- Daily boundary: 00:00 UTC; intraday automation is risk-reduction only.
- Leverage is model-determined; 70% drawdown remains catastrophic tolerance only.
- FLAT means zero directional exposure; re-entry and first short activation require human approval.
- Trading Agent/API credential only; no master wallet private key, automated withdrawals or external transfers.
- Production authorization remains empty.

## P1.8 PASS / MERGED

PR #56 closed the Phase 1 emergency-control acceptance boundary:

- cancel-all follows fresh exchange open-order truth;
- reduce-only close follows fresh clearinghouse position and metadata-driven size formatting;
- emergency FLAT cancels open orders, closes every observed non-zero perp position, then requires a second fresh clearinghouse read proving zero remaining position before reporting success;
- explicit non-ok/rejected exchange responses fail closed;
- durable atomic disable-new-risk switch blocks normal risk-increasing transitions while preserving same-direction reductions;
- malformed/unreadable switch state fails closed for new risk without disabling reductions;
- `emergency_once.py` provides a direct control-plane entrypoint independent of signal/portfolio/target-engine health.

`EXEC-KILL-EMERGENCY-P1.8 = IMPLEMENTATION_VERIFIED` is registered.

## P1.8 review corrections retained

1. Kill-switch uncertainty originally raised in trade mode and could also block reduction. Corrected so uncertainty is treated as new-risk disabled while reduction remains available.
2. Emergency actions originally treated a returned API call as sufficient success. Corrected to reject explicit exchange errors; emergency FLAT additionally requires fresh verified-flat account truth.

## P1.8 final evidence

Candidate head `3d2f0f662d5fb98d42a6d809004b3ad4bd6592ed` passed:

- `Phase 0 baseline contract` #48 / Actions `31096773496`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #62 / Actions `31096773499`: SUCCESS.

Final implementation head:

```text
3d1715dafda8edc5d8a37d1de7a2a2de56b0e587
```

passed:

- `Phase 0 baseline contract` #50 / Actions `31096925400`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #64 / Actions `31096925378`: SUCCESS.

PR #56 squash-merged to main as:

```text
765fc53dfcb3699ffc1de530717349cf926b42ed
```

## Current unique next task: P2.1 Canonical instrument registry

For BTC, ETH, SOL and BNB record:

- spot token identity;
- perp identity;
- decimals / tick size;
- custody/redemption facts where relevant;
- liquidity metrics;
- availability state.

BTC spot identity already has prior evidence and should be imported rather than rediscovered.

P2.1 must not silently perform P2.2 UETH/USOL/BNB validation, P2.3 cost modeling, P2.4 routing decisions, or production authorization.

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
P2.1 Canonical instrument registry
```

Start from current main after this post-merge normalization is merged, on a fresh candidate branch.
