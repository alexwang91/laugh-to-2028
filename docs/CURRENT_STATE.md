# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- Master plan: `docs/MASTER_PLAN_2026-08-05.md`
- Roadmap: `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`
- Governance: `docs/PROJECT_GOVERNANCE_2026-08-05.md`
- Continuity protocol: `docs/CONTEXT_CONTINUITY_PROTOCOL.md`
- P1.1 implementation PR #42 + handoff #43: PASS / MERGED
- P1.2 implementation PR #44 + handoff #45: PASS / MERGED
- P1.3 implementation PR #46 + handoff #47: PASS / MERGED
- P1.4 implementation PR #48 + handoff #49: PASS / MERGED
- P1.5 implementation PR #50 merged; squash/main commit `f23aa681e04ba0fdb37ff413270380e60036e9af`
- P1.5 final implementation head: `f62eb4edcf22aa47dccd521f119ddff688cbe289`

## Current roadmap position

```text
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: PASS / MERGED
P1.3 Partial-fill correctness: PASS / MERGED
P1.4 Reversal safety: PASS / MERGED
P1.5 Precision / metadata: PASS / MERGED
P1.6 Post-submit reconciliation: NEXT
P1.7+ blocked until dependency order is satisfied
```

The unique next implementation task is **P1.6 Post-submit reconciliation**. Do not start P1.7, P1.8, P2, P3, P4 or P5 before P1.6 closes its evidence/merge gate.

## Frozen product state

- Long universe: BTC / ETH / SOL / BNB.
- Initial managed capital: $2,000 cash/stablecoin.
- Recurring manual contribution: about $100/week.
- Primary venue: Hyperliquid.
- Official daily boundary: 00:00 UTC.
- Daily strategy decisions; intraday automation may only reduce risk.
- Leverage is model-determined; 70% drawdown is catastrophic tolerance only.
- FLAT = zero directional exposure; re-entry and first short activation require human approval.
- Bot uses trading Agent/API credentials only; no master wallet private key, automated withdrawals or external transfers.
- Strategy upgrades use candidate/shadow + manual blue-green cutover.
- BTC-only executor capability does not redefine the four-asset product universe.

## P1.1–P1.4 closure baseline

Registered engineering decisions retained:

- `EXEC-ORDER-ID-P1.1 = IMPLEMENTATION_VERIFIED`
- `EXEC-ORDER-LEDGER-P1.2 = IMPLEMENTATION_VERIFIED`
- `EXEC-PARTIAL-FILL-P1.3 = IMPLEMENTATION_VERIFIED`
- `EXEC-REVERSAL-SAFETY-P1.4 = IMPLEMENTATION_VERIFIED`

## P1.5 PASS / MERGED

PR #50 established metadata-driven formatting:

- Hyperliquid perp `meta.universe` supplies each asset's `szDecimals`;
- executor fetches metadata before economic write actions;
- order sizes use metadata-driven Decimal/ROUND_DOWN formatting instead of a global 5-decimal helper;
- ledger parameters record `sz_decimals` and `precision_source=hyperliquid_meta`;
- metadata-derived price formatting enforces decimal/significant-figure constraints with integer-price allowance;
- BTC, ETH, SOL and BNB each pass independent formatting tests;
- malformed, duplicate, incomplete metadata and quantities that round to zero fail closed;
- formatting verification does not imply multi-asset production execution or P2 routing.

`EXEC-PRECISION-METADATA-P1.5 = IMPLEMENTATION_VERIFIED` is registered. Production authorization remains empty.

Final evidence on `f62eb4edcf22aa47dccd521f119ddff688cbe289`:

- Phase 0 baseline contract run #36 / Actions `31079063482`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- PR handoff governance run #46 / Actions `31079063679`: SUCCESS;
- evidence-only governance run #47 / Actions `31079123985`: SUCCESS.

PR #50 squash-merged to main as `f23aa681e04ba0fdb37ff413270380e60036e9af`.

## Current unique next task: P1.6 Post-submit reconciliation

Roadmap requirement: after every trading cycle fetch open orders, fills, positions, and account equity/margin; compare with local ledger and target.

Acceptance criteria:

- unexplained differences block further risk-increasing orders;
- reduce-risk actions remain available.

P1.6 must consume P1.2 durable ledger truth, P1.3 actual-fill transitions, P1.4 reversal safety, and P1.5 metadata formatting. It must not silently escalate into P1.7 restart-matrix or P1.8 emergency-path work.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Latest project-drift assessment

```text
DRIFT_0
```

## Exact next action

```text
P1.6 Post-submit reconciliation
```

Start from current main after this normalization merges, using a fresh candidate branch.