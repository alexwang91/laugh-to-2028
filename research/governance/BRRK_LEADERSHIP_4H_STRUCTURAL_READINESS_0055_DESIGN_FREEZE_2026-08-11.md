# BRRK-LEADERSHIP-4H-STRUCTURAL-READINESS-0055 — DESIGN FREEZE

Date: 2026-08-11  
Status: **DESIGN FROZEN / NUMERICAL PREREG NOT YET FROZEN / NOT IMPLEMENTED / NOT RUN**

## 1. Research identity

Research ID: `BRRK-LEADERSHIP-4H-STRUCTURAL-READINESS-0055`  
Family: `BRRK_DYNAMIC_LEADERSHIP_ROUTER`  
Purpose: representation / estimator-readiness methodology only.

0055 is a result-informed follow-up to immutable 0054. 0054 established that the exact frozen 7-feature 4h dynamic estimator reached the 672-observation HAC admissibility floor and remained numerically identified, but never satisfied the frozen training probability-precision gate. The best observed P90 probability interval width was 0.6543462452 versus the frozen 0.10 threshold; the best observed maximum width was 0.7395819839 versus 0.20. No 0054 training refit passed, so calibration and reserved-support stages were not eligible.

0055 therefore does **not** loosen 0054's thresholds, change the HAC lag, choose a convenient fixed burn-in, or inspect post-2022 ETH/SOL targets. It asks whether a **single prospectively fixed lower-dimensional economic representation** can reduce estimator variance enough to satisfy the same readiness rules.

## 2. Scientific question

> If the seven 4h ETH/SOL relative-state features are compressed ex ante into one fixed three-dimensional structural representation that preserves the economic content of trend level, trend age and state support, can the same 0054 overlap-aware estimator-precision methodology establish training and calibration readiness without reading post-2022 leadership targets?

This is a methodology / representation question, not an alpha test.

## 3. Explicit non-questions

0055 does **not** test:

- whether ETH or SOL is forecastable;
- whether the 3D model beats the 7D model in NLL, Brier, AUC or any predictive metric;
- whether a 2D, 4D, PCA, Lasso, elastic-net, tree, neural or alternative feature representation is better;
- confidence breakpoints, HIGH states or concentration weights;
- portfolio CAGR, MDD, Sharpe, Sortino, Calmar or terminal wealth;
- Beta-to-BTC, BTC-to-cash or integrated-router economics;
- production, signing or order-submission rules.

No predictive-performance metric and no post-2022 leadership target may have selection authority under 0055.

## 4. Frozen upstream evidence

0055 may later reuse, but not replace, the immutable Binance Spot BTC/ETH/SOL 4h payload inherited through 0053/0054:

- common interval: 2020-08-11 04:00 UTC through 2026-08-02 20:00 UTC;
- payload SHA256: `471b54991ae648b79433285f073ea7bc813663319b6e2389c1682dad1a319135`.

Immutable upstream results:

- 0048: `MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED`;
- 0053: `FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT / CLOSED`;
- 0054: `FAIL_4H_NATIVE_TRAINING_PRECISION_NOT_ESTABLISHED / CLOSED`.

0055 cannot rerun, retune, relabel or rescue 0048, 0053 or 0054.

## 5. Design principle — change exactly one scientific dimension

The only substantive scientific change from 0054 is:

`7 free dynamic coefficients -> 3 free dynamic coefficients`

Everything else is inherited unless the later numerical preregistration must state an implementation detail explicitly:

- same 4h clock;
- same BTC eligibility semantics;
- same ETH/SOL target definition and horizons;
- same expanding matured-label prevalence prior;
- same no-fitted-intercept ridge logistic dynamic component;
- same ridge lambda = 1;
- same 168-bar refit grid;
- same 336-bar maximum target maturity;
- same Bartlett HAC lag 335;
- same numerical floor 672;
- same 0.10 P90 / 0.20 maximum training probability-width tolerances;
- same three-consecutive-refit training readiness rule;
- same temperature-calibration family and 0.10 calibration-width tolerance;
- same 2022-12-31 target firewall;
- same label-blind 2023+ reserved-support rule;
- same 336-ordered-eligible-row dependence block and 12-block support requirement.

