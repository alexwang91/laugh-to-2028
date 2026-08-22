# 0074 Stage-8 terminal CI handoff

- Stage 7 ZERO-RESULT PREFLIGHT merged at `4e2dd98519ce9d513318beb5678ac1e00be3a04b`.
- Stage 8 is terminal `INVALID_EXECUTION` on PR #369.
- `RUN_ATTEMPT.marker` is durable and attempt `1/1` is permanently consumed.
- Canonical create-only persistence remains sealed in frozen order: `PRIMARY_RESULT.json` -> `EVIDENCE.json` -> `EXECUTION.json` -> `RUN_ONCE.marker`.
- A concurrent post-marker path is recorded in `STAGE8_CONCURRENCY_INCIDENT.json`; final correction is recorded in `STAGE8_SEAL_SUPPLEMENT.json` without overwriting the create-only bundle.
- Final operational accounting: Stage6 artifact downloads after marker `1`; controlled scientific/history reads `402`; authorized historical payloads opened scientifically `402/402`, each at most once; scientific engine invocations `1/1`, but the invocation is inadmissible because the local harness was not frozen Stage4 implementation; scientific source-network fetches `0`; scientific values exposed `true`.
- No local harness metrics were persisted as admissible 0074 scientific evidence. No PASS/FAIL strategy-performance inference is available.
- Same-ID rerun, retune, rescue, source substitution, candidate replacement, history extension, second engine invocation and recomputation are forbidden.
- `docs/CURRENT_STATE.md` records the incident-aware terminal Stage8 accounting and still contains the immutable line `workflow run                         31381953131 / attempt 1` exactly.
- Frozen Stage3 science, Stage4 code identity, Stage6 source identities and production/signature/order authority did not change.

This connector-authored governance-only update restores a normal exact PR head after the self-deleting CURRENT_STATE writer and supersedes the earlier zero-read handoff snapshot. Fresh exact-head standing CI is authoritative for merge.
