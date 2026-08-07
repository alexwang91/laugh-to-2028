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
- [ ] `LEVERAGE-0040` first and only preregistered search run executed.

PR #88 final head `9ed8c627afd9800f8c4a8cf79246a07bc89e6108` evidence:

- dedicated prerequisite #4 / `31178219708`: SUCCESS, 14 passed;
- Phase 0 #149 / `31178220870`: SUCCESS, 257 passed + 5/5 integration;
- Research evidence #55 / `31178223443`: SUCCESS;
- P3.2 parity/golden #42 / `31178219593`: SUCCESS;
- P4 cap=1 parity #8 / `31178220456`: SUCCESS;
- latest metadata/ready governance #209 / `31178603896`: SUCCESS;
- expected-head squash merge `8d512479c5b2a0522409afbf0b63b817de6c6fe0`.

No 1.10/1.20/1.30 historical result existed before either pre-run prerequisite was frozen and merged.

The only unchecked pre-run item is now the actual one-time `LEVERAGE-0040` study execution. That execution may begin only from a fresh branch after this normalization is merged. Any post-result change to the preregistered study or multiplier policy requires a new experiment ID.
