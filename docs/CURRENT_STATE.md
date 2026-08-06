# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P1.1 through P1.8: PASS / MERGED
- Phase 1: COMPLETE
- P2.1 implementation PR #58: PASS / MERGED
- P2.2 implementation PR #60: PASS / MERGED
- P2.3 implementation PR #62: PASS / MERGED
- P2.3 final implementation head: `3a6dc02a560aa47be9a95e58942fe7814ae6c511`
- P2.3 squash/main commit: `e890aebc1764ab872b9446ab755fde793c48a77d`

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: PASS / MERGED
P2.3 Spot vs perp cost model: PASS / MERGED
P2.4 Router decision: NEXT
P3+ blocked
```

## P2.3 PASS / MERGED

P2.3 established a reproducible BTC/ETH/SOL spot-versus-perp economic comparison using equal asset, equal notional and equal holding horizon.

Model inputs include configurable maker/taker fees, quoted spread, beyond-spread slippage, live depth/VWAP diagnostics, signed perp funding, basis evolution and spot custody/redemption friction. Positive funding costs the long; negative funding benefits it. VWAP impact is not double-counted when it is used to derive slippage.

`config/route_cost_model.json` freezes the measurement contract and holding-horizon scenarios, not a route choice. BNB remains excluded under `ROUTER-BNB-PERP-ONLY-2026-08-06`.

`ROUTER-COST-MODEL-P2.3 = IMPLEMENTATION_VERIFIED` is registered.

## P2.3 final evidence

Final implementation head:

```text
3a6dc02a560aa47be9a95e58942fe7814ae6c511
```

passed:

- `Phase 0 baseline contract` #74 / Actions `31100005137`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #92 / Actions `31100003917`: SUCCESS.

PR #62 squash-merged to main as:

```text
e890aebc1764ab872b9446ab755fde793c48a77d
```

## Current unique next task: P2.4 Router decision

The target engine requests economic exposure; the router must return an implementation plan plus deterministic reason code.

Required behavior:

- use the P2.1/P2.2 verified instrument registry;
- use P2.3 cost-model inputs and assumptions;
- keep BNB `PERP_ONLY_DEFAULT`;
- shorts require perp;
- leverage-overlay exposure requires perp;
- fail closed when liquidity/identity evidence is insufficient;
- log every routing decision and assumptions so research can reproduce it.

Example reason-code family from roadmap:

```text
SPOT_VERIFIED_LOWER_COST
PERP_SPOT_UNVERIFIED
PERP_REQUIRED_FOR_SHORT
PERP_REQUIRED_FOR_LEVERAGE_OVERLAY
NO_TRADE_LIQUIDITY_FAIL
```

P2.4 does not authorize production trading or change BRRK economics.

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
P2.4 Router decision
```

Start from current main after this documentation-only normalization is merged, on a fresh candidate branch.
