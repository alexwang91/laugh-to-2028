# 0072 Stage-7 handoff sync

Research ID: `BRRK-CRYPTO-CARRY-ATLAS-0072`

This governance-only handoff records the live merged truth after PR #345.

- Stage-7 zero-result preflight evidence PR #345 merged as `8736100e0d617d22b0580cfc1cdf5d52b330f4e8`.
- Formal lifecycle completion is therefore `7/10`.
- Controlled scientific-history reads remain `0`.
- CAPTURE-0002 raw-artifact downloads for Stage 8 remain `0`.
- Stage-8 controlled attempt remains `0/1` unconsumed.
- `research/0072-result-v1` remains absent at the Stage-7 evidence point.
- No `RUN_ATTEMPT.marker`, `PRIMARY_RESULT.json`, `EVIDENCE.json`, `EXECUTION.json`, or `RUN_ONCE.marker` existed at the Stage-7 evidence point.
- CAPTURE-0001 remains sealed failed after HTTP 451 and is permanently no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- Frozen science, source identities, six authorized scientific objects, read/call budgets, no-result-informed-rescue rule, and zero production/signature/order authority remain unchanged.

The existing `docs/CURRENT_STATE.md` handoff wording that says `PREFLIGHT EVIDENCE IN PROGRESS / FORMAL COMPLETION 6/10` is stale relative to merged PR #345. This file records the minimal forward governance correction without changing any frozen scientific contract.

## Exact next legal action

Stage 8 may execute exactly once only after a durable remote `research/0072-result-v1/RUN_ATTEMPT.marker` exists before the first CAPTURE-0002 raw-artifact download or any controlled content read. The attempt must obey the Stage-6 frozen boundary: at most one raw-artifact download, exactly the six authorized scientific-object reads at most once each, zero source-network fetches, scientific engine exactly once, create-only `RUN_ATTEMPT.marker -> PRIMARY_RESULT.json -> EVIDENCE.json -> EXECUTION.json -> RUN_ONCE.marker`, and no same-ID rerun/retune/rescue/recompute after marker creation.
