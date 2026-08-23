# 0075 Stage8 CONTROLLED ATTEMPT authorization gate

## Lifecycle scope

Stage7 ZERO-RESULT PREFLIGHT merged at `3af2a58cb7ff12be37f918f2c45f44369bd0900d` with terminal `PREFLIGHT_PASS_ZERO_RESULT`. This Stage8 branch starts from that exact merge and remains pre-marker.

## Current gate

`AUTHORIZED_TO_PROCEED / ATTEMPT 0/1 / PRE-MARKER`

- controlled attempt: `0/1`
- `RUN_ATTEMPT.marker`: absent
- controlled scientific-history reads: `0`
- scientific engine: `0/1`
- Stage8 scientific source-network fetches: `0`
- scientific values exposed: `false`
- `RUN_ONCE.marker`: absent
- Stage8 result bundle: absent

## Explicit contemporaneous authorization

On 2026-08-23 the repository owner/user explicitly authorized this exact irreversible scope with the instruction:

> “授权执行 0075 Stage8 controlled attempt 1/1，并按既定 frozen science、marker-before-read、exactly-once 规则立即推进。”

This authorization covers consumption of the unique `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-0075` Stage8 controlled attempt `1/1`. It does not relax frozen science, exactly-once, marker-before-read, zero Stage8 scientific source-network fetches, no-result-informed-rescue, source identity, candidate identity, history window, or production-authority constraints.

## Immutable execution order after authorization

1. Re-establish live main ancestry and identity-only / metadata-only zero-result pre-marker readiness.
2. Persist contemporaneous explicit authorization for this exact 0075 Stage8 scope.
3. Require fresh exact-head metadata/governance pre-marker checks to remain successful.
4. Create `RUN_ATTEMPT.marker` and verify remote durability. Marker durability consumes attempt `1/1`.
5. Read each authorized historical object at most once under the frozen Stage6 manifest and identities.
6. Run the frozen scientific engine exactly once.
7. Perform zero Stage8 scientific source-network fetches.
8. Persist the create-only immutable result bundle.
9. Create `RUN_ONCE.marker` to seal the attempt.

After marker durability, rerun, retune, rescue, source substitution, candidate replacement, history extension and recomputation are permanently forbidden.

## What did not change

Stage3 frozen science, Stage6 source/object identities, Stage7 zero-result PASS, lifecycle ordering, and immutable budgets remain unchanged. No scientific payload value was opened. No controlled read, engine call, result-informed action, source-network fetch, marker creation, result bundle creation, production authorization, signature authorization, or order-submission authorization occurred.

The exact historical line `workflow run                         31381953131 / attempt 1` remains immutable and must remain present in `docs/CURRENT_STATE.md`. CAPTURE-0001 remains sealed failed HTTP 451 with no retry. CAPTURE-0002 remains permanently claimed with no refetch.
