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
- P1.1 handoff normalization PR: #43 merged; main commit `83ef2b44616269213f371ddbd2c0d352749c1c50`
- P1.2 implementation PR: #44 open on `p1-2/persistent-order-ledger`

## Current roadmap position

```text
PLANNING BASELINE: complete
CONTEXT-HANDOFF GOVERNANCE: complete
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: IMPLEMENTATION VERIFIED ON CANDIDATE — final-head CI/merge gate still required
P1.3 Partial-fill state machine: BLOCKED ON P1.2
P1+: continue in dependency order only
```

P1.2 must not be promoted to `PASS / MERGED` until PR #44 final-head CI is green and #44 is merged.

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

## Phase 0 and P1.1 established

Phase 0 established the canonical machine-readable product config and decision registry, including an empty `production_authorized_components` set. P1.1 established deterministic Hyperliquid CLOID identity from strategy release, canonical UTC decision timestamp, asset, side, route-independent economic intent and executable target revision. Replay/restart queries exchange `orderStatus` by CLOID and suppresses a known order.

P1.1 deliberately did not claim persistent local order truth, partial-fill lifecycle, retry semantics or distributed locking.

## P1.2 implementation candidate

PR #44 implements a SQLite-backed execution ledger for the current single-account executor:

- CLOID is the primary local/exchange correlation key and database primary key;
- strategy release, canonical decision timestamp, asset, side, route-independent economic intent, target revision, route label, submitted quantity and submitted SDK parameters are persisted;
- `intent_recorded` commits before the pre-submit exchange lookup;
- a separate durable `submission_attempt_recorded` marker commits before the order network submit call;
- submission response, OID when available, response timestamp and rejection reason are persisted;
- status history and raw exchange observations provide structured audit evidence;
- fill events are deduplicated by Hyperliquid trade ID and persist OID, timestamp, price, quantity, fee, fee token and raw payload;
- ledger aggregates fill quantity, weighted average fill price, fees and remaining quantity;
- unresolved orders survive process restart and reconstruct from Hyperliquid `orderStatus` plus `userFillsByTime`;
- exchange truth wins over conflicting local observations while conflict history is retained;
- an exchange `filled` state without complete fill evidence remains unresolved and fails closed;
- `unknownOid` after a durable submission-attempt marker remains uncertain and is never blindly resubmitted;
- a recovered exchange order with an OID blocks new economic risk even if the current local ledger never recorded its original submission attempt;
- malformed/failed order-status and fill reconciliation paths leave structured `reconciliation_uncertain` audit events before failing closed;
- unknown exchange status values fail closed rather than being silently treated as known lifecycle states;
- SQLite initialization runs `quick_check`; database/read failures fail closed;
- a fill response at the documented API limit is treated as potentially truncated and fails closed rather than claiming complete truth;
- trade mode requires an explicitly configured persistent ledger path and `ORDER_LEDGER_DURABLE_STORAGE=true`;
- the current local SQLite backend rejects Vercel trade mode; Docker declares `/data` as the intended mount point, but the operator must actually provide persistent storage;
- service trade runs reconcile unresolved state before a new order and reconcile again after submission; unresolved attempted/recovered exchange orders block a new rebalance until terminal exchange truth is recovered.

`EXEC-ORDER-LEDGER-P1.2` is registered as `IMPLEMENTATION_VERIFIED` in `config/decision_registry.json`. `production_authorized_components` remains empty.

## P1.2 evidence and review corrections

Tests cover:

- SQLite persistence across reopen/restart;
- CLOID uniqueness and idempotent replay;
- pre-network durable intent and submission-attempt ordering;
- network timeout followed by restart without blind duplicate submission;
- known-CLOID duplicate suppression with local exchange observation;
- recovered exchange-open order blocking even without a local submission-attempt record;
- reconstruction of OID, fills, average fill price, fees, remaining quantity and terminal state;
- exchange/local status conflict audit;
- filled-with-missing-fills fail-closed behavior;
- structured audit for order-status lookup failure and malformed fill lookup;
- unknown exchange-status fail-closed behavior;
- corrupt database fail-closed behavior;
- API fill-limit truncation guard;
- durable-storage and Vercel runtime configuration gates.

