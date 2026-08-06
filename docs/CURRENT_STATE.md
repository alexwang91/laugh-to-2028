# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- Master plan: `docs/MASTER_PLAN_2026-08-05.md`
- Roadmap: `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
- Governance: `docs/PROJECT_GOVERNANCE_2026-08-05.md`
- Continuity protocol: `docs/CONTEXT_CONTINUITY_PROTOCOL.md`
- P1.1 through P1.7: PASS / MERGED
- Current main before P1.8: `4af547a96ca15a419ba7c3e3ae7892e5e912def6`
- P1.8 candidate branch: `p1-8/kill-emergency-paths`

## Current roadmap position

```text
P0.1-P0.2: PASS / MERGED
P1.1-P1.7: PASS / MERGED
P1.8 Kill and emergency paths: CANDIDATE / NOT MERGED
P2+ blocked
```

The only active implementation task is **P1.8 Kill and emergency paths**.

## Frozen product state

- Long universe: BTC / ETH / SOL / BNB.
- Primary venue: Hyperliquid.
- Initial capital: $2,000; recurring manual contribution about $100/week.
- Daily boundary: 00:00 UTC; intraday automation is risk-reduction only.
- Leverage is model-determined; 70% drawdown remains catastrophic tolerance only.
- FLAT means zero directional exposure; re-entry and first short activation require human approval.
- Trading Agent/API credential only; no master wallet private key, automated withdrawals or external transfers.
- Production authorization remains empty.

## P1.8 candidate implementation

Roadmap requirements:

- cancel-all;
- reduce-only close;
- emergency FLAT;
- disable-new-risk switch;
- controlled/testnet proof;
- emergency control must not depend on the normal target engine being healthy.

Candidate implementation:

- adds `beta_bot/emergency.py`, a direct risk-reduction control plane with no signal/portfolio/target-engine dependency;
- `cancel_all()` reads fresh exchange open orders and cancels each exact coin/OID;
- `reduce_only_close()` reads fresh clearinghouse position and uses existing Hyperliquid `market_close` reduce-only semantics with metadata-driven size formatting;
- `emergency_flat()` cancels open orders, closes every non-zero perp position found in fresh clearinghouse state, then performs a second fresh read and only reports `verified_flat` if no position remains;
- explicit non-ok/rejected exchange responses fail the emergency command instead of being reported as success;
- a durable atomic `NewRiskKillSwitch` blocks normal risk-increasing transitions while preserving same-direction reductions;
- malformed/unreadable kill-switch state fails closed for new risk but does not disable reduction paths;
- `emergency_once.py` exposes `cancel-all`, `reduce-only-close`, `emergency-flat`, and `disable-new-risk` without invoking the normal target engine;
- `.env.example` documents the persistent switch path and emergency command selector.

## Candidate controlled tests

- cancel-all follows exchange open-order truth;
- reduce-only close uses fresh position and never opens direction;
- emergency FLAT cancels, closes all observed positions and requires fresh verified-flat state;
- remaining position after close causes emergency FLAT failure;
- explicit exchange rejection is not reported as success;
- disable-new-risk persists atomically;
- malformed switch state blocks new risk;
- service-level switch blocks a clean risk increase while preserving same-direction reduction.

## Self-review corrections

1. Initial kill-switch uncertainty handling raised an exception in trade mode, which could also prevent reduction. Corrected so uncertainty is interpreted as `new risk disabled` while reduction remains available.
2. Initial emergency actions only recorded that API calls returned. Corrected to reject explicit non-ok/error responses; emergency FLAT additionally requires a second fresh clearinghouse read proving zero remaining perp positions before reporting success.

## Deliberately not solved

- No P2 instrument routing or spot identity work.
- No new production authorization.
- No leverage expansion or strategy economics changes.
- Cross-process locking and order slicing remain outside this task.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

P1.8 is exact execution hardening from the roadmap and changes no BRRK economics or authorization.

## Exact next action

```text
open P1.8 PR -> authoritative CI -> fix same PR -> register evidence -> final-head CI -> merge -> normalize handoff to P2.1
```
