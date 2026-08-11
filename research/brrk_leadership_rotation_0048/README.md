# BRRK-LEADERSHIP-ROTATION-0048

Status: **PREREGISTERED_NOT_RUN / PREREGISTRATION-ONLY CANDIDATE**

This directory formalizes the owner-approved revised 0048 architecture and numerical method after the architecture amendment merged at `09a676e0e704a360730b1df0a57e6010b5a15f00`.

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

## Result hierarchy

Possible formal outcomes include:

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

## Registry synchronization

The preregistration object and dataset declaration are registered atomically in `config/research_registry.json` and `config/dataset_exposure_registry.json`. The temporary registration writer is deleted before merge and is not part of the frozen preregistration surface.

This synchronization records governance metadata only. It does not fit a model, inspect a 0048 result, or consume an additional candidate variant.

The required `docs/CURRENT_STATE.md` preregistration handoff is synchronized separately as governance continuity metadata and does not change any frozen numerical method. The refreshed handoff preserves prior immutable research markers and the exact production-authorization invariants required by the repository governance suite.

## Preregistration-only boundary

At this stage the following files must **not** exist:

- `engine.py`
- `run_once.py`
- `RUN_INTERFACE.json`
- `PRIMARY_RESULT.json`
- `RESULT_SUMMARY.json`
- `EXECUTION.json`
- `RUN_ONCE.marker`
- `RESULT.md`
- any portfolio runner or allocation output

No model fit, calibration fit, historical candidate evaluation, CAGR/MDD test or portfolio allocation is authorized by this preregistration.

The only permitted next step after this preregistration is merged is a separate implementation-only branch that mechanically implements the frozen protocol with equivalence, symmetry, maturity, prequential-calibration and fail-closed tests. Only after that implementation boundary is merged and green may exactly one historical 0048 DEVELOPMENT execution occur.

Canonical BRRK, Phase 6, production authorization, signing authorization and order-submission authorization remain unchanged.
