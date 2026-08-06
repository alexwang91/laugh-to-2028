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
- P1.4 implementation PR: #48 open
- P1.4 candidate branch: `p1-4/reversal-safety`

## Current roadmap position

```text
PLANNING BASELINE: complete
CONTEXT-HANDOFF GOVERNANCE: complete
P0.1 Canonical product config: PASS / MERGED
P0.2 Decision registry: PASS / MERGED
P1.1 Deterministic order identity: PASS / MERGED
P1.2 Persistent order ledger: PASS / MERGED
P1.3 Partial-fill correctness: PASS / MERGED
P1.4 Reversal safety: IMPLEMENTATION VERIFIED / FINAL-HEAD CI PENDING / NOT MERGED
P1.5+ blocked until P1.4 closes its final evidence/merge gate
```

The only active implementation task is **P1.4 Reversal safety**. Do not start P1.5, P2, P3, P4, P5 or P8 while PR #48 remains unmerged.

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

## P1.1 PASS / MERGED

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

- position transition uses reconciled actual fills, never requested notional;
- zero / partial / full fill are explicit;
- actual position and target gap remain calculable while the baseline is trustworthy;
- live resting remainder and canceled unfilled remainder are distinct;
- local submitted-minus-fill truth must agree with exchange remaining size;
- inconsistent transition truth fails closed;
- reversal-open deliberately left the fresh between-leg position baseline unresolved for P1.4.

Exact final implementation head `68bd96f86945ab0fd42ad977142fdacef6a2642d` passed Phase 0 baseline contract run `31055589418`, execution tests, research integration and PR handoff governance before merge. `EXEC-PARTIAL-FILL-P1.3` is registered as `IMPLEMENTATION_VERIFIED`.

## P1.4 implementation verified on candidate

PR #48 implements the roadmap reversal-safety gate without changing strategy economics:

- old-direction reduction and new-direction opening remain distinct `reduce` and `increase` economic intents;
- reversal close uses `market_close` with explicit reduce-only semantics;
- after the close leg, the executor fetches a fresh Hyperliquid `clearinghouseState` account position;
- the new-direction open leg is not constructed or submitted until the fresh account position proves the old direction is flat;
- any partial old-direction remainder blocks the new-direction open leg;
- any unexpected cross-through into the opposite sign blocks the new-direction open leg instead of compounding risk;
- malformed account-position state fails closed;
- failure to obtain fresh account state fails closed;
- after verified flat, the opening intent persists `position_before_qty=0`, `reversal_flat_verified=true`, and `position_tracking_source=fresh_exchange_flat_after_reversal_close`.

Candidate tests cover:

- LONG -> SHORT after verified fresh flat;
- SHORT -> LONG through the same gate;
- partial close blocking the new-direction leg;
- unexpected cross-through blocking the new-direction leg;
- malformed position rows;
- fresh account-state read failure.

Self-review correction: checking close submission status alone is insufficient because submitted/filled response is not equivalent to current account position truth. The implementation therefore gates on a fresh account-level position read.

`EXEC-REVERSAL-SAFETY-P1.4` is registered as `IMPLEMENTATION_VERIFIED` in `config/decision_registry.json`. This is candidate engineering verification only; P1.4 is not merged and production authorization remains empty.

## P1.4 evidence so far

Candidate head after the mandatory CURRENT_STATE correction:

```text
b6a068bbe63f299bbaed680fc0aa5732c02cb2eb
```

That head passed:

- `PR handoff governance` run #39 / Actions run `31078103004`: SUCCESS;
- `Phase 0 baseline contract` run #30 / Actions run `31078103076`: SUCCESS;
- execution tests inside Phase 0 baseline contract: SUCCESS;
- research integration contract inside Phase 0 baseline contract: SUCCESS.

Earlier governance run #38 / Actions run `31078002807` failed only because the forward PR had not directly modified `docs/CURRENT_STATE.md`. That governance defect was corrected on the same PR; no implementation semantics changed for that correction.

The branch now also contains the verified decision-registry record and this evidence handoff update. **A new final-head CI run is required before merge.**

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

P1.4 engineering work does not authorize live deployment or increase risk.

## Open blockers / uncertainties

1. P1.4 final-head CI and merge remain outstanding.
2. P1.5 metadata-driven precision remains unimplemented.
3. P1.6 full post-submit account reconciliation remains unimplemented.
4. P1.7 complete restart recovery remains unimplemented.
5. P1.8 kill/emergency paths remain unimplemented.
6. Cross-process simultaneous submission races/distributed locking remain unimplemented.
7. Order slicing remains unimplemented.
8. SQLite durability still depends on real persistent deployment storage; Vercel trade mode remains rejected by the current backend.
9. `userFillsByTime` pagination beyond the guarded response limit remains a fail-closed blocker.
10. Production authorization remains empty.

## Latest project-drift assessment

```text
DRIFT_0
```

Reason: P1.4 is the exact roadmap dependency after P1.3. It only hardens reversal execution safety and changes no BRRK objective, strategy economics, product universe, Hyperliquid-first venue, leverage philosophy, 70% catastrophic-only boundary, human approval rule, ACTIVE/CANDIDATE separation, credential boundary, stopped research line or production authorization.

## Exact next action

```text
final-head CI on PR #48 -> merge -> normalize handoff to P1.5
```

Do not begin P1.5 until PR #48 is merged.

## Fresh-chat resume instructions

A fresh conversation should:

1. read the canonical files in the repository-defined order;
2. verify actual main, PR #48 head, open PR/issues and final-head CI rather than trusting handoff prose alone;
3. confirm P1.3 / PR #46 and handoff PR #47 are merged;
4. confirm `EXEC-REVERSAL-SAFETY-P1.4` is registered but production authorization remains empty;
5. if PR #48 is still open, continue only its P1.4 final-head CI/merge loop;
6. begin P1.5 only after P1.4 is PASS / MERGED and post-merge handoff is normalized.

Do not ask the user to repeat product decisions already captured in GitHub.