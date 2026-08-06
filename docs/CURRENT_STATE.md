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
P2.2 UETH / USOL / BNB validation: IMPLEMENTATION VERIFIED / FINAL-HEAD CI PENDING / NOT MERGED
P2.3+ blocked
```

## P2.2 implementation verified on candidate

- UETH is verified as Unit's Ethereum-native tokenized spot representation on Hyperliquid; Unit documents native Ethereum deposits and withdrawals.
- USOL is verified as Unit's Solana-native tokenized spot representation on Hyperliquid; Unit documents native Solana deposits and withdrawals.
- BNB has no verified Unit-native route in the validated official evidence set and remains spot-unavailable under that route set.
- ETH/SOL remain `IDENTITY_VERIFIED_ROUTING_NOT_AUTHORIZED`; P2.2 does not implement a route decision.
- Dynamic HyperCore spot token/pair indexes remain runtime `spotMeta` data and are not fabricated as constants.
- `ROUTER-SPOT-IDENTITY-P2.2 = IMPLEMENTATION_VERIFIED` is registered.

## Candidate evidence

Candidate head before decision/evidence writeback:

```text
f337663cc0e697e3840beeef9459cea1e46ec3a8
```

passed:

- `Phase 0 baseline contract` #56 / Actions `31098385353`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #72 / Actions `31098385377`: SUCCESS.

External identity evidence:

- Unit official About documentation: native Bitcoin, Ethereum and Solana assets can flow between native chains and Hyperliquid.
- Unit official API documentation: Ethereum and Solana are supported finalized chains.
- Unit Generate Address documentation: Ethereum and Solana native deposit/withdrawal address generation is supported.

## Self-review boundary

P2.2 records identity and availability only. It does not decide that spot is economically superior, does not model funding/spread/slippage, and does not implement routing. BNB remains unavailable rather than receiving an invented `UBNB` identity.

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
final-head CI on PR #60 -> expected-head merge -> post-merge normalization to P2.3
```
