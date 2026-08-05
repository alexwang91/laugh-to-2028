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
- P1.3 implementation PR: #46 open
- P1.3 candidate branch: `p1-3/partial-fill-correctness`

## Current roadmap position

```text
PLANNING BASELINE: complete
CONTEXT-HANDOFF GOVERNANCE: complete
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: PASS / MERGED
P1.3 Partial-fill correctness: IMPLEMENTATION VERIFIED / FINAL-HEAD CI PENDING / NOT MERGED
P1.4+ blocked until P1.3 closes its final evidence/merge gate
```

The only active implementation task is **P1.3 Partial-fill correctness**. Do not start P1.4, P2, P4, P5 or P8 while PR #46 remains unmerged.

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

## P1.3 implementation verified on candidate code head

PR #46 adds an actual-fill-driven transition layer on top of P1.2 truth without changing strategy economics:

- every new same-direction order persists the exchange-observed pre-trade position baseline and intended target position in the already-durable submitted-order parameters;
- fill state is classified from reconciled actual fill quantity as `zero_fill`, `partial_fill` or `full_fill`;
- signed position delta is derived from actual fills and order side, never from requested notional;
- `actual_position_qty_from_fills = position_before_qty + signed_fill_quantity`;
- `target_gap_qty = target_position_qty - actual_position_qty_from_fills` remains explicitly visible while the baseline is trustworthy;
- `exchange_remaining_quantity`, `unfilled_quantity` and `resting_remaining_quantity` are separately exposed so a live resting remainder is not confused with a canceled unfilled remainder;
- exchange remaining quantity must agree with local `submitted_quantity - actual_fill_quantity`; disagreement fails closed instead of declaring progress complete;
- reconciliation returns structured `fill_transitions` for orders touched by the cycle;
- transition-construction failures are persisted as `fill_transition_failed` reconciliation uncertainty and block new risk;
- legacy P1.2 rows without a stored position baseline retain fill truth but report `position_tracking_status=baseline_unavailable` rather than inventing target-versus-actual exposure;
- for a reversal close leg, the known pre-trade baseline can be tracked toward zero;
- for the reversal open leg, P1.3 deliberately persists `position_before_qty=null` and reports the baseline unavailable, because only P1.4 may establish safe fresh state between reversal legs.

Candidate unit coverage includes 0% fill, partial fill, full fill, sell-side signed transitions, canceled versus resting remainder, reversal baseline unavailability, overfill rejection and remaining-quantity mismatch rejection.

`EXEC-PARTIAL-FILL-P1.3` is now registered as `IMPLEMENTATION_VERIFIED` in `config/decision_registry.json`, based on the green candidate code head evidence below. This does **not** authorize production and does **not** mark P1.3 merged.

## P1.3 evidence so far

Candidate code/docs head before registry finalization:

```text
c75cd51ba2d73a6b629fb7402e6948326756c0af
```

That head passed:

- `Phase 0 baseline contract` run #24 / Actions run `31055367127`: SUCCESS;
- execution tests step: SUCCESS;
- research integration contract step: SUCCESS;
- corrected `PR handoff governance` run #32 / Actions run `31055420052`: SUCCESS.

The first governance run #31 failed only because the PR body used `## Risks / unresolved` instead of the exact mandatory heading `## Risks and unresolved items`. The PR body was corrected without changing implementation code; governance run #32 then passed.

Pre-PR self-review also identified and corrected one implementation issue before the PR opened: exchange remaining quantity must equal local submitted-minus-actual-fill truth, otherwise a local/exchange size mismatch could be misclassified as valid progress.

The current branch now also contains the decision-registry and handoff updates. **Final-head CI is still required before merge.**

## P1.3 boundaries deliberately not solved

P1.3 does **not** claim:

- safe reversal continuation or a fresh account-state read between reversal legs (P1.4);
- metadata-driven size/price precision (P1.5);
- full open-orders/fills/positions/equity/margin post-submit account reconciliation (P1.6);
- the complete restart-recovery matrix (P1.7);
- kill/emergency paths (P1.8);
- simultaneous multi-process race elimination or distributed locking;
- order slicing;
- production readiness;
- multi-asset production execution.

## P1.2 evidence retained

Exact final P1.2 implementation head `62fab73baef86970954afe55831305f4328dee20` passed:

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

## Research boundaries that remain closed unless formally reopened

- Do not rescue stopped carry work.
- Do not rescue rejected TSMOM or historical alpha lines by parameter/window/asset retuning.
- Do not treat historical ASYM-BETA extra sleeve as approved leverage expansion.
- Do not infer spot identity from PnL.
- ETH/SOL/BNB execution support is not production-ready merely because those assets are in the product universe.

## Production authorization

```text
Strategy economics change from P1.3: NONE
New live capital authorization: NONE
Leverage expansion authorization: NONE
New asset execution authorization: NONE
Short authorization: NONE
Cycle-exit production authorization: NONE
Strategy cutover authorization: NONE
Production-authorized component set: EMPTY
```

P1.3 engineering verification does not authorize live deployment or increase risk.

## Open blockers / uncertainties

1. P1.3 final-head CI and merge are still outstanding.
2. P1.4 fresh-state reversal safety remains unimplemented; the P1.3 reversal-open transition therefore reports its position baseline unavailable.
3. Cross-process simultaneous submission races/distributed locking remain unimplemented.
4. Order slicing remains unimplemented.
5. SQLite durability depends on the deployment actually mounting persistent storage; Vercel trade mode remains rejected by the current backend.
6. `userFillsByTime` pagination beyond the guarded response limit is not implemented; reaching the limit blocks rather than claiming complete truth.
7. Current BTC quantity precision remains hardcoded at five decimals; instrument-specific precision belongs to later router/metadata work.
8. Production authorization remains empty.

## Latest project-drift assessment

```text
DRIFT_0
```

Reason: P1.3 is the exact roadmap dependency and implements actual-fill position progress on top of P1.2. It changes no BRRK objective, strategy economics, product universe, Hyperliquid-first venue, leverage philosophy, 70% catastrophic-only boundary, human approval rule, ACTIVE/CANDIDATE separation, credential boundary, stopped research line or production authorization. P1.4 behavior is explicitly not claimed.

## Exact next action

```text
P1.3 final-head CI -> merge PR #46 -> normalize post-merge handoff to P1.4
```

Do not begin P1.4 until PR #46 is merged and its handoff is normalized.

## Fresh-chat resume instructions

A fresh conversation should:

1. read the canonical files in the repository-defined order;
2. verify actual main, PR #46 head, open PR/issues and final-head CI rather than trusting handoff prose alone;
3. confirm P1.2 / PR #44 and normalization PR #45 are merged;
4. confirm `EXEC-PARTIAL-FILL-P1.3` is registered but production authorization remains empty;
5. if PR #46 is still open, continue only its final-head CI/fix/merge loop;
6. start P1.4 only after P1.3 is PASS / MERGED and the post-merge handoff is normalized.

Do not ask the user to repeat product decisions already captured in GitHub.
