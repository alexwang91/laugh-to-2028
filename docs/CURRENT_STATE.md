# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P1.1 through P1.8: PASS / MERGED
- Phase 1: COMPLETE
- P2.1 implementation PR #58: PASS / MERGED
- P2.2 implementation PR #60: PASS / MERGED
- Current main before P2.3: `71cd245a093dc9024940513a0fc06d55703c037a`
- P2.3 candidate branch: `p2-3/spot-perp-cost-model`

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: PASS / MERGED
P2.3 Spot vs perp cost model: CANDIDATE / NOT MERGED
P2.4+ blocked
```

## P2.3 candidate implementation

- Adds `beta_bot/route_cost.py` for same-asset, equal-notional, equal-horizon spot/perp economic comparison.
- Models taker/maker fees, full spread, expected entry/exit slippage, live depth, observed VWAP impact, signed funding, basis/premium evolution, custody/redemption friction and holding duration.
- Positive perp funding is a long cost; negative funding is a long benefit.
- Basis cost is explicit as entry perp premium minus expected exit premium.
- Live depth and VWAP impact are preserved as capacity/measurement diagnostics.
- VWAP impact is **not** added a second time when expected slippage is derived from the same order-book observation.
- Adds explicit positive-funding break-even horizon calculation.
- Adds `config/route_cost_model.json` with reproducible comparison scope, fee baseline, holding horizons and measurement definitions.
- Comparison scope is BTC / ETH / SOL. BNB is excluded by `ROUTER-BNB-PERP-ONLY-2026-08-06`.

## Fee baseline

Current configurable baseline uses Hyperliquid Tier-0 base fees with no staking discount:

```text
perp taker 4.5 bps
perp maker 1.5 bps
spot taker 7.0 bps
spot maker 4.0 bps
```

Fee schedule is explicitly an input, not a permanent constant: account volume tier and staking discount must refresh it when used for live routing analysis.

## Self-review corrections

1. Initial model added both order-book VWAP impact and expected slippage to total cost. Because slippage can be derived from the same VWAP observation, that can double count impact. Corrected: VWAP/depth are diagnostics; total cost charges explicitly defined slippage beyond spread once.
2. No static conclusion such as `spot always wins` is encoded. Holding horizon, signed funding, basis and liquidity remain explicit inputs so P2.4 can make reproducible decisions later.

## Deliberately not solved

- No P2.4 route-selection reason codes or execution plan.
- No fixed historical funding forecast is declared canonical in P2.3.
- No production authorization.
- BNB spot remains outside scope by canonical policy.

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
open P2.3 PR -> authoritative CI -> fix same PR -> register evidence -> final-head CI -> merge -> normalize to P2.4
```