If 0055 fails, the same ID may not add dimensions, change weights, relax thresholds or switch inferential units.

## 6. Frozen three-dimensional structural representation

0055 does not estimate, optimize or select the compression map. It is fixed before any 0055 numerical output.

Start from the exact 0054 bounded relative-state features:

`K1, K2, K3, K4, Persistence360, Position720, Participation`.

### 6.1 Structural dimension 1 — TrendLevel

Define:

`TrendLevel = (K1 + K2 + K3 + K4) / 4`.

Interpretation: overall SOL-vs-ETH relative trend strength averaged across the four non-overlapping age buckets. This is the low-frequency level component of the age profile.

The equal weights are governance-fixed and data-independent. No alternative weighting is evaluated.

### 6.2 Structural dimension 2 — TrendAge

Define the fixed zero-sum age contrast:

`TrendAge = (3*K1 + K2 - K3 - 3*K4) / 8`.

Properties:

- coefficient sum = 0, so the contrast is orthogonal to a constant level across the four age buckets;
- L1 coefficient norm = 1, so bounded `Kj in [-1,1]` implies `TrendAge in [-1,1]`;
- positive values mean relative strength is concentrated more in recent than stale buckets;
- negative values mean relative strength is concentrated more in older buckets or recent relative trend has deteriorated.

The integer contrast `[3, 1, -1, -3] / 8` is frozen because it is a simple ordered-age contrast with no fitted degree of freedom. No midpoint-fitted, exponential-decay or target-informed alternative is allowed under 0055.

### 6.3 Structural dimension 3 — StateSupport

Define:

`StateSupport = (Persistence360 + Position720 + Participation) / 3`.

Interpretation: equal-weight structural support behind the current relative leadership state:

- `Persistence360`: breadth/consistency of relative-return signs;
- `Position720`: current SOL/ETH relative price position within its recent range;
- `Participation`: relative quote-volume activity acceleration.

All three inputs are already bounded and antisymmetric; equal weighting keeps the composite bounded and introduces no fitted weight.

### 6.4 Final candidate representation

The sole 0055 dynamic feature vector is:

`X_struct = [TrendLevel, TrendAge, StateSupport]`.

There is exactly **one** representation candidate.

No 2D ablation, no separate 4D representation, no PCA, no supervised projection, no factor rotation, no coefficient-based pruning and no feature-selection path may be evaluated under 0055.

## 7. Antisymmetry / economic identity

Under an ETH/SOL asset swap, each inherited relative feature changes sign. Therefore:

`X_struct -> -X_struct`.

The compression does not introduce an ETH/SOL identity dummy, fitted intercept or asymmetric special case. The Laplace prevalence prior remains a separate historical base-rate component exactly as in 0054; 0055 measures uncertainty of the three-dimensional dynamic component around that prior.

## 8. Development / reserved target firewall

0055 preserves the 0054 firewall exactly.

A target label may be used only if the **entire maximum 336-bar future target path ends by 2022-12-31 20:00 UTC**.

Origins from 2023-01-01 00:00 UTC onward are target-firewalled. Under 0055 they may be inspected only for label-blind:

- feature validity;
- BTC eligibility;
- timestamps;
- full future-maturity availability;
- ordered eligible support counts/blocks after readiness activation.

No 2023+ `Y`, realized margin `M`, winner identity or predictive score may be read.

This firewall is a mechanism-study holdout against 0055 tuning, not a claim of independent OOS history.

## 9. Training estimator family

The later numerical preregistration must retain the 0054 model family with only the feature dimension changed:

- matured-label prevalence `pi = (N_SOL + 1) / (N_SOL + N_ETH + 2)`;
- dynamic model `p_raw = sigmoid(logit(pi) + beta' X_struct)`;
- no fitted intercept;
- ridge lambda = 1;
- expanding training set;
- target tie excluded exactly as in 0054;
- refit every 168 4h bars on the frozen refit grid.

`beta` has dimension 3.

0055 may estimate `beta` only to measure training precision/readiness. Predictive scoring is forbidden.

## 10. Serial-dependence treatment

