# BRRK-CRYPTO-DELTA-NEUTRAL-CARRY-STRATEGY-0073 — ZERO-RESULT PREFLIGHT CONTRACT

Status: `CONTRACT ONLY / STAGE 7 NOT STARTED / ZERO CONTROLLED HISTORY READS`

Date: 2026-08-22

## Purpose

This file is a Stage-6 completion artifact that prospectively defines the only legal Stage-7 ZERO-RESULT PREFLIGHT behavior. Its presence does not start Stage 7, consume the controlled attempt, authorize a historical payload read, create an attempt marker, or call the scientific engine.

## Entry gate

Stage 7 may begin only after Stage 6 is merged from the exact authorized-object boundary commit. Until that merge:

- controlled attempt remains `0/1`;
- controlled scientific/history reads remain `0`;
- scientific engine calls remain `0`;
- scientific source-network fetches remain `0`;
- `RUN_ATTEMPT.marker` must not exist for 0073;
- no authorized archive ZIP/CSV payload may be opened.

## Frozen capture identity

Stage 7 must inherit without modification:

- capture cutoff `2026-07-31T23:59:59.999999Z`;
- study window `2024-08-01T00:00:00Z` through `2026-07-31T23:59:59.999999Z` inclusive;
- exact Stage-6 authorized-object manifest and its persisted SHA-256 identities;
- maximum scientific content-read budget `1` per authorized object;
- exactly three candidates `C1`, `C2`, `C3` and all Stage-3 frozen science.

No Stage-7 action may add, remove, replace, extend or re-hash an authorized object based on realized scientific content.

## Zero-result checks allowed in Stage 7

Stage 7 may inspect only non-scientific identity and execution metadata needed to prove that a single Stage-8 attempt can run without ambiguity. Allowed checks are limited to:

1. manifest schema completeness and unique object IDs;
2. exact path/checksum/SHA-256 field presence;
3. duplicate-path and duplicate-hash detection;
4. candidate/asset/venue/instrument-type membership against the frozen contract;
5. UTC coverage arithmetic against the frozen 730-day window;
6. per-object read-budget value exactly `1`;
7. local engine/config file identities and deterministic parameter equality to the merged Stage-3/Stage-4 contract;
8. create-only result destination emptiness and marker-path availability;
9. proof that Stage-8 source-network fetch budget is `0`;
10. proof that no scientific result field, return, PnL, funding realization, basis realization, stress outcome, bootstrap output, DSR or PBO value was read or computed.

Stage 7 must fail closed if any identity or execution prerequisite is missing. It may not repair the failure by changing sources, candidates, thresholds, costs, stress definitions, capture cutoff or study window.

## Forbidden in Stage 7

Stage 7 must not:

- open or parse any authorized historical ZIP/CSV payload;
- query historical market APIs for scientific values;
- calculate returns, carry, funding PnL, basis, volatility, drawdown or any strategy metric;
- create `RUN_ATTEMPT.marker` or `RUN_ONCE.marker`;
- call the scientific engine;
- consume any per-object scientific read budget;
- substitute an unavailable C2 or C3 source;
- infer historical instrument eligibility from present-day metadata;
- perform result-informed rescue, retune, rerun or recomputation.

## Stage-7 terminal states

Stage 7 may produce only one of two governance outcomes:

- `PREFLIGHT_PASS_ZERO_RESULT`: every identity/execution prerequisite is mechanically satisfied and Stage 8 may be proposed on a new independent branch.
- `PREFLIGHT_BLOCKED_ZERO_RESULT`: one or more prerequisite is missing or inconsistent; Stage 8 remains prohibited and no scientific attempt is consumed.

Neither outcome is a scientific result and neither may be described as PASS/FAIL evidence for the strategy.

## Stage-8 handoff if preflight passes

A later Stage-8 branch must re-establish live main, verify the exact merged Stage-6 and Stage-7 commits, then create the durable remote `RUN_ATTEMPT.marker` before the first authorized historical content read. Only after that marker exists may each manifest object be opened at most once and the scientific engine be called exactly once. Source-network fetches during that attempt remain fixed at `0`.
