# 0074 Stage 8 controlled-attempt authorization gate

State: `BLOCKED_PENDING_EXPLICIT_STAGE8_AUTHORIZATION / ATTEMPT 0/1 / PRE-MARKER`

Stage 7 zero-result preflight merged at `4e2dd98519ce9d513318beb5678ac1e00be3a04b` with terminal classification `PREFLIGHT_PASS_ZERO_RESULT`.

No `RUN_ATTEMPT.marker` exists. No controlled historical payload has been read. Scientific engine calls remain `0`. Stage8 scientific source-network fetches remain `0`.

The standing governance authorization permits creation and maintenance of this Stage8 branch/PR and other reversible governance-only work, but it explicitly excludes the irreversible Stage8 controlled attempt. Before any attempt-consuming action, a fresh explicit authorization must cover marker creation followed by the single controlled read/engine sequence under the frozen Stage3/Stage6/Stage7 boundaries.

Required irreversible order after authorization:
1. Re-establish live main and pass identity-only/metadata-only zero-result checks.
2. Create durable `RUN_ATTEMPT.marker` and verify remote persistence. Marker durability consumes attempt `1/1`.
3. Only after marker durability, read each authorized historical object at most once.
4. Invoke the scientific engine exactly once.
5. Persist the result bundle create-only.
6. Seal with `RUN_ONCE.marker`.

Forbidden after marker durability: rerun, retune, rescue, source substitution, candidate replacement, history extension, recomputation, or any second scientific-engine invocation.

Production authorization remains false. Signature authorization remains false. Order-submission authorization remains false.