Candidate head `40dff282eb89fcf6f2459c029b4a1f681f7c96c8` passed both `Phase 0 baseline contract` and `PR handoff governance`; the Phase 0 job included successful execution pytest and research integration steps. The decision-registry/current-state commits after that evidence require a new final-head CI run before merge.

Self-review corrections made inside PR #44:

1. uncertainty/conflict audit records were initially vulnerable to transaction rollback when immediately followed by an exception; the corrected paths persist audit/state before raising;
2. a recovered exchange-open order could initially remain non-blocking when the new local ledger had no historical submission-attempt marker; blocking now includes either a durable local attempt or discovered exchange OID;
3. malformed order/fill reconciliation and unknown exchange status paths now leave structured uncertainty audit evidence before failing closed.

These are implementation/safety corrections only and do not change product assumptions.

## P1.2 boundaries not solved

P1.2 does **not** claim:

- the complete P1.3 partial-fill state machine or retry policy;
- simultaneous multi-process race elimination or distributed locking;
- order slicing;
- fresh position/fill verification between reversal close/open legs;
- P1.4 reversal safety;
- cancel/retry lifecycle hardening beyond persisted truth and fail-closed uncertainty;
- multi-asset execution readiness;
- production readiness.

The existing reversal route remains observable as `close_for_reversal` / `open_reversal` while deterministic identity remains route-independent `reduce` / `increase`.

## Research boundaries that remain closed unless formally reopened

- Do not rescue stopped carry work.
- Do not rescue rejected TSMOM or historical alpha lines by parameter/window/asset retuning.
- Do not treat historical ASYM-BETA extra sleeve as approved leverage expansion.
- Do not infer spot identity from PnL.
- ETH/SOL/BNB execution support is not production-ready merely because those assets are in the product universe.

## Current evidence status

- BRRK-0011 remains the frozen directional research target.
- Hyperliquid all-perp implementation remains rejected as the default relative to spot-aware routing evidence on the tested window.
- BTC spot/UBTC identity has public verification; other instrument identity work remains separately gated.
- Phase 0 and P1.1 are merged and green.
- P1.2 implementation is verified on the PR #44 candidate, but final-head CI and merge evidence are still required before `PASS / MERGED`.
- Execution production readiness is not established.
- Dynamic leverage expansion is not production-authorized.
- Cycle-top/exit model is not validated.
- Bear-market Top-20 expansion remains research-only and deferred.

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

## Open blockers / uncertainties

1. P1.2 still requires PR #44 final-head CI and merge before it can PASS.
2. P1.3 partial-fill state transitions and retry policy remain unimplemented.
3. Cross-process simultaneous submission races/distributed locking remain unimplemented.
4. Existing reversal close/open lifecycle is not declared safe by P1.2.
5. SQLite durability depends on the deployment actually mounting persistent storage; Vercel trade mode is rejected by the current backend.
6. `userFillsByTime` pagination beyond the guarded response limit is not implemented; reaching the limit blocks rather than claiming complete truth.
7. Current BTC quantity precision remains hardcoded at five decimals; instrument-specific precision belongs to later router work.
8. Production authorization remains empty.

## Latest project-drift assessment

```text
DRIFT_0
```

Reason: P1.2 implements the next roadmap dependency without changing BRRK economics, objective, product universe, Hyperliquid-first venue, leverage philosophy, 70% catastrophic-only boundary, human approval rules, ACTIVE/CANDIDATE separation, credential boundary, stopped research lines or production authorization. Rejecting trade mode without durable storage is an execution-safety requirement of P1.2, not a product-scope change.

## Exact next action

```text
Run PR #44 final-head CI -> merge #44 -> normalize post-merge handoff if stale wording remains.
```

Do not begin P1.3 until P1.2 is actually `PASS / MERGED`.

## Fresh-chat resume instructions

A fresh conversation should read the canonical files, verify actual GitHub/CI state, confirm PR #43/main baseline, then inspect PR #44. If #44 is not merged or its final head is not green, finish P1.2 first. Only after P1.2 is merged and handoff text is normalized may the exact next task become P1.3.

Do not ask the user to repeat product decisions already captured in GitHub.
