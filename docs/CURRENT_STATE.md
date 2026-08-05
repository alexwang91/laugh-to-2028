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
- P1.1 implementation PR: #42 merged; squash commit `937db648b4ddaf8322c7bd9ce9b03f39321e2508`
- P1.1 handoff normalization PR: #43 merged; main commit `83ef2b44616269213f371ddbd2c0d352749c1c50`
- P1.2 implementation PR: #44 merged; squash/main commit `a4e1ebc98039ffee7e53f2acd7c38feaebbb2769`
- P1.2 final implementation head before merge: `62fab73baef86970954afe55831305f4328dee20`

## Current roadmap position

```text
PLANNING BASELINE: complete
CONTEXT-HANDOFF GOVERNANCE: complete
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: PASS / MERGED
P1.3 Partial-fill correctness: NEXT
P1.4+ blocked until dependency order is satisfied
```

The unique next implementation task is **P1.3 Partial-fill correctness**. Do not start P1.4, P2, P4, P5 or P8 before P1.3 closes its own evidence/merge gate.

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

## P1.1 established

P1.1 established deterministic Hyperliquid CLOID identity from:

- strategy release;
- canonical UTC decision timestamp;
- asset;
- side;
- route-independent economic intent;
- executable target revision.

Sequential replay/restart reconstructs the same CLOID, queries Hyperliquid `orderStatus`, and suppresses a known economic order. Reversal route labels remain observable as `close_for_reversal` / `open_reversal` while economic identity remains `reduce` / `increase`.

## P1.2 PASS / MERGED

PR #44 established persistent execution truth for the current single-account executor using SQLite on explicitly durable storage:

- CLOID is the local/exchange correlation key and database primary key;
- strategy release, canonical decision timestamp, asset, side, economic intent, target revision, route label, submitted quantity and submitted order parameters are persisted;
- `intent_recorded` commits before any economic-order network submission;
- a durable `submission_attempt_recorded` marker commits before the submit network call;
- submission response, OID when available, timestamps and rejection information are persisted;
- structured status history and raw exchange observations preserve audit evidence;
- fill events are deduplicated by Hyperliquid trade ID and persist OID, timestamp, price, quantity, fee, fee token and raw payload;
- fill quantity, weighted average fill price, fees and remaining quantity are reconstructed and persisted;
- unresolved orders survive restart and are reconciled from Hyperliquid `orderStatus` plus `userFillsByTime`;
- exchange facts supersede conflicting local observations while conflicts remain auditable;
- Hyperliquid's documented active, cancellation and rejection status taxonomy is classified explicitly and exact cancel/reject reasons are retained;
- exchange `origSz`, remaining `sz` and reconstructed fills are cross-checked; inconsistent or incomplete fill truth remains unresolved and fails closed;
- `unknownOid` after a durable submission attempt never triggers blind resubmission;
- a recovered exchange order with an OID blocks new risk even when the new local ledger lacks the historical submission-attempt marker;
- malformed/failed reconciliation and undocumented exchange states persist `reconciliation_uncertain` evidence before failing closed;
- a fill response at the guarded API result limit is treated as potentially incomplete and fails closed;
- SQLite initialization performs an integrity check; database/read failures fail closed;
- trade mode requires explicit `ORDER_LEDGER_PATH` plus `ORDER_LEDGER_DURABLE_STORAGE=true`;
- the current local SQLite backend rejects Vercel trade mode; Docker declares `/data` as the intended mount point, but infrastructure must actually provide persistent storage;
- each trade cycle reconciles unresolved truth before new submission and again after submission.

`EXEC-ORDER-LEDGER-P1.2` is registered as `IMPLEMENTATION_VERIFIED` in `config/decision_registry.json`. `production_authorized_components` remains empty.

## P1.2 evidence

Exact final implementation head `62fab73baef86970954afe55831305f4328dee20` passed:

- `Phase 0 baseline contract` run #22 / Actions run `31053496487`: SUCCESS;
- execution pytest step inside that run: SUCCESS;
- research integration contract step inside that run: SUCCESS;
- `PR handoff governance` run #27 / `31053496526`: SUCCESS;
- `PR handoff governance` run #28 / `31053541154`: SUCCESS.

PR #44 then squash-merged to main as `a4e1ebc98039ffee7e53f2acd7c38feaebbb2769`.

