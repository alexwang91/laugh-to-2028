# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P1.1 through P1.8: PASS / MERGED
- Phase 1: COMPLETE
- P2.1 implementation PR #58: PASS / MERGED
- P2.2 implementation PR #60: PASS / MERGED
- Current main before P2.3: `71cd245a093dc9024940513a0fc06d55703c037a`
- P2.3 implementation PR: #62 OPEN

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: PASS / MERGED
P2.3 Spot vs perp cost model: IMPLEMENTATION VERIFIED / FINAL-HEAD CI PENDING / NOT MERGED
P2.4+ blocked
```

## P2.3 implementation verified on candidate

- `beta_bot/route_cost.py` compares spot/perp only for the same asset, equal economic notional and equal holding horizon.
- Models configurable taker/maker fees, full quoted spread, beyond-spread entry/exit slippage, live depth, VWAP diagnostics, signed funding, basis/premium evolution and spot custody/redemption friction.
- Positive perp funding is a long cost; negative funding is a benefit.
- Basis cost is entry perp premium minus expected exit premium.
- Live depth/VWAP are retained for capacity and slippage diagnostics without double counting VWAP impact when it is the source of slippage.
- Explicit funding break-even horizon is available.
- `config/route_cost_model.json` freezes the model contract, comparison scope and reproducible holding-horizon scenarios, not a route decision.
- BTC/ETH/SOL are comparison assets; BNB is excluded by `ROUTER-BNB-PERP-ONLY-2026-08-06`.
- `ROUTER-COST-MODEL-P2.3 = IMPLEMENTATION_VERIFIED` is registered.

## Candidate CI evidence

Candidate head before decision/evidence writeback:

```text
cc9ee0834520168e313e5bba4a3587d17518c98b
```

passed:

- `Phase 0 baseline contract` #72 / Actions `31099792353`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #90 / Actions `31099792997`: SUCCESS.

## Fee baseline

The configurable no-staking Tier-0 baseline is:

```text
perp taker 4.5 bps
perp maker 1.5 bps
spot taker 7.0 bps
spot maker 4.0 bps
```

The model requires effective account fees to be refreshed when volume/staking tier changes.

## Self-review corrections

1. Removed double counting of VWAP impact and expected slippage. VWAP/depth are diagnostics; explicitly defined beyond-spread slippage is charged once.
2. No `spot always wins` rule is encoded. Holding horizon, signed funding, basis and liquidity remain explicit inputs for P2.4.

## Deliberately not solved

- No P2.4 route-selection reason codes or implementation plan.
- No fixed historical funding forecast is declared canonical.
- No production authorization.

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
final-head CI on PR #62 -> expected-head merge -> post-merge normalization to P2.4
```
