# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- Master plan: `docs/MASTER_PLAN_2026-08-05.md`
- Roadmap: `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
- Governance: `docs/PROJECT_GOVERNANCE_2026-08-05.md`
- Continuity protocol: `docs/CONTEXT_CONTINUITY_PROTOCOL.md`
- P1.1 through P1.8: PASS / MERGED
- Phase 1 Account and execution truth: COMPLETE
- Current main before P2.1: `f064d70da970e3b5d0b98bda094adff8eb7378bb`
- P2.1 implementation PR: #58 open

## Current roadmap position

```text
P0.1-P0.2: PASS / MERGED
P1.1-P1.8: PASS / MERGED
P2.1 Canonical instrument registry: IMPLEMENTATION VERIFIED / FINAL-HEAD CI PENDING / NOT MERGED
P2.2+ blocked
```

## P2.1 implementation verified on candidate

- `config/instrument_registry.json` is the machine-readable canonical registry for BTC / ETH / SOL / BNB;
- canonical perp identities and precision expectations are recorded;
- BTC HyperCore spot identity `UBTC/USDC` imports prior `ROUTER-DATA-0004` evidence;
- UETH/USOL remain candidate-only and BNB spot identity remains unknown; ETH/SOL/BNB are explicitly non-routable until P2.2;
- custody/redemption evidence state and availability state are explicit instead of inferred;
- liquidity metric names/sources are defined as a live-observation contract, not frozen route authorization;
- loader validation rejects missing BRRK assets, precision inconsistency and silent P2.2 spot promotion.

`ROUTER-INSTRUMENT-REGISTRY-P2.1 = IMPLEMENTATION_VERIFIED` is registered. Production authorization remains empty.

## Evidence boundary / self-review

Official Hyperliquid documentation establishes `meta`/`spotMeta` identity semantics, distinct spot token/pair IDs, the BTC UI-to-UBTC remap, and `szDecimals`-driven precision. P2.1 deliberately does not fabricate unresolved spot indexes/token IDs, custody/redemption facts, or transient liquidity values. It does not perform P2.2 validation.

## Candidate CI evidence

Candidate head:

```text
89ce55b18351e0fa3250fa253695e1e59c889d32
```

passed:

- `Phase 0 baseline contract` #52 / Actions `31097513898`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` #67 / Actions `31097513890`: SUCCESS.

The branch now contains the decision-registry record and this evidence writeback. A new final-head CI run is required before merge.

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
final-head CI on PR #58 -> expected-head merge -> post-merge normalization to P2.2
```