Self-review corrections completed inside PR #44:

1. persisted uncertainty/conflict audit events before raising so exception rollback cannot erase forensic evidence;
2. made recovered exchange orders blocking even without a historical local submission-attempt marker;
3. added structured audit persistence for malformed/failed order/fill reconciliation and undocumented exchange states;
4. expanded lifecycle classification to the documented Hyperliquid cancel/reject taxonomy and retained exact reason codes;
5. prevented false completion of partially-filled-then-canceled orders by cross-checking `origSz`, remaining `sz` and reconstructed fills.

These corrections changed implementation safety only. They did not change product economics or authorization.

## P1.2 boundaries deliberately not solved

P1.2 does **not** claim:

- P1.3 partial-fill transition/retry correctness;
- safe continuation or resizing after a partial fill;
- simultaneous multi-process race elimination or distributed locking;
- order slicing;
- fresh position/fill verification between reversal close/open legs;
- P1.4 reversal safety;
- full post-submit account/position reconciliation of P1.6;
- production readiness;
- multi-asset production execution.

P1.2 can persist and reconstruct partial-fill facts. It does not yet use those facts to drive a correct partial-fill execution lifecycle. That distinction is the P1.3 boundary.

## Current unique next task: P1.3 Partial-fill correctness

Roadmap requirement:

> Implement position transition from actual fills, not requested notional.

Acceptance criteria:

- 0%, partial and full fill cases all reconcile correctly;
- resting remainder is visible;
- target versus actual exposure is continuously calculable.

P1.3 has **not** been implemented yet. Its development must begin from current main on a fresh candidate branch and follow the normal implementation/test/self-review/PR/final-head-CI/merge loop.

## Research boundaries that remain closed unless formally reopened

- Do not rescue stopped carry work.
- Do not rescue rejected TSMOM or historical alpha lines by parameter/window/asset retuning.
- Do not treat historical ASYM-BETA extra sleeve as approved leverage expansion.
- Do not infer spot identity from PnL.
- ETH/SOL/BNB execution support is not production-ready merely because those assets are in the product universe.

## Production authorization

```text
Strategy economics change from P1.2: NONE
New live capital authorization: NONE
Leverage expansion authorization: NONE
New asset execution authorization: NONE
Short authorization: NONE
Cycle-exit production authorization: NONE
Strategy cutover authorization: NONE
Production-authorized component set: EMPTY
```

P1.2 engineering verification does not authorize live deployment or increase risk.

## Open blockers / uncertainties

1. P1.3 actual-fill-driven position transition remains unimplemented.
2. Cross-process simultaneous submission races/distributed locking remain unimplemented.
3. Order slicing remains unimplemented.
4. Existing reversal close/open lifecycle is not declared safe by P1.2.
5. SQLite durability depends on the deployment actually mounting persistent storage; Vercel trade mode remains rejected by the current backend.
6. `userFillsByTime` pagination beyond the guarded response limit is not implemented; reaching the limit blocks rather than claiming complete truth.
7. Current BTC quantity precision remains hardcoded at five decimals; instrument-specific precision belongs to later router/metadata work.
8. Production authorization remains empty.

## Latest project-drift assessment

```text
DRIFT_0
```

Reason: P1.2 followed roadmap dependency order and changed no BRRK objective, strategy economics, product universe, Hyperliquid-first venue, leverage philosophy, 70% catastrophic-only boundary, human approval rule, ACTIVE/CANDIDATE separation, credential boundary, stopped research line or production authorization.

## Exact next action

```text
P1.3 Partial-fill correctness
```

Start only from current main after verifying this handoff normalization is merged. Implement position transition from actual fills, with explicit 0% / partial / full fill reconciliation, visible resting remainder, and continuously calculable target-versus-actual exposure.

## Fresh-chat resume instructions

A fresh conversation should:

1. read the canonical files in the repository-defined order;
2. verify actual main, latest merged PR, open PR/issues and final CI rather than trusting handoff prose alone;
3. confirm P1.2 / PR #44 is merged and `EXEC-ORDER-LEDGER-P1.2` is registered;
4. confirm production authorization is still empty;
5. if this post-merge normalization is present on main, start only P1.3 from a fresh branch.

Do not ask the user to repeat product decisions already captured in GitHub.