0055 inherits 0054's dependence assumptions rather than re-estimating them from the new representation.

Primary long-run covariance:

- Bartlett kernel;
- fixed lag `L_HAC = 335` ordered eligible origins;
- numerical admissibility floor `N_HAC_FLOOR = 672` matured eligible observations.

The fixed 335 lag remains tied to the already frozen 336-bar maximum target-overlap scale. The 672 floor remains an admissibility floor, not a readiness threshold.

The later implementation must fail closed on non-finite covariance, invalid dimensions, invalid Hessian/curvature, failed solve or numerical nonconvergence.

## 11. Training-readiness precision gate

Let `V_beta,r` be the same 0054 penalized sandwich covariance, now for the 3D dynamic component.

### 11.1 Frozen 3D canonical probe library

Because the dynamic component is now three-dimensional, freeze the data-independent probe library as:

`Q3 = {0} union {+0.5 e_j, -0.5 e_j, +1.0 e_j, -1.0 e_j for j=1..3}`.

There are exactly 13 probes.

At probe `q`, centered dynamic probability is:

`p_dyn(q) = sigmoid(beta' q)`.

Use the delta method and `V_beta,r` to obtain the two-sided 95% probability interval width for every probe.

### 11.2 Frozen tolerances

A refit is `TRAINING_PRECISION_PASS` iff all hold:

1. matured eligible methodology-prefix observations >= 672;
2. all estimator/HAC calculations are finite and numerically valid;
3. P90 of the 13 probe widths <= 0.10;
4. maximum of the 13 probe widths <= 0.20.

Training readiness requires three consecutive passing 168-bar refits.

The probability-width thresholds are copied unchanged from 0054. Fewer probes do not authorize looser or tighter tolerances.

The later numerical preregistration must freeze the exact deterministic P90 quantile convention before execution.

## 12. Shadow calibration

Only if training readiness passes may 0055 begin shadow raw forecasts.

Shadow/calibration logic is inherited from 0054:

- raw forecasts emitted causally before outcomes exist;
- each forecast enters the calibration pool only after 336-bar maturity;
- all usable calibration outcomes remain subject to the 2022-12-31 target-path firewall;
- prior-preserving calibration `p_cal = sigmoid(logit(pi) + gamma*eta)` with `eta=beta'X_struct`, `gamma>=0`;
- same finite-stable-minimizer semantics;
- same Bartlett HAC lag 335 for scalar calibration scores;
- same numerical floor 672 matured shadow pairs;
- same calibration probe grid `{-2,-1,-0.5,-0.2,0.2,0.5,1,2}`;
- maximum 95% probability width <= 0.10;
- three consecutive passing 168-bar refits required.

If training readiness fails, calibration must not be evaluated.

## 13. Reserved-suffix support

Only if both training and calibration readiness pass may 0055 count prospective post-2022 support.

Reserved support starts at 2023-01-01 00:00 UTC or later if the frozen readiness activation implies a later start.

Count only label-blind feature-valid, BTC-eligible origins with complete 336-bar future availability by the frozen payload end.

Blocks are sequential ordered eligible origins of length 336. Require at least 12 complete blocks.

No reserved-suffix target value may be inspected during this step.

## 14. Primary success/failure taxonomy

### PASS

`PASS_4H_STRUCTURAL_3D_READINESS_ELIGIBLE_FOR_NEW_PREDICTIVE_STUDY`

requires all of:

1. three-consecutive-refit training readiness on methodology-prefix labels;
2. three-consecutive-refit calibration readiness on matured methodology-prefix shadow pairs;
3. at least 12 complete 336-row label-blind reserved-support blocks;
4. zero post-2022 target exposure;
5. all numerical/data/governance integrity checks pass.

A PASS establishes only that the fixed 3D estimator family is sufficiently precise and support-feasible for a **new separately preregistered predictive study**. It does not establish leadership alpha and does not authorize concentration.

### FAIL — training precision

`FAIL_4H_STRUCTURAL_3D_TRAINING_PRECISION_NOT_ESTABLISHED`

if three consecutive training-precision passes are never achieved.

### FAIL — calibration precision

