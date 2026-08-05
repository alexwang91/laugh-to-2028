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
- Phase 0 PR: #40 merged; squash commit `1feffd07208a741e53766fe126dc9cb7add3d3d1`; final-head governance and Phase-0 baseline CI both passed
- Phase 0 handoff normalization PR: #41 merged

## Current roadmap position

```text
PLANNING BASELINE: complete
CONTEXT-HANDOFF GOVERNANCE: complete
P0.1 Canonical product config: PASS
P0.2 Decision registry: PASS
P1.1 Deterministic order identity: CANDIDATE / CI REQUIRED
P1.2 Persistent order ledger: BLOCKED ON P1.1
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

## P1.1 candidate implementation

The current candidate branch implements deterministic exchange-visible order identity:

- canonical daily decision timestamp is the UTC boundary immediately after the last completed daily candle;
- order identity inputs are release ID, decision timestamp, asset, side, intent and target revision;
- target revision is based on executable target-position precision rather than current-position delta;
- canonical inputs are hashed to a 128-bit Hyperliquid cloid;
- `market_open` and `market_close` receive that cloid;
- before submission the bot queries Hyperliquid `orderStatus` by cloid;
- an already-known cloid is returned as `duplicate_suppressed` instead of submitting again;
- malformed/ambiguous order-status lookup fails closed before submission;
- replay/restart and golden-vector tests are included.

P1.1 does **not** claim persistent local ledger, partial-fill lifecycle, retry-attempt policy or cross-process locking. Those remain later Phase-1 dependencies.

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
- P1.1 code exists on candidate branch but is not PASS until final-head CI and governance checks succeed.
- Execution production readiness is not established: persistent ledger, partial-fill lifecycle, reconciliation, idempotency beyond sequential replay, slicing, kill paths and executor lifecycle tests remain required.
- Dynamic leverage above the current BRRK scale is not yet production-authorized.
- Cycle-top/exit model is not yet validated; future study must include 2021 two-wave structure and 2025 multi-peak structure.
- Bear-market Top-20 short expansion is research-only and deferred.

## Production authorization

```text
Strategy change from P1.1 candidate: NONE
New live capital authorization: NONE
Leverage expansion authorization: NONE
Short authorization: NONE
```

## Open blockers / uncertainties

1. P1.1 requires green final-head CI before it can be marked PASS.
2. P1.2 persistent ledger is not yet implemented.
3. Cross-process simultaneous submission races are not claimed solved by P1.1.
4. Retry behavior after rejected/canceled/partially-filled orders is intentionally not defined until later Phase 1.
5. Operating drawdown budget is intentionally not frozen until leverage research.
6. Cycle-exit signal parameters/timeframes are intentionally not frozen until historical/walk-forward study.
7. ETH/SOL/BNB execution and spot identities are not authorized merely because they exist in the product universe.

## Latest project-drift assessment

```text
DRIFT_0
```

Reason: P1.1 candidate is pure execution hardening implementing the next roadmap dependency. It changes no strategy economics, asset universe, venue, risk philosophy, approval boundary, credential boundary or production authorization.

## Exact next unblocked task

Until candidate CI closes:

```text
P1.1 Deterministic order identity — TEST / REVIEW / CLOSE EVIDENCE
```

After P1.1 is green and merged:

```text
P1.2 Persistent order ledger
```

Do not begin P4 leverage, P5 cycle-exit research or P8 bear-short work before required earlier gates are closed.

## Fresh-chat resume instructions

A fresh conversation should read the canonical files, verify actual GitHub state and CI, inspect the latest P1.1 PR, and either close/fix P1.1 or, if it is already green and merged, begin `P1.2 Persistent order ledger`.

Do not ask the user to repeat product decisions already captured in `config/product.json`, `config/decision_registry.json`, the master plan or this handoff.
