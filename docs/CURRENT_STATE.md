# BRRK Current State

Last updated: 2026-08-06
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
- P1.1 implementation PR: #42 merged; squash commit `937db648b4ddaf8322c7bd9ce9b03f39321e2508`
- P1.1 handoff normalization PR: #43 merged; main commit `83ef2b44616269213f371ddbd2c0d352749c1c50`
- P1.2 implementation PR: #44 merged; squash/main commit `a4e1ebc98039ffee7e53f2acd7c38feaebbb2769`
- P1.2 handoff normalization PR: #45 merged; main commit `0a461cb541e85c5287177a0c46ae9905d9fede25`
- P1.3 implementation PR: #46 merged; squash/main commit `fe663a0e8115baaa5c2ae9f1a59338e8f4a0c868`
- P1.3 handoff normalization PR: #47 merged; main commit `19445de8fc689ea4f5f7d7e123934fbac2751f83`
- P1.4 implementation PR: #48 merged; squash/main commit `7acb093af59825c39fd092f232573666682197d8`
- P1.4 final implementation head before merge: `879ce2da3b1e4382473037650c3fca30cda7f63f`

## Current roadmap position

```text
PLANNING BASELINE: complete
CONTEXT-HANDOFF GOVERNANCE: complete
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: PASS / MERGED
P1.3 Partial-fill correctness: PASS / MERGED
P1.4 Reversal safety: PASS / MERGED
P1.5 Precision / metadata: NEXT
P1.6+ blocked until dependency order is satisfied
```

The unique next implementation task is **P1.5 Precision / metadata**. Do not start P1.6, P2, P3, P4, P5 or P8 before P1.5 closes its own evidence/merge gate.

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
- FLAT = zero directional exposure.
- Re-entry from FLAT and first short activation in a new bear phase require human approval.
- Bot may use a trading Agent/API credential only; never the master wallet private key and never automated withdrawals or external transfers.
- Strategy upgrades use candidate/shadow plus manual blue-green cutover; no hot strategy patching.
- Current BTC-only executor capability does not redefine the BTC/ETH/SOL/BNB product universe.

## P1.1–P1.3 retained baseline

P1.1 established deterministic economic order identity. P1.2 established durable local/exchange order, fill and restart truth. P1.3 made position progress actual-fill-driven with explicit zero/partial/full fill states, resting remainder visibility and target-gap calculation when baseline truth exists.

Registered decisions retained:

- `EXEC-ORDER-ID-P1.1 = IMPLEMENTATION_VERIFIED`
- `EXEC-ORDER-LEDGER-P1.2 = IMPLEMENTATION_VERIFIED`
- `EXEC-PARTIAL-FILL-P1.3 = IMPLEMENTATION_VERIFIED`

## P1.4 PASS / MERGED

PR #48 established reversal safety:

- old-direction reduction and new-direction opening are distinct `reduce` and `increase` economic intents;
- reversal close uses `market_close` with explicit reduce-only semantics;
- after the close leg, executor fetches a fresh Hyperliquid `clearinghouseState` account position;
- the new-direction open leg is not constructed or submitted until that fresh account position proves the old direction is flat;
- partial old-direction remainder blocks the new-direction open leg;
- unexpected cross-through into the opposite sign blocks the new-direction open leg rather than compounding risk;
- malformed account-position state and failed state reads fail closed;
- a verified-flat open leg persists `position_before_qty=0`, `reversal_flat_verified=true`, and source `fresh_exchange_flat_after_reversal_close`.

Self-review correction: close submission status is not sufficient evidence of a flat account position, so the second leg is gated by fresh account-level position truth.

`EXEC-REVERSAL-SAFETY-P1.4` is registered as `IMPLEMENTATION_VERIFIED`. This is engineering verification only; production authorization remains empty.

## P1.4 final evidence

Exact final implementation head:

```text
879ce2da3b1e4382473037650c3fca30cda7f63f
```

Final-head evidence:

- `Phase 0 baseline contract` run #32 / Actions run `31078243843`: SUCCESS;
- execution tests: SUCCESS;
- research integration contract: SUCCESS;
- `PR handoff governance` run #41 / Actions run `31078243847`: SUCCESS;
- evidence-only PR-body governance run #42 / Actions run `31078303601`: SUCCESS.

Earlier governance run #38 failed only because the forward PR had not directly modified `docs/CURRENT_STATE.md`; that governance defect was corrected on the same PR and later governance runs passed.

PR #48 squash-merged to main as:

```text
7acb093af59825c39fd092f232573666682197d8
```

## P1.4 boundaries deliberately not solved

P1.4 does **not** claim:

- P1.5 metadata-driven size/price precision;
- P1.6 full open-order/fill/position/equity/margin post-submit reconciliation;
- P1.7 complete restart-recovery matrix;
- P1.8 kill/emergency paths;
- simultaneous multi-process race elimination or distributed locking;
- order slicing;
- P2 router capability;
- P3 production-quality daily target engine;
- P4 leverage research completion;
- P5 cycle-top research completion;
- production readiness;
- multi-asset production execution.

## Current unique next task: P1.5 Precision / metadata

Roadmap requirement:

> Remove hardcoded size and price precision.

Acceptance criteria:

- asset metadata drives valid order formatting;
- all BRRK instruments pass formatting tests.

P1.5 must remove the current hardcoded BTC quantity precision and introduce metadata-driven formatting without claiming P2 routing or production-ready multi-asset execution.

## Research boundaries that remain closed unless formally reopened

- Do not rescue stopped carry work.
- Do not rescue rejected TSMOM or historical alpha lines by parameter/window/asset retuning.
- Do not treat historical ASYM-BETA extra sleeve as approved leverage expansion.
- Do not infer spot identity from PnL.
- ETH/SOL/BNB execution support is not production-ready merely because those assets are in the product universe.

## Production authorization

```text
Strategy economics change from P1.4: NONE
New live capital authorization: NONE
Leverage expansion authorization: NONE
New asset execution authorization: NONE
Short authorization: NONE
Cycle-exit production authorization: NONE
Strategy cutover authorization: NONE
Production-authorized component set: EMPTY
```

P1.4 engineering verification does not authorize live deployment or increase risk.

## Open blockers / uncertainties

1. P1.5 metadata-driven precision remains unimplemented.
2. P1.6 full post-submit account reconciliation remains unimplemented.
3. P1.7 complete restart recovery remains unimplemented.
4. P1.8 kill/emergency paths remain unimplemented.
5. Cross-process simultaneous submission races/distributed locking remain unimplemented.
6. Order slicing remains unimplemented.
7. SQLite durability still depends on real persistent deployment storage; Vercel trade mode remains rejected by the current backend.
8. `userFillsByTime` pagination beyond the guarded response limit remains a fail-closed blocker.
9. Production authorization remains empty.

## Latest project-drift assessment

```text
DRIFT_0
```

Reason: P1.4 followed the roadmap dependency order and changed no BRRK objective, strategy economics, product universe, Hyperliquid-first venue, leverage philosophy, 70% catastrophic-only boundary, human approval rule, ACTIVE/CANDIDATE separation, credential boundary, stopped research line or production authorization.

## Exact next action

```text
P1.5 Precision / metadata
```

Start only from current main after this post-merge normalization is merged. Keep P1.6+ blocked until P1.5 passes its implementation/test/review/PR/final-head-CI/merge gate.

## Fresh-chat resume instructions

A fresh conversation should:

1. read the canonical files in repository-defined order;
2. verify actual main, latest merged PR, open PR/issues and final CI rather than trusting handoff prose alone;
3. confirm P1.4 / PR #48 is merged and `EXEC-REVERSAL-SAFETY-P1.4` is registered;
4. confirm production authorization remains empty;
5. if this post-merge normalization is present on main, start only P1.5 from a fresh candidate branch.

Do not ask the user to repeat product decisions already captured in GitHub.