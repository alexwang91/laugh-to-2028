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
- P1.3 final implementation head before merge: `68bd96f86945ab0fd42ad977142fdacef6a2642d`

## Current roadmap position

```text
PLANNING BASELINE: complete
CONTEXT-HANDOFF GOVERNANCE: complete
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: PASS / MERGED
P1.3 Partial-fill correctness: PASS / MERGED
P1.4 Reversal safety: NEXT
P1.5+ blocked until dependency order is satisfied
```

The unique next implementation task is **P1.4 Reversal safety**. Do not start P1.5, P2, P4, P5 or P8 before P1.4 closes its own evidence/merge gate.

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

P1.1 established deterministic Hyperliquid CLOID identity from strategy release, canonical UTC decision timestamp, asset, side, route-independent economic intent and executable target revision. Replay/restart reconstructs the same CLOID and suppresses a known economic order.

## P1.2 PASS / MERGED

P1.2 established the persistent single-account SQLite execution ledger and restart reconciliation spine:

- durable intent before any economic-order submit;
- durable submission-attempt marker before the network call;
- CLOID/OID/status/fill/fee/average-fill/remaining/cancel-reject persistence;
- fill-event deduplication by Hyperliquid trade ID;
- restart reconstruction through `orderStatus` plus `userFillsByTime`;
- exchange-truth precedence with auditable conflicts;
- documented Hyperliquid lifecycle status classification;
- no blind retry after an uncertain durable submission attempt;
- fail-closed behavior for corrupt, malformed, incomplete or truncated truth;
- durable storage required for trade mode, with current Vercel local-SQLite trade mode rejected.

`EXEC-ORDER-LEDGER-P1.2` remains `IMPLEMENTATION_VERIFIED`. Production authorization remains empty.

## P1.3 PASS / MERGED

PR #46 established actual-fill-driven position progress on top of P1.2 ledger truth:

- new same-direction orders persist the exchange-observed pre-trade position baseline and target position in durable order parameters;
- fill progress is classified as `zero_fill`, `partial_fill` or `full_fill` from reconciled actual fill quantity;
- signed position movement is derived from actual fill quantity plus buy/sell side, never from requested notional;
- `actual_position_qty_from_fills = position_before_qty + signed_fill_quantity`;
- `target_gap_qty = target_position_qty - actual_position_qty_from_fills` while the baseline is trustworthy;
- `exchange_remaining_quantity`, `unfilled_quantity` and `resting_remaining_quantity` are distinct, so canceled unfilled size is not mislabeled as a live resting order;
- exchange remaining quantity must equal local submitted-minus-actual-fill truth or the transition fails closed;
- reconciliation exposes structured `fill_transitions` for rows touched by the cycle;
- transition-construction failure is persisted as `fill_transition_failed` uncertainty and blocks new risk;
- legacy rows without a position baseline preserve fill truth but report `position_tracking_status=baseline_unavailable` rather than inventing an exposure gap;
- reversal close legs can track actual-fill progress toward zero using the known pre-trade baseline;
- reversal open legs deliberately keep `position_before_qty=null`, because safe fresh-state handoff between reversal legs belongs to P1.4.

Focused tests cover 0%, partial and full fills; sell-side signed transition; live-resting versus canceled remainder; reversal-open baseline unavailability; overfill rejection; and local/exchange remaining-quantity mismatch rejection.

`EXEC-PARTIAL-FILL-P1.3` is registered as `IMPLEMENTATION_VERIFIED` in `config/decision_registry.json`. This is engineering verification only, not production authorization.

## P1.3 evidence

Exact final implementation head:

```text
68bd96f86945ab0fd42ad977142fdacef6a2642d
```

Final-head evidence:

- `Phase 0 baseline contract` run #27 / Actions run `31055589418`: SUCCESS;
- execution tests step inside that run: SUCCESS;
- research integration contract step inside that run: SUCCESS;
- `PR handoff governance` run #35 / Actions run `31055589427`: SUCCESS;
- evidence-only PR-body update then triggered `PR handoff governance` run #36 / Actions run `31055704431`: SUCCESS.

PR #46 was squash-merged to main as:

```text
fe663a0e8115baaa5c2ae9f1a59338e8f4a0c868
```

Review corrections:

1. self-review identified that fill-state classification alone could hide an exchange/local order-size mismatch; P1.3 now requires exchange remaining size to equal local submitted-minus-fill truth and fails closed on disagreement;
2. initial PR governance run #31 failed because the risk-section heading did not exactly match the governance contract; the PR body was corrected without code changes, then governance runs #32, #35 and #36 passed;
3. final diff review found no additional P1.3 implementation change required and no open review threads remained before merge.

## P1.3 boundaries deliberately not solved

P1.3 does **not** claim:

- P1.4 reversal safety or fresh account-state verification between reversal close/open legs;
- P1.5 metadata-driven size/price precision;
- P1.6 full open-order/fill/position/equity/margin post-submit reconciliation;
- P1.7 complete restart-recovery matrix;
- P1.8 kill/emergency paths;
- simultaneous multi-process race elimination or distributed locking;
- order slicing;
- production readiness;
- multi-asset production execution.

## Current unique next task: P1.4 Reversal safety

Roadmap requirement:

> No non-atomic long-to-short or short-to-long assumption.

Acceptance criteria:

- reduction and new-direction opening are distinct intents;
- reduce-only is used where applicable;
- failure during reversal cannot accidentally double directional risk.

P1.4 has **not** been implemented yet. Development must begin from current main on a fresh candidate branch after this post-merge handoff normalization is merged.

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

1. P1.4 fresh-state reversal safety remains unimplemented.
2. Cross-process simultaneous submission races/distributed locking remain unimplemented.
3. Order slicing remains unimplemented.
4. SQLite durability depends on the deployment actually mounting persistent storage; Vercel trade mode remains rejected by the current backend.
5. `userFillsByTime` pagination beyond the guarded response limit is not implemented; reaching the limit blocks rather than claiming complete truth.
6. Current BTC quantity precision remains hardcoded at five decimals; instrument-specific precision belongs to P1.5/later router work.
7. Production authorization remains empty.

## Latest project-drift assessment

```text
DRIFT_0
```

Reason: P1.3 followed the roadmap dependency order and changed no BRRK objective, strategy economics, product universe, Hyperliquid-first venue, leverage philosophy, 70% catastrophic-only boundary, human approval rule, ACTIVE/CANDIDATE separation, credential boundary, stopped research line or production authorization. Its reversal limitation is explicitly handed to P1.4 rather than being silently widened.

## Exact next action

```text
P1.4 Reversal safety
```

Start only from current main after verifying this post-merge normalization is merged. Keep P1.5+ blocked until P1.4 passes its own implementation/test/review/PR/final-head-CI/merge gate.

## Fresh-chat resume instructions

A fresh conversation should:

1. read the canonical files in the repository-defined order;
2. verify actual main, latest merged PR, open PR/issues and final CI rather than trusting handoff prose alone;
3. confirm P1.3 / PR #46 is merged and `EXEC-PARTIAL-FILL-P1.3` is registered;
4. confirm production authorization remains empty;
5. if this post-merge normalization is present on main, start only P1.4 from a fresh candidate branch.

Do not ask the user to repeat product decisions already captured in GitHub.
