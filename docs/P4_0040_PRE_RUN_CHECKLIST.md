# LEVERAGE-0040 pre-run checklist

No item in this file is a leverage-search result or production authorization.

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
- [ ] Liquidation-distance implementation validated and merged against the frozen margin snapshot. **Candidate implementation/contract exists on the current prerequisite branch; CI pending.**
- [ ] >1 multiplier-selection algorithm frozen and merged before observing any >1 result. **Candidate pre-run addendum freezes `1 + (cap-1) * defensive_scale`; CI pending.**
- [ ] `LEVERAGE-0040` first and only preregistered search run executed.

The current prerequisite branch contains no 1.10/1.20/1.30 historical candidate output. The multiplier policy was frozen before any >1 result observation.

Cap=1 parity is a wiring/baseline gate only. It produced no >1 candidate, no leverage selection and no production authorization.

If any unchecked prerequisite is bypassed, the resulting leverage result is invalid for promotion.
