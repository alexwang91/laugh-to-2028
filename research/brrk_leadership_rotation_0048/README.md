# BRRK-LEADERSHIP-ROTATION-0048

Status: **PREREGISTERED_NOT_RUN / CONTROLLED-EXECUTION BOUNDARY / ZERO RESULT**

The revised architecture, numerical preregistration and zero-result implementation are frozen. This directory now also contains the hash-bound controlled-execution interface, result schema and exactly-once runner. **No historical 0048 scientific execution has occurred.**

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

## Frozen implementation

`engine.py` mechanically implements the preregistered mathematics. It is unchanged by the controlled-run stage and remains bound by git blob SHA in `RUN_INTERFACE.json`.

Historical input is accepted only through the immutable 0047 market-evidence wrapper and must match payload SHA256:

`d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`

The evidence itself is DEVELOPMENT history already exposed to the research program. It is not independent OOS.

## Controlled-execution boundary

The controlled-run stage adds only:

- `CONTROLLED_EXECUTION_BOUNDARY.json`;
- `RUN_INTERFACE.json`;
- `RESULT_SCHEMA.json`;
- `run_once.py`;
- `test_run_interface_contract.py`;
- stage updates to the existing contract tests and operating documentation.

It does **not** create or authorize a historical result on this branch.

### Hash binding

Execution requires an explicit `--expected-head-sha` and fails closed unless the current git HEAD matches exactly.

The runner additionally verifies frozen git blob identities for:

- `PREREGISTRATION.json`;
- `DATASET_DECLARATION.json`;
- `IMPLEMENTATION_BOUNDARY.json`;
- `engine.py`;
- the immutable 0047 `MARKET_EVIDENCE.json`.

The market wrapper must also carry the exact frozen payload SHA256 above.

### Exactly-once semantics

`preflight` is repeatable and has zero scientific result authority. It verifies the exact execution head, immutable blobs, market evidence identity and absence of runtime artifacts without fitting the registered historical candidate.

`evaluate` is different. Immediately before registered-history model evaluation begins it create-only writes:

`RUN_ATTEMPT.marker`

Once that marker exists, **a second historical model computation under 0048 is forbidden**, even if the process later crashes.

On a successful valid execution, the runner create-only writes:

1. `PRIMARY_RESULT.json`;
2. `RESULT_SUMMARY.json`;
3. `EXECUTION.json`;
4. `RUN_ONCE.marker` last.

`RUN_ONCE.marker` is the final commit authority for the completed scientific execution. A valid result then closes 0048 to same-ID rerun, retuning and rescue regardless of PASS, FAIL or INCONCLUSIVE classification.

### Interruption recovery

Recovery is deliberately narrow.

If `RUN_ATTEMPT.marker` exists and the complete result + summary + execution bundle already exists but `RUN_ONCE.marker` is missing, `recover-marker` may verify all stored hashes and create the final marker **without calling the model again**.

If the bundle is partial or hash-inconsistent, there is no automatic same-ID retry path. That state must be handled as an interrupted/invalid execution under governance; the runner cannot silently recompute.

## Frozen result schema

`RESULT_SCHEMA.json` freezes the allowed result classifications and required result structure before any 0048 historical output exists.

Possible formal classifications remain:

- `INVALID_EXECUTION`;
- `MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT`;
- `MEASUREMENT_INCONCLUSIVE_CALIBRATION_UNIDENTIFIABLE`;
- `FAIL_NO_INCREMENTAL_DYNAMIC_LEADERSHIP`;
- `FAIL_NO_ROBUST_DYNAMIC_LEADERSHIP`;
- `PASS_LEADERSHIP_INFORMATION_NO_CONCENTRATION_HANDOFF`;
- `PASS_ONE_SIDED_LEADERSHIP_NO_FULL_ROUTER`;
- `PASS_LEADERSHIP_INFORMATION_CONCENTRATION_HANDOFF_ELIGIBLE`.

A leadership-information PASS does not require the confidence breakpoint to pass. Failure of the HIGH translation does not erase valid continuous leadership information.

The primary result stores the aligned formal evaluation rows and a canonical SHA256 digest of those rows so later closeout can audit exactly what observations entered the frozen gates.

Beta-calibration and isotonic diagnostics have zero selection/rescue authority. The frozen engine does not expose a separate causal diagnostic implementation for them; the result schema therefore requires their availability status to be reported rather than permitting a post-hoc replacement implementation during execution.

## Pre-result artifact state

Before the exactly-once historical execution, the following runtime files must remain absent:

- `PRIMARY_RESULT.json`;
- `RESULT_SUMMARY.json`;
- `EXECUTION.json`;
- `RUN_ATTEMPT.marker`;
- `RUN_ONCE.marker`;
- `RESULT.md`;
- any portfolio runner or portfolio result.

The controlled-run branch must merge with `actual_variants_evaluated = 0` and `result_status = PREREGISTERED_NOT_RUN` unchanged.

## What remains forbidden

0048 still cannot test or change:

- 60/80/90/100 concentration weights;
- CAGR, Sharpe, Calmar or MDD portfolio economics;
- Beta-to-BTC shelter timing;
- BTC-to-cash cycle exit;
- CORE4 or broader state thresholds;
- BNB/UNI/AAVE or any universe expansion;
- canonical BRRK;
- Phase 6;
- leverage/shorting;
- signing/order submission/production authority.

## Exact next step after this boundary merges green

On the exact merged controlled-run SHA:

1. run `preflight`;
2. verify it reports `PREFLIGHT_PASS_ZERO_RESULT`;
3. run `evaluate` exactly once;
4. preserve the resulting immutable artifacts and close out 0048 without same-ID rescue.

No historical 0048 evaluation is permitted on this boundary PR itself.
