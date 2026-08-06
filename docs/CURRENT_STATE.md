# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P1.1 through P1.8: PASS / MERGED
- Phase 1: COMPLETE
- P2.1 implementation PR #58: PASS / MERGED
- Current main before P2.2: `bfb8ce4b59c36db4075a0c931e7d3d376fa97eef`
- P2.2 candidate branch: `p2-2/validate-spot-identities`

## Current roadmap position

```text
P2.1 Canonical instrument registry: PASS / MERGED
P2.2 UETH / USOL / BNB validation: CANDIDATE / NOT MERGED
P2.3+ blocked
```

## P2.2 candidate findings

- UETH is validated as Unit's Ethereum-native tokenized spot representation on Hyperliquid; Unit documents native Ethereum deposits and withdrawals.
- USOL is validated as Unit's Solana-native tokenized spot representation on Hyperliquid; Unit documents native Solana deposits and withdrawals.
- BNB has no verified Unit-native route in the official evidence set reviewed for P2.2 and remains spot-unavailable under the validated Unit route set.
- ETH/SOL spot identity verification does not authorize routing; both remain `IDENTITY_VERIFIED_ROUTING_NOT_AUTHORIZED` until P2.3/P2.4.
- Dynamic HyperCore spot token/pair indexes are runtime metadata and are not fabricated as frozen constants.
- No PnL evidence is used as identity evidence.

## Evidence sources

- Unit official About documentation: native Bitcoin, Ethereum and Solana assets can flow between native chains and Hyperliquid.
- Unit official API documentation: protocol supports chain-finalized deposit/withdrawal operations and explicitly lists Ethereum and Solana confirmation requirements.
- Unit Generate Address documentation: Ethereum and Solana are supported protocol assets with native-chain deposit/withdrawal address generation.
- Hyperliquid canonical `spotMeta` remains the runtime source for dynamic spot token/pair metadata.

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
open P2.2 PR -> authoritative CI -> evidence registry -> final-head CI -> merge -> normalize to P2.3
```
