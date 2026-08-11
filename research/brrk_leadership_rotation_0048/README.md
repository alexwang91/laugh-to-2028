# BRRK-LEADERSHIP-ROTATION-0048

Status: **PREREGISTERED_NOT_RUN / IMPLEMENTATION-ONLY ZERO-RESULT CANDIDATE**

The revised architecture and numerical preregistration are frozen. This directory now contains a zero-result implementation of the frozen protocol, but no historical 0048 scientific execution has occurred.

## Scientific scope

0048 is an ETH/SOL Beta-leadership information study inside the pre-existing causal BTC-fast-trend supportive state.

It asks whether a frozen seven-feature antisymmetric ETH/SOL relative-state model predicts the stronger 14/28/56-day path-integrated Beta leader beyond static prevalence, lagged leader persistence and simple 60-day relative momentum.

BTC is an eligibility/defensive-anchor asset, not a competing 0048 winner. Cash is outside 0048.

## Frozen primary candidate

- eligibility: canonical `BTC_TREND_FAST >= 0`;
- forward target: equal-weight 14/28/56 path-integrated ETH/SOL leadership;
- features: four non-overlapping relative-momentum age buckets + persistence60 + symmetric position120 + relative quote-volume participation20/120;
- model: expanding Laplace-prevalence offset + no-intercept ridge logistic, lambda=1;
- maximum label maturity: 56 calendar days;
- refit cadence: 28 calendar days;
- first shadow model support: 365 matured eligible origins;
- calibration: shadow-prequential prior-preserving one-parameter dynamic-logit scaling;
- first formal calibrated evaluation support: 365 matured eligible shadow predictions;
- primary metric: simultaneous dependence-aware candidate-minus-baseline NLL upper confidence bound;
- uncertainty: 10,000 moving-block bootstrap replicates, block length 56 eligible observations, seed 4292549012;
- confidence-strength diagnostic: natural cubic spline with internal knots 0.25/0.50/0.75;
- HIGH breakpoint: exactly one segmented-regression breakpoint in [0.20,0.80], subject to frozen admissibility/stability gates.

## Frozen baselines

1. uniform 0.5;
2. expanding Laplace historical SOL-lead prevalence;
3. lagged 14/28/56 path leader;
4. simple 60-day SOL/ETH relative momentum.

The candidate must beat all probabilistic causal baselines under the simultaneous NLL gate.

## Zero-result implementation

`engine.py` mechanically implements the preregistered mathematics without executing the frozen historical study.

Key implementation properties:

- historical input is accepted only through the immutable 0047 market-evidence wrapper and must match payload SHA256 `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`;
- BTC eligibility reuses the already frozen 0047 `trend_score` implementation and FAST weights;
- ETH/SOL feature exchange maps the seven-feature vector to its negative and model probabilities to complements;
- 14/28/56 target code is tested against the literal preregistered path-integral formula;
- training labels cannot enter before 56 calendar days have elapsed;
- refitting is expanding and anchored every 28 calendar days;
- calibration consumes only matured shadow-prequential predictions;
- candidate and B2/B3 baselines use the same prevalence-offset/ridge/refit/calibration machinery;
- bootstrap resamples aligned evaluation rows without retraining the walk-forward models;
- the one-breakpoint segmented model uses a deterministic global SSE search over the frozen admissible family;
- spline derivatives remain diagnostic only;
- no allocation, CAGR, MDD, Beta-to-BTC or BTC-to-cash function exists.

`test_engine_contract.py` uses deterministic **synthetic data only**. Synthetic unit-test fits verify mathematical and causal invariants and are not an evaluation of the registered historical candidate variant.

`IMPLEMENTATION_BOUNDARY.json` records the zero-result boundary and explicitly leaves historical scientific execution unauthorized.

## Result hierarchy

Possible future formal outcomes remain:

- `INVALID_EXECUTION`;
- `MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT`;
- `MEASUREMENT_INCONCLUSIVE_CALIBRATION_UNIDENTIFIABLE`;
- `FAIL_NO_INCREMENTAL_DYNAMIC_LEADERSHIP`;
- `FAIL_NO_ROBUST_DYNAMIC_LEADERSHIP`;
- `PASS_LEADERSHIP_INFORMATION_NO_CONCENTRATION_HANDOFF`;
- `PASS_ONE_SIDED_LEADERSHIP_NO_FULL_ROUTER`;
- `PASS_LEADERSHIP_INFORMATION_CONCENTRATION_HANDOFF_ELIGIBLE`.

A leadership-information PASS does not require the confidence breakpoint to pass. Failure of the HIGH translation does not erase valid continuous leadership information.

## Dataset status

The study reuses the already researcher-exposed 0047 BTC/ETH/SOL Binance UTC daily market evidence through 2026-08-02. The source payload identity is frozen as:

`sha256:d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`

This is DEVELOPMENT history, not independent OOS.

## Registry status

The preregistration object and dataset declaration remain byte-for-byte registered in `config/research_registry.json` and `config/dataset_exposure_registry.json`.

Implementation does **not** change:

- `declared_variant_budget = 1`;
- `actual_variants_evaluated = 0`;
- `result_status = PREREGISTERED_NOT_RUN`;
- the registered dataset exposure state;
- canonical BRRK;
- Phase 6;
- production/signing/order authority.

## Implementation-only boundary

At this stage the following files must **not** exist:

- `run_once.py`
- `RUN_INTERFACE.json`
- `PRIMARY_RESULT.json`
- `RESULT_SUMMARY.json`
- `EXECUTION.json`
- `RUN_ONCE.marker`
- `RESULT.md`
- any portfolio runner or allocation output

No registered-history 0048 model fit, calibration fit, candidate evaluation, CAGR/MDD test or portfolio allocation is authorized by this implementation branch.

The only permitted next step after this implementation is merged and all standing CI is green is a **separate controlled-execution stage** that adds a hash-bound run interface/run-once boundary and then performs exactly one historical DEVELOPMENT execution. Any valid scientific output closes 0048 to same-ID rerun, retuning and rescue.

Canonical BRRK, Phase 6, production authorization, signing authorization and order-submission authorization remain unchanged.
