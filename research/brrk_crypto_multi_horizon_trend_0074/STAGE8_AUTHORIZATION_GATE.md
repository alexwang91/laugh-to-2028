# 0074 Stage 8 controlled-attempt authorization gate

State: `AUTHORIZED_TO_PROCEED / ATTEMPT 0/1 / PRE-MARKER`

Stage 7 zero-result preflight merged at `4e2dd98519ce9d513318beb5678ac1e00be3a04b` with terminal classification `PREFLIGHT_PASS_ZERO_RESULT`.

Fresh contemporaneous authorization was granted by the user on 2026-08-22 at approximately 23:23 +02:00 with the explicit instruction `授权！` in direct response to the request for authorization of the unique 0074 Stage 8 controlled historical attempt. This authorization covers the irreversible marker-before-read execution under the already-frozen Stage3/Stage6/Stage7 contract and does not relax any frozen-science, exactly-once, source, candidate, history-window, budget, no-rescue, no-rerun or production-authority constraint.

Fresh live pre-marker recheck after authorization confirmed:
- PR #369 remains the only open 0074 forward PR.
- Stage 7 remains merged and terminal `PREFLIGHT_PASS_ZERO_RESULT`.
- Stage6 staging artifact `9480304574` / `0074-stage6-authorized-payloads-v1` remains nonexpired and retrievable.
- Stage6 evidence remains exactly 402 authorized payload objects, 402 hash-verified, 402 offline-ZIP-readable, `scientific_values_exposed=false`.
- `RUN_ATTEMPT.marker` is absent.
- `RUN_ONCE.marker` is absent.
- controlled scientific-history reads remain `0`.
- scientific engine calls remain `0`.
- Stage8 scientific source-network fetches remain `0`.
- controlled attempt remains `0/1`.

Required irreversible order after this authorization:
1. Create durable `RUN_ATTEMPT.marker` and verify remote persistence. Marker durability consumes attempt `1/1`.
2. Only after marker durability, read each authorized historical object at most once.
3. Invoke the scientific engine exactly once.
4. Persist the result bundle create-only.
5. Seal with `RUN_ONCE.marker`.

Forbidden after marker durability: rerun, retune, rescue, source substitution, candidate replacement, history extension, threshold/horizon alteration, recomputation, or any second scientific-engine invocation.

Production authorization remains false. Signature authorization remains false. Order-submission authorization remains false.
