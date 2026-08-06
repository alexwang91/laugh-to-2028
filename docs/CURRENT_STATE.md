# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P1.1 through P1.8: PASS / MERGED
- Phase 1: COMPLETE
- P2.1 implementation PR #58: PASS / MERGED
- P2.2 implementation PR #60: PASS / MERGED
- P2.2 final implementation head: `882f404d5bda11839c52ed92167fb96cb3097353`
- P2.2 squash/main commit: `d8a2554ea520f73e77eee9816108261fdaaf762f`

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 ETH / SOL spot validation + BNB perp-only policy: PASS / MERGED
P2.3 Spot vs perp cost model: NEXT
P2.4+ blocked
```

## P2.2 PASS / MERGED

- UETH is verified as Unit's Ethereum-native tokenized spot representation on Hyperliquid, with native Ethereum deposit/withdrawal support.
- USOL is verified as Unit's Solana-native tokenized spot representation on Hyperliquid, with native Solana deposit/withdrawal support.
- ETH/SOL remain `IDENTITY_VERIFIED_ROUTING_NOT_AUTHORIZED`; identity verification alone does not authorize routing.
- `ROUTER-BNB-PERP-ONLY-2026-08-06 = ACCEPTED_RESEARCH_TARGET` freezes BNB as `PERP_ONLY_DEFAULT`; BNB spot is outside current router scope unless that decision is explicitly reopened.
- `ROUTER-SPOT-IDENTITY-P2.2 = IMPLEMENTATION_VERIFIED` records the P2.2 identity boundary.
- Dynamic HyperCore token/pair indexes remain runtime `spotMeta` metadata rather than fabricated constants.

## P2.2 final evidence

Final implementation head:

```text
882f404d5bda11839c52ed92167fb96cb3097353
```

passed:

- `Phase 0 baseline contract` #70 / Actions `31099064883`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #88 / Actions `31099065127`: SUCCESS.

PR #60 squash-merged to main as:

```text
d8a2554ea520f73e77eee9816108261fdaaf762f
```

## Current unique next task: P2.3 Spot vs perp cost model

Build the economic comparison for BTC / ETH / SOL only:

- spot trading fees/spread/slippage;
- perp trading fees/spread/slippage;
- realized/expected funding drag or benefit;
- holding-horizon sensitivity;
- liquidity/capacity observations;
- explicit treatment of custody/redemption or bridge friction where economically relevant.

BNB is not part of the spot-vs-perp comparison because the canonical product decision fixes BNB to `PERP_ONLY_DEFAULT`.

P2.3 must not silently implement P2.4 route decisions or production authorization.

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
P2.3 Spot vs perp cost model
```

Start from current main after this post-merge normalization is merged, on a fresh candidate branch.
