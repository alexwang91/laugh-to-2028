# BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053

Status: **PREREGISTERED / 4H DATA HASH-FROZEN / SUPPORT-FUNNEL IMPLEMENTATION-ONLY / NO SUPPORT RESULT / NO MODEL FIT / NO PREDICTIVE RESULT**.

0053 is a label-blind 4h support-feasibility study created after the immutable 0048 insufficient-support closeout. It measures whether 4h resolution creates genuine dependence-aware support under calendar-equivalent semantics or merely more correlated rows.

Governance objective type: **`DATA_QUALITY`**. Primary authority remains Track A only: 2190 eligible matured training origins, 2190 matured eligible shadow origins, 336-row dependence blocks, 12 complete blocks required. Track B (365/365/56) and Track C (365/365/336) remain diagnostics only.

No ETH/SOL winner label, model fit, calibration fit, NLL/AUC/Brier, confidence threshold or portfolio economics is permitted under this ID.

## Frozen data identity

The first complete valid payload was captured in GitHub Actions run `31512578577`, job `93849786583` after a pre-exposure source-base amendment to Binance's official market-data-only REST base.

- common coverage: `2020-08-11T04:00:00Z` through `2026-08-02T20:00:00Z`
- common bars: `13097`
- BTC raw bars: `13098`
- ETH raw bars: `13098`
- SOL raw bars: `13097`
- canonical payload SHA256: `471b54991ae648b79433285f073ea7bc813663319b6e2389c1682dad1a319135`
- payload size: `7030655` bytes
- internal 4h gaps: `0`
- no synthetic fill / no alternate venue

The payload is immutable researcher-exposed DEVELOPMENT history and cannot be replaced under 0053.

## Zero-result support implementation

`support_funnel.py` mechanically implements only:

1. exact payload SHA verification and common 4h index validation;
2. calendar-equivalent BTC FAST trend over 120/360/720/1440 bars with weights 0.15/0.25/0.30/0.30;
3. support eligibility `BTC_FAST_4H >= 0` after full 1440-bar feature history;
4. 336-bar maturity before an eligible origin can count toward training support;
5. track-specific training and shadow-support counters;
6. 168-bar anchor-relative refit grid before formal support activates;
7. full 336-bar future maturity for every formal origin;
8. sequential ordered eligible-row dependence blocks for Tracks A/B/C.

The implementation intentionally computes **no ETH/SOL target value or winner label** and contains no predictive model/calibration code.

Synthetic-only GitHub Actions run `31514184465` passed: support counter `py_compile`, exact trend-math contract, maturity/refit causality, ineligible-row attrition, block counting, Track-A-only classification authority, wrong-hash fail-closed behavior, and the zero-result artifact boundary. The temporary workflow was removed after validation.

**The frozen real 4h payload has not yet been passed to `measure_support_funnel()` on this implementation branch.** Therefore Track A/B/C counts and the 0053 primary classification remain unknown.

The next permitted stage after a fully green implementation merge is a separately controlled exactly-once support measurement against the frozen payload SHA. No predictive research is unlocked merely by merging this code.
