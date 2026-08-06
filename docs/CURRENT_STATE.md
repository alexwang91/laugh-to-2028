# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P1.1 through P1.8: PASS / MERGED
- Phase 1: COMPLETE
- P2.1 implementation PR #58: PASS / MERGED
- Current main before P2.2: `bfb8ce4b59c36db4075a0c931e7d3d376fa97eef`
- P2.2 implementation PR: #60 OPEN

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: IMPLEMENTATION VERIFIED / NEW FINAL-HEAD CI REQUIRED / NOT MERGED
P2.3+ blocked
```

## P2.2 implementation state

- UETH is verified as Unit's Ethereum-native tokenized spot representation on Hyperliquid; Unit documents native Ethereum deposits and withdrawals.
- USOL is verified as Unit's Solana-native tokenized spot representation on Hyperliquid; Unit documents native Solana deposits and withdrawals.
- ETH/SOL remain `IDENTITY_VERIFIED_ROUTING_NOT_AUTHORIZED`; P2.2 does not implement a route decision.
- **BNB is an explicit product routing policy: `PERP_ONLY_DEFAULT`.** P2.2 no longer validates or searches for a BNB spot route.
- BNB spot is `NOT_ROUTABLE_BY_PRODUCT_POLICY`; no UBNB identity, custody/redemption path or spot-liquidity route is required by the current product.
- `ROUTER-BNB-PERP-ONLY-2026-08-06 = ACCEPTED_RESEARCH_TARGET` records this policy.
- `ROUTER-SPOT-IDENTITY-P2.2 = IMPLEMENTATION_VERIFIED` now covers ETH/SOL identity validation and explicitly treats BNB spot as out of scope under the frozen perp-only policy.
- Later routing logic must keep BNB on canonical BNB perp unless the product decision is explicitly reopened and approved.
- Dynamic HyperCore spot token/pair indexes remain runtime `spotMeta` data and are not fabricated as constants.
- No PnL evidence is used as identity evidence.

## Previous candidate evidence

Candidate head before the BNB product-policy refinement passed:

```text
f337663cc0e697e3840beeef9459cea1e46ec3a8
```

with:

- `Phase 0 baseline contract` #56 / Actions `31098385353`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #72 / Actions `31098385377`: SUCCESS.

The later head `8fbced6edae9a0457ddf32d9dd5d6a53ec06457e` also passed baseline #58 and governance #74, but the BNB policy refinement changed the branch afterward, so those runs are no longer final-head authority. A new final-head CI run is required.

## Evidence sources

- Unit official About/API/Generate Address documentation verifies Ethereum and Solana native deposit/withdrawal support.
- Hyperliquid canonical `spotMeta` remains the runtime source for dynamic spot token/pair metadata.
- BNB perp-only is a product routing decision, not a claim that no BNB spot market can ever exist.

## Self-review boundary

P2.2 records ETH/SOL identity and availability and freezes BNB as perp-only by product policy. It does not model funding/spread/slippage and does not implement P2.4 routing logic.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

This is an in-scope product clarification that reduces router search space; it does not expand universe, leverage, credentials, execution authority or production authorization.

## Exact next action

```text
update PR #60 body -> authoritative CI on new head -> final-head evidence -> expected-head merge -> normalize to P2.3
```
