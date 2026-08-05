# BRRK Current State

Last updated: 2026-08-05
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- Master plan: `docs/MASTER_PLAN_2026-08-05.md`
- Roadmap: `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
- Governance: `docs/PROJECT_GOVERNANCE_2026-08-05.md`
- Continuity protocol: `docs/CONTEXT_CONTINUITY_PROTOCOL.md`
- Last merged planning PR: #38
- Continuity bootstrap commit: `7abf1260e979061960b8eda27457905473f27d4f`

## Current roadmap position

```text
PLANNING BASELINE: complete
P0.1 Canonical product config: NEXT
P0.2 Decision registry: NEXT / may be implemented in the same Phase-0 PR if acceptance gates remain clear
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

## Production authorization

```text
Strategy change from planning/continuity work: NONE
New live capital authorization: NONE
Leverage expansion authorization: NONE
Short authorization: NONE
```

## Open blockers / uncertainties

1. Phase 0 canonical machine-readable config does not yet exist.
2. Phase 0 decision registry does not yet exist.
3. Execution account/order/fill truth is not yet hardened.
4. Operating drawdown budget is intentionally not frozen until leverage research.
5. Cycle-exit signal parameters/timeframes are intentionally not frozen until historical/walk-forward study.

## Latest project-drift assessment

```text
DRIFT_1
```

Reason: the initial `CONTEXT_CONTINUITY_PROTOCOL.md` bootstrap file was committed directly to `main` before the PR guard/template branch existed. This is a process-only deviation. It changed no product, research, risk, credential or production behavior. All subsequent material work must follow candidate branch + PR + handoff protocol.

## Exact next unblocked task

Implement Phase 0:

```text
P0.1 Canonical product config
P0.2 Decision registry
```

Acceptance gates are defined in `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`.

Do not begin P1 until Phase 0 has a closed PR with tests/evidence and this file is updated.

## Fresh-chat resume instructions

A fresh conversation should read the canonical files listed above, inspect the latest merged PR after #38, verify actual GitHub state, then continue P0.1/P0.2. Do not ask the user to repeat strategy decisions already captured here or in the master plan.
