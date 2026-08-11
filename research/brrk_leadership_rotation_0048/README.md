# BRRK-LEADERSHIP-ROTATION-0048

Status: **MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED**

0048 was an ETH/SOL Beta-leadership information study inside the causal `BTC_TREND_FAST >= 0` state. The architecture, numerical preregistration, implementation and controlled-execution boundary were frozen before the unique DEVELOPMENT execution.

The unique historical execution has now completed. The result is **INCONCLUSIVE because preregistered support gate G1 failed**: only 4 complete 56-observation formal-evaluation blocks were available versus the required 12. This is neither a PASS nor a formal model FAIL.

## Frozen scientific question

Within a causally identified crypto-uptrend environment, can current ETH/SOL relative state predict which Beta asset will produce the stronger subsequent 14/28/56-day path-integrated relative wealth path?

BTC is a defensive anchor / eligibility asset, not a competing 0048 winner. Cash is outside 0048.

## Frozen candidate

- eligibility: canonical `BTC_TREND_FAST >= 0`;
- target: equal-weight 14/28/56 path-integrated ETH/SOL leadership;
- features: K1/K2/K3/K4 non-overlapping relative-momentum age buckets, Persistence60, Position120, Participation20/120;
- model: expanding Laplace-prevalence offset + no-intercept ridge logistic, lambda=1;
- maximum label maturity: 56 calendar days;
- first shadow-model support: 365 matured eligible origins;
- refit cadence: 28 calendar days;
- calibration: shadow-prequential prior-preserving one-parameter dynamic-logit scaling;
- first formal evaluation support: 365 matured eligible shadow predictions;
- primary metric: simultaneous dependence-aware candidate-minus-baseline NLL upper confidence bounds;
- uncertainty plan: 10,000 moving-block bootstrap replicates, block length 56 eligible observations, seed 4292549012;
- confidence-strength diagnostics: natural cubic spline and one frozen segmented breakpoint.

## Baselines

1. B0 uniform 0.5;
2. B1 expanding Laplace historical SOL-lead prevalence;
3. B2 lagged 14/28/56 path leader;
4. B3 simple 60-day SOL/ETH relative momentum.

## Dataset identity

0048 reused the immutable 0047 Binance BTC/ETH/SOL UTC daily evidence through 2026-08-02.

```text
payload SHA256
d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193

data budget        DEVELOPMENT
researcher exposed true
independent OOS    false
```

No new 0048 market fetch or data re-preparation occurred.

## Unique controlled execution

```text
controlled HEAD                 12f70c927df39b9e2ba799c8d4c597a7ae9b1726
GitHub Actions run              31505757608
job                            93826791780
run attempt                    1
preflight                      PREFLIGHT_PASS_ZERO_RESULT
final marker                   VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN
actual variants evaluated      1
```

`RUN_ATTEMPT.marker` was durably persisted before historical model computation. `RUN_ONCE.marker` was persisted last. No rerun occurred.

Official artifact:

```text
name    brrk-0048-execution-bundle
id      9106961253
digest  sha256:3ae658faee064add594b5494bd660dec3d3cee735a5a7cf517e3a01f408bfb32
```

## Formal result

```text
classification                    MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT
G0                                PASS
G1                                FAIL
required complete 56-row blocks   12
observed complete 56-row blocks    4
formal rows                       245
minimum rows implied by G1        672
formal window                     2025-01-14 through 2026-05-10
ETH-leader full blocks              4
SOL-leader full blocks              4
bootstrap                         NOT RUN / NOT ELIGIBLE AFTER G1
```

The binding failure was total support, not one-sided class absence. The frozen causal pipeline — feature validity, BTC-uptrend eligibility, training burn-in, shadow-prequential calibration burn-in and 56-day target maturity — left materially fewer formal rows than assumed at preregistration.

## Descriptive non-gating evidence

These values are immutable outputs of the unique execution but cannot override the G1 stopping rule:

```text
candidate NLL            0.7185986815
B0 NLL                   0.6931471806
B1/B2/B3 NLL             0.7185986815
candidate Brier          0.2627024107
B0 Brier                 0.2500000000
AUC                      0.3789464939
balanced accuracy        0.5508059156
confidence-margin rho   -0.4111806894
```

At the first formal refit, `gamma_candidate = gamma_B2 = gamma_B3 = 0.0`; the prior-preserving calibration therefore emitted the expanding prevalence prior at that refit. Aggregate candidate/B1/B2/B3 NLL and Brier are exactly equal on the observed formal segment. This is adverse diagnostic evidence, not a post-hoc formal FAIL classification.

## Interpretation boundary

0048 does not establish incremental ETH/SOL leadership information, but it also does not formally reject it. The preregistered dependence-aware support floor was not met, so G2 and all later inferential gates were not eligible.

The result does **not** authorize:

- 0049 concentration research from the 0048 lineage;
- 60/80/90/100 winner-weight backtests;
- portfolio CAGR/Sharpe/Calmar/MDD evaluation;
- Beta-to-BTC shelter timing;
- BTC-to-cash exit;
- integrated routing;
- canonical BRRK modification;
- Phase 6 changes;
- leverage/shorting;
- signing, order submission or production authority.

## Closure

0048 is permanently closed to same-ID rerun, retuning and rescue. Any reduction of the support requirement, burn-in change, eligibility change, calibration change, feature/target change, historical-window extension or other result-informed modification requires a **new research ID and new preregistration**.

Authoritative closeout artifacts:

- `RUN_ATTEMPT.marker`
- `PRIMARY_RESULT.json`
- `RESULT_SUMMARY.json`
- `EXECUTION.json`
- `RUN_ONCE.marker`
- `RESULT.md`
- `CLOSEOUT.json`
