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
- P2.1 candidate branch: `p2-1/canonical-instrument-registry`

## Current roadmap position

```text
P0.1-P0.2: PASS / MERGED
P1.1-P1.8: PASS / MERGED
P2.1 Canonical instrument registry: CANDIDATE / NOT MERGED
P2.2+ blocked
```

## P2.1 candidate implementation

- adds `config/instrument_registry.json` as the machine-readable canonical registry for BTC / ETH / SOL / BNB;
- records canonical perp identities, size precision and derived price-decimal caps;
- imports BTC HyperCore spot identity `UBTC/USDC` from prior decision `ROUTER-DATA-0004` rather than rediscovering it;
- records UETH and USOL only as P2.2 candidates and leaves BNB spot identity unknown; none are routable in P2.1;
- records custody/redemption evidence status explicitly rather than inferring it from UI names or PnL;
- defines the live liquidity metric contract and official Hyperliquid metadata sources without freezing transient market observations into routing authorization;
- adds a validated loader and tests that reject silent P2.2 spot authorization.

## Evidence boundary

Official Hyperliquid API documentation establishes that perp identity comes from `meta`, spot identity/token fields come from `spotMeta`, spot pair IDs differ from token IDs, UI names may be remapped (explicitly BTC/USDC -> UBTC/USDC), and precision is driven by `szDecimals` with 6-perp / 8-spot decimal bases and five significant price figures.

P2.1 deliberately does not validate UETH/USOL/BNB identity, token IDs, custody/redemption mechanisms or routing economics. Those remain P2.2+.

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
open P2.1 PR -> authoritative CI -> self-review corrections if any -> register evidence -> final-head CI -> merge -> normalize handoff to P2.2
```
