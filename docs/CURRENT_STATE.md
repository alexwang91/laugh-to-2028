# BRRK Current State

Last updated: 2026-08-05
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- Master plan: `docs/MASTER_PLAN_2026-08-05.md`
- Roadmap: `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
- Governance: `docs/PROJECT_GOVERNANCE_2026-08-05.md`
- Continuity protocol: `docs/CONTEXT_CONTINUITY_PROTOCOL.md`
- Planning PR: #38 merged
- Context-handoff governance PR: #39 merged
- Current candidate branch: `phase0/canonical-config-registry`

## Current roadmap position

```text
PLANNING BASELINE: complete
CONTEXT-HANDOFF GOVERNANCE: complete
P0.1 Canonical product config: candidate implemented, pending PR/CI closure
P0.2 Decision registry: candidate implemented, pending PR/CI closure
P1.1 Deterministic order identity: NEXT only after Phase 0 closes
P1+: not authorized to skip ahead
```

## Product state frozen by the master plan

- Long universe: BTC / ETH / SOL / BNB.
- Initial managed capital: $2,000 cash/stablecoin.
- Recurring capital: user manually contributes about $100/week.
- Primary venue: Hyperliquid.
- Official daily boundary: 00:00 UTC.
- Daily strategy decisions; intraday automation may only reduce risk.
- Concentration/diversification is dynamic.
- Leverage is model-determined, not a user-fixed constant.
- 70% drawdown is catastrophic tolerance only, not an operating target.
- Cycle exit is market-state based, not tied to a literal 2028 date.
- Late-bull rotation may increase relative alt weights while total gross exposure decreases.
- FLAT = zero directional exposure.
- Re-entry from FLAT and first short activation in a new bear phase require human approval.
- Bot may use a trading Agent/API credential only; never the master wallet private key and never automated withdrawals.
- Strategy upgrades use candidate/shadow plus manual blue-green cutover; no hot strategy patching.

## Phase 0 candidate implementation

P0.1 adds:

- `config/product.json` as the canonical machine-readable product baseline;
- `execution/plan-b-bot/beta_bot/product_config.py` as a validated loader;
- execution settings now consume the canonical product config before applying the narrower BTC-only implementation capability;
- explicit distinction between product universe and current executor capability;
- research and execution contract tests reading the same source file;
- `phase0-baseline.yml` CI contract.

P0.2 adds:

- `config/decision_registry.json` with accepted research targets, implementation-verified evidence, shadow-only lines, stopped/rejected lines and explicit production-authorized set;
- stopped historical lines are machine-readable so future tasks can detect that they must not be silently reopened.

## Research boundaries that must remain closed unless formally reopened

- Do not silently rescue stopped carry work.
- Do not rescue rejected TSMOM or historical alpha lines by parameter/window/asset retuning.
- Do not treat prior ASYM-BETA extra sleeve as an approved leverage implementation.
- Do not infer spot identity from PnL; UETH/USOL identity/custody validation remains separate.

## Current evidence status

- BRRK-0011 remains the frozen directional research target.
- Hyperliquid all-perp implementation is economically inferior to spot-aware routing on the tested window.
- BTC spot/UBTC identity has public verification; ETH/SOL spot identity remains an explicit later router validation item.
- Execution production readiness is not established: deterministic order identity, persistent ledger, partial-fill lifecycle, reconciliation, idempotency, slicing, kill paths and executor lifecycle tests remain required.
- Dynamic leverage above the current BRRK scale is not yet production-authorized.
- Cycle-top/exit model is not yet validated; future study must include 2021 two-wave structure and 2025 multi-peak structure.
- Bear-market Top-20 short expansion is research-only and deferred.
- Phase 0 evidence is not final until candidate PR CI and governance checks pass.

## Production authorization

```text
Strategy change from Phase 0: NONE
New live capital authorization: NONE
Leverage expansion authorization: NONE
Short authorization: NONE
```

## Open blockers / uncertainties

1. Phase 0 candidate must pass PR governance and Phase-0 CI before being considered closed.
2. Execution account/order/fill truth is not yet hardened; this becomes Phase 1.
3. Operating drawdown budget is intentionally not frozen until leverage research.
4. Cycle-exit signal parameters/timeframes are intentionally not frozen until historical/walk-forward study.

## Latest project-drift assessment

```text
DRIFT_0
```

Reason: Phase 0 implements the exact next roadmap dependency. It does not change strategy economics, risk limits, venue, asset universe, approval boundaries or production authorization. Legacy BTC-only and beta-cap behavior is explicitly treated as current execution capability/research legacy rather than canonical product policy.

## Exact next unblocked task

If and only if the Phase 0 PR passes CI/review and merges:

```text
P1.1 Deterministic order identity
```

Then continue Phase 1 in dependency order. Do not begin dynamic leverage, cycle-exit research or bear-short work before account/execution truth is closed.

## Fresh-chat resume instructions

A fresh conversation should read the canonical files, inspect the latest merged PR after #39, verify actual GitHub state and CI, then:

- if the Phase 0 PR is still open or failing, close/fix it first;
- if Phase 0 is merged and green, begin P1.1 Deterministic order identity;
- do not ask the user to repeat product decisions already captured in `config/product.json`, the master plan or this handoff.
