# LEVERAGE-0040 pre-run checklist

No checked item is a leverage-search result or production authorization.

Before `LEVERAGE-0040` may execute:

- [x] `LEVERAGE-0039` preserved as `STOPPED_PRE_RUN / NO_RESULT_EVER_PRODUCED`.
- [x] New experiment ID `LEVERAGE-0040` preregistered.
- [x] Master Plan two-layer architecture restored.
- [x] BTC buy-and-hold benchmark preregistered.
- [x] BTC/ETH/SOL/BNB equal-weight buy-and-hold benchmark preregistered.
- [x] Hyperliquid native funding-spike stress preregistered.
- [x] Degraded-fill/depth/capacity stress preregistered.
- [x] Official Hyperliquid margin metadata captured and hashed before first result.
- [x] Architecture-correction PR #84 merged with CI evidence.
- [x] Separate leverage-multiplier composition merged without modifying the frozen defensive selector.
- [x] Cap `1.00` exact historical BRRK parity merged by PR #86.
- [x] Liquidation-distance implementation validated and merged against the frozen margin snapshot by PR #88.
- [x] >1 multiplier-selection algorithm frozen and merged before observing any >1 result by PR #88: `1 + (cap-1) * defensive_scale`.
- [x] Post-#88 handoff normalization merged by PR #89; normalized main is `98396a5b510c5f0a717b954568921c1daef6edc8`.
- [x] One-time study implementation semantics frozen on clean v2 branch before any >1 result: P3.3 drift/band, route/funding, liquidation collateral, capacity, stress, bootstrap, broad-region and deterministic selection rules.
- [ ] Clean v2 pre-study draft PR passes final applicable contract/preflight, Phase 0, research, P3.2 parity/golden, P4 cap=1, P4 prerequisite and governance gates.
- [ ] Exact `RUN_ONCE_LEVERAGE_0040.marker` created once only after the preceding CI gate is complete.
- [ ] `LEVERAGE-0040` first and only preregistered search run executed and immutable result committed/validated.

Current branch:

`p4-4/leverage-0040-one-time-study-v2`

Old `p4-4/leverage-0040-one-time-study-v1` is **INVALID / ABANDONED / DO NOT MERGE / DO NOT REVIVE** because a tool-layer write-routing error created transient empty-file commits before any PR or result existed. The v2 branch is derived from a clean intended tree; compare against main proves the transient file is absent.

Current one-time study safety state:

```text
RUN_ONCE marker                         ABSENT
research/results/leverage_0040          ABSENT
1.10/1.20/1.30 candidate observation   NONE
result-selected threshold               NONE
operating budget selected              NO
production authorization               NONE
```

The exact run marker must hash to:

`f54cdf362f60cad19d6c429ac4e008047b45d2cb537a95c96e2bc6dac5ce733a`

The contract CI's `--preflight-only` path may validate real historical inputs and the cap1 baseline, but must return before evaluating cap>1. If the preflight fails, it may be corrected in the same PR while no >1 result exists.

After the exact marker is created, the dedicated run-once workflow must execute the frozen suite once, commit immutable result artifacts, and never retrigger from those result commits. Any material post-result change requires a new experiment ID.
