# LEVERAGE-0040 pre-run checklist

No checked item is a leverage-search result or production authorization.

Before `LEVERAGE-0040` may execute:

- [x] `LEVERAGE-0039` preserved as `STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED`.
- [x] `LEVERAGE-0040` preregistered with the corrected two-layer architecture.
- [x] BTC buy-and-hold and BTC/ETH/SOL/BNB equal-weight benchmarks preregistered.
- [x] Hyperliquid native funding-spike and degraded-fill/depth/capacity stresses preregistered.
- [x] Hyperliquid margin metadata captured and hashed before first result.
- [x] Architecture correction PR #84 merged.
- [x] cap=1 exact historical BRRK parity merged by PR #86.
- [x] liquidation-distance model and >1 multiplier policy merged by PR #88 before any >1 result.
- [x] post-#88 normalization merged by PR #89; normalized main `98396a5b510c5f0a717b954568921c1daef6edc8`.
- [x] one-time study semantics frozen on clean v2 branch before any >1 observation.
- [x] initial #90 fail-closed preflight caught invalid banded-holdings defensive-scale recovery before cap>1 construction.
- [x] `PREFLIGHT-RAW-TARGET-001`: raw V1/BRRK scale rebuilt from frozen five-asset feature authority; banded holdings are legacy evidence only.
- [x] `PREFLIGHT-SESSION-TIMING-002`: first decision `2022-12-09` maps to first evaluation session `2022-12-10`.
- [x] corrected R1 checkpoint passed contract/preflight, Phase 0, research, P3.2 parity/golden, P4 cap=1, P4 prerequisite and governance; preflight explicitly reported `cap>1 not evaluated`.
- [x] subsequent handoff head `0db6544af1793f48c30f9eb0b3cb98629bee58ba` also passed all seven applicable gates.
- [x] contract CI lifecycle frozen before first result: result absent => R1 preflight only; immutable result present => validator only, never a second study execution.
- [ ] latest lifecycle-hardened pre-result head passes all applicable gates and latest metadata/ready governance.
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

Lifecycle invariant:

```text
summary absent  -> contract CI may run real R1 --preflight-only and must exit before cap>1 construction
summary present -> contract CI must validate immutable committed result only; it must not redownload the study artifact or rerun historical research
```

This invariant is regression-tested before first result and prevents post-result handoff/decision-registry updates from accidentally causing a second LEVERAGE-0040 execution.

After the exact marker is created, the dedicated run-once workflow must execute the already-frozen suite once, commit immutable result artifacts, and never retrigger from those result commits. Any material post-result change requires a new experiment ID.