`FAIL_4H_STRUCTURAL_3D_CALIBRATION_PRECISION_NOT_ESTABLISHED`

if training readiness passes but three consecutive calibration-precision passes are never achieved.

### FAIL — future support

`FAIL_4H_STRUCTURAL_3D_METHOD_READY_BUT_RESERVED_SUPPORT_INSUFFICIENT`

if training and calibration readiness pass but fewer than 12 complete reserved-support blocks remain.

### INVALID / INCONCLUSIVE

Any post-2022 target inspection, payload/hash mismatch, preregistration drift, result-before-attempt persistence breach or numerical-integrity violation fails closed under a preregistered invalid/inconclusive status rather than becoming a scientific PASS/FAIL.

## 15. Outputs permitted under 0055

The unique later methodology measurement may report only:

- training precision records and readiness timestamp/count;
- 3D probe probability interval widths;
- HAC/Hessian numerical diagnostics;
- shadow/calibration precision records if eligible;
- calibration readiness timestamp/count if eligible;
- label-blind reserved support counts/blocks if eligible;
- final methodology classification;
- descriptive comparison with immutable 0054 precision widths only if explicitly marked zero-selection-authority.

Forbidden outputs include NLL, Brier, AUC, balanced accuracy, directional precision/recall, realized-margin statistics, confidence breakpoints and all portfolio economics.

## 16. Governance sequence

0055 must follow:

`design -> numerical/data preregistration -> implementation-only -> controlled exactly-once methodology measurement -> immutable closeout`.

Before the unique measurement:

- payload reuse must be hash-bound;
- all three composite formulas and estimator mathematics must be frozen;
- the 2022 target firewall must be implementation-tested;
- the 2023+ target path must be inaccessible to 0055 measurement code;
- attempt marker must be durably persisted before any real methodology output;
- same-ID rerun, retuning and rescue must be false after a valid measurement.

## 17. Forbidden result-informed rescue

After any 0055 numerical output is observed, the same ID may not:

- change `[1,1,1,1]/4` TrendLevel weights;
- change `[3,1,-1,-3]/8` TrendAge weights;
- change the equal one-third StateSupport weights;
- replace the 3D representation with 2D, 4D, PCA, Lasso or another projection;
- change ridge lambda 1;
- change HAC kernel/lag 335 or numerical floor 672;
- change the 0.10/0.20 training widths, 0.10 calibration width or three-refit rule;
- select a fixed burn-in from observed 0055 widths;
- read post-2022 target values;
- add predictive/economic metrics;
- rerun or rescue 0048, 0053 or 0054.

Any such result-informed change requires a new research ID.

## 18. Interpretation discipline

Possible interpretations are deliberately narrow:

- **PASS**: the fixed structural 3D representation is estimator-ready and leaves enough label-blind reserved support for a later predictive study.
- **Training FAIL**: reducing 7 free dynamic coefficients to these 3 fixed structural dimensions is not sufficient to meet the prospectively frozen overlap-aware precision requirement. This does not prove all ETH/SOL leadership mechanisms impossible.
- **Calibration FAIL**: coefficient precision is adequate but the one-parameter probability scaling remains insufficiently precise on the protected methodology prefix.
- **Reserved-support FAIL**: the method is estimable but the preserved post-2022 suffix is still too small under dependence-aware support accounting.

No result may be translated into portfolio allocation authority under 0055.

## 19. Production and canonical no-drift

0055 cannot modify:

- canonical BRRK-0011;
- Phase 6 state or observation policy;
- production gross cap;
- authorized production components;
- signing authority;
- order-submission authority.

Required invariants remain:

`production_authorized=false`  
`production_authorized_components=[]`  
`signature_authorized=false`  
`order_submission_authorized=false`.

## 20. Exact next step

After this design freeze is merged with `DRIFT_0`, create a separate numerical/data preregistration for 0055. The preregistration must mechanically specify the inherited 4h target/eligibility equations, exact 3D compression, exact HAC/probe/quantile calculations, dataset/hash firewall, result taxonomy, variant budget = 1 and exactly-once execution policy.

No real 0055 numerical output may be generated before that preregistration is merged.