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
- Phase 0 PR: #40 merged; squash commit `1feffd07208a741e53766fe126dc9cb7add3d3d1`
- Phase 0 handoff normalization PR: #41 merged
- P1.1 implementation PR: #42 merged; squash commit `937db648b4ddaf8322c7bd9ce9b03f39321e2508`; final-head governance, execution pytest and research integration contracts passed

## Current roadmap position

```text
PLANNING BASELINE: complete
CONTEXT-HANDOFF GOVERNANCE: complete
P0.1 Canonical product config: PASS
P0.2 Decision registry: PASS
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: NEXT
P1+: continue in dependency order only
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

## Phase 0 implementation established

P0.1:

- `config/product.json` is the canonical machine-readable product baseline;
- `execution/plan-b-bot/beta_bot/product_config.py` validates and serializes that baseline;
- execution settings consume the canonical product config before applying narrower executor capability constraints;
- product universe and current BTC-only executor capability are explicitly separated;
- research and execution contract tests consume the same canonical product file;
- `.github/workflows/phase0-baseline.yml` enforces the contract.

P0.2:

- `config/decision_registry.json` is the machine-readable frozen decision registry;
- accepted research targets, implementation-verified evidence, shadow-only lines, stopped/rejected lines and superseded work are explicit;
- the production-authorized component set is currently empty;
- future tasks must reference an existing decision or create a new registered decision rather than silently reopening stopped work.

## P1.1 implementation established

Deterministic exchange-visible order identity is implemented for the current BTC executor:

- canonical decision timestamp is the UTC boundary immediately after the last completed daily candle;
- identity inputs are strategy release ID, decision timestamp, asset, side, route-independent economic intent (`increase` / `reduce`) and executable target revision;
- target revision is target-position-centric, not current-position/delta-centric;
- target revision rounding matches the current executor order-size rounding semantics;
- canonical identity is hashed to a valid 128-bit Hyperliquid cloid;
- `market_open` and `market_close` receive that cloid;
- before submission, executor queries Hyperliquid `orderStatus` by cloid;
- an already-known cloid is returned as `duplicate_suppressed` instead of submitting again;
- malformed/ambiguous order-status lookup fails closed before submission;
- reversal route labels remain observable, but the cloid uses route-independent `reduce` / `increase` intent so a restart after the close leg reconstructs the same open-leg identity;
- golden-vector, component-difference, target-rounding, reversal-restart, sequential replay/restart, new-revision and fail-closed tests passed on PR #42 final head;
- `EXEC-ORDER-ID-P1.1` is registered as `IMPLEMENTATION_VERIFIED` in `config/decision_registry.json`.

P1.1 does **not** claim:

- persistent local order ledger;
- full partial-fill lifecycle;
- retry-attempt policy after rejected/canceled/partially-filled orders;
- cross-process/distributed locking;
- multi-asset instrument-specific quantity precision.

Those remain later dependencies.

## Research boundaries that must remain closed unless formally reopened

- Do not silently rescue stopped carry work.
- Do not rescue rejected TSMOM or historical alpha lines by parameter/window/asset retuning.
- Do not treat prior ASYM-BETA extra sleeve as an approved leverage implementation.
- Do not infer spot identity from PnL; UETH/USOL identity/custody validation remains separate.

## Current evidence status

- BRRK-0011 remains the frozen directional research target.
- Hyperliquid all-perp implementation is economically inferior to spot-aware routing on the tested window.
- BTC spot/UBTC identity has public verification; ETH/SOL spot identity remains an explicit later router validation item.
- Phase 0 is merged and green.
- P1.1 PR #42 is merged and its final head passed PR handoff governance, execution pytest and research integration contracts.
- Execution production readiness is not established: persistent ledger, partial-fill lifecycle, reconciliation, broader idempotency/coordination, slicing, kill paths and executor lifecycle tests remain required.
- Dynamic leverage above the current BRRK scale is not yet production-authorized.
- Cycle-top/exit model is not yet validated; future study must include 2021 two-wave structure and 2025 multi-peak structure.
- Bear-market Top-20 short expansion is research-only and deferred.

## Production authorization

```text
Strategy change from P1.1: NONE
New live capital authorization: NONE
Leverage expansion authorization: NONE
Short authorization: NONE
Production-authorized component set: EMPTY
```

## Open blockers / uncertainties

1. P1.2 persistent order ledger is not implemented.
2. Cross-process simultaneous submission races are not claimed solved by P1.1.
3. Retry behavior after rejected/canceled/partially-filled orders is intentionally not defined until later Phase 1.
4. Current target revision precision is tied to the BTC executor's 5-decimal size precision; instrument-specific precision belongs to later router work.
5. Operating drawdown budget is intentionally not frozen until leverage research.
6. Cycle-exit signal parameters/timeframes are intentionally not frozen until historical/walk-forward study.
7. ETH/SOL/BNB execution and spot identities are not authorized merely because they exist in the product universe.

## Latest project-drift assessment

```text
DRIFT_0
```

Reason: P1.1 implemented the exact next execution-hardening dependency. It changed no strategy economics, long/short universe, venue, risk philosophy, human approval boundary, wallet/credential boundary or production authorization. During review, reversal identity was corrected from route-label-dependent IDs to route-independent economic intents specifically to reduce restart drift rather than expand scope.

## Exact next unblocked task

```text
P1.2 Persistent order ledger
```

Required outcome from the roadmap: persist order intent, submitted order, exchange order ID, status history, fill events, fees, average fill price, remaining quantity and cancellation/rejection reason; process restart must reconstruct unresolved orders.

Do not begin P4 leverage, P5 cycle-exit research or P8 bear-short work before required earlier gates are closed.

## Fresh-chat resume instructions

A fresh conversation should read the canonical files, verify actual GitHub/CI state, confirm PR #42 is merged, then begin `P1.2 Persistent order ledger` and do not skip ahead.

Do not ask the user to repeat product decisions already captured in `config/product.json`, `config/decision_registry.json`, the master plan or this handoff.
