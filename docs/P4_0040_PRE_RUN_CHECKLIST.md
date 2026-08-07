# LEVERAGE-0040 pre-run checklist

No checked item is a leverage-search result or production authorization.

Before `LEVERAGE-0040` may execute:

- [x] `LEVERAGE-0039` preserved as `STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED`.
- [x] `LEVERAGE-0040` preregistered with the corrected two-layer architecture.
- [x] BTC buy-and-hold and BTC/ETH/SOL/BNB equal-weight benchmarks preregistered.
- [x] Hyperliquid native funding-spike and degraded-fill/depth/capacity stresses preregistered.
- [x] Hyperliquid margin metadata captured and hashed before first result.
- [x] Architecture correction PR #84 merged.
- [x] cap=1 exact historical parity merged by PR #86.
- [x] liquidation-distance model and >1 multiplier policy merged by PR #88 before any >1 result.
- [x] post-#88 normalization merged by PR #89; normalized main `98396a5b510c5f0a717b954568921c1daef6edc8`.
- [x] one-time study semantics frozen on clean v2 branch before any >1 observation.
- [x] initial #90 fail-closed preflight detected invalid banded-holdings defensive-scale recovery before cap>1 construction.
- [x] `PREFLIGHT-RAW-TARGET-001`: R1 rebuilt raw V1/BRRK scale from frozen five-asset feature authority; published banded holdings demoted to legacy evidence only.
- [x] `PREFLIGHT-SESSION-TIMING-002`: first decision `2022-12-09` now correctly maps to first evaluation session `2022-12-10`.
- [x] corrected checkpoint head `0b396de4d2bf10f06fee1403836331459b7bd696` passed contract/preflight, Phase 0, research, P3.2 parity/golden, P4 cap=1, P4 prerequisite and governance; R1 preflight explicitly reported `cap>1 not evaluated`.
- [ ] latest handoff head repeats all applicable pre-result gates successfully.
- [ ] exact `RUN_ONCE_LEVERAGE_0040.marker` created once only after the preceding final pre-result gate is complete.
- [ ] `LEVERAGE-0040` first and only preregistered search run executed and immutable result committed/validated.

Current branch:

`p4-4/leverage-0040-one-time-study-v2`

Old v1 is **INVALID / ABANDONED / DO NOT MERGE / DO NOT REVIVE** and has no PR/result authority.

Current safety state:

```text
RUN_ONCE marker                         ABSENT
research/results/leverage_0040 summary ABSENT
1.10/1.20/1.30 candidate observation   NONE
result-selected threshold               NONE
operating budget selected              NO
production authorization               NONE
```

Marker path:

`research/leverage_0040/RUN_ONCE_LEVERAGE_0040.marker`

Required SHA-256:

`f54cdf362f60cad19d6c429ac4e008047b45d2cb537a95c96e2bc6dac5ce733a`

Corrected checkpoint evidence:

- study contract/preflight #7 `31186348512`: SUCCESS, 24 tests, compile PASS, pinned capacity artifact PASS, R1 real-data preflight PASS;
- Phase 0 #157 `31186348457`: SUCCESS, 281 passed + 5/5 integration;
- Research #63 `31186348431`: SUCCESS;
- P3.2 parity/golden #50 `31186348474`: SUCCESS;
- P4 cap=1 #16 `31186350411`: SUCCESS;
- P4 prerequisite #12 `31186349388`: SUCCESS;
- governance #219 `31186348416`: SUCCESS.

These are checkpoint runs only because the handoff updates create a newer pre-result head. The exact marker remains forbidden until that latest head is green.

After marker creation, the dedicated run-once workflow must execute the already-frozen suite once, commit immutable result artifacts, and never retrigger from those result commits. Any material post-result change requires a new experiment ID.
