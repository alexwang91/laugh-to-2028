# BRRK-LEADERSHIP-4H-NATIVE-READINESS-0054 — DESIGN FREEZE

Date: 2026-08-11  
Status: **DESIGN FROZEN / NUMERICAL PREREG NOT YET FROZEN / NOT IMPLEMENTED / NOT RUN**

## 1. Research identity

Research ID: `BRRK-LEADERSHIP-4H-NATIVE-READINESS-0054`  
Family: `BRRK_DYNAMIC_LEADERSHIP_ROUTER`  
Purpose: methodology / support-readiness only.

0054 is a result-informed follow-up to the immutable 0053 support-feasibility closeout. 0053 established that changing daily bars to 4h bars while translating every support clock by six produced almost exactly six times as many formal rows but no increase in 56-day-equivalent dependence blocks: Track A remained 4 blocks. Track C showed that the two calendar-equivalent 2190-origin burn-ins were the dominant support bottleneck, but Track C was diagnostic-only and cannot be promoted into a predictive specification.

0054 therefore does **not** ask whether 365, 672, 1344, 2190 or any other fixed row count has the best predictive performance. It asks whether a **model-specific causal readiness rule based on estimator precision** can replace the fixed calendar-equivalent burn-ins without consulting downstream predictive performance.

## 2. Scientific question

> For the fixed low-dimensional 4h ETH/SOL leadership estimator family inherited from 0048, can training readiness and shadow-calibration readiness be determined causally from parameter/prediction precision under serial dependence, rather than by a fixed 365-day-equivalent observation count, while preserving a reserved post-2022 suffix for a later predictive study?

This is a methodology question, not an alpha test.

## 3. Explicit non-questions

0054 does **not** test:

- whether ETH or SOL is forecastable;
- whether the 7-feature candidate beats B0/B1/B2/B3;
- NLL, Brier, AUC, balanced accuracy, precision/recall or realized leadership margin;
- confidence breakpoints or HIGH states;
- 60/80/90/100% concentration;
- CAGR, MDD, Sharpe, Sortino, Calmar or terminal wealth;
- Beta-to-BTC, BTC-to-cash or integrated-router economics;
- any production, signing or order-submission rule.

No predictive-performance metric may have selection authority under 0054.

## 4. Frozen upstream evidence

0054 may later reuse, but not replace, the immutable 0053 Binance Spot BTC/ETH/SOL 4h payload:

- common interval: 2020-08-11 04:00 UTC through 2026-08-02 20:00 UTC;
- common bars: 13,097;
- payload SHA256: `471b54991ae648b79433285f073ea7bc813663319b6e2389c1682dad1a319135`.

0053 is permanently closed as `FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT`. 0054 cannot rerun, retune, relabel or rescue 0053 or 0048.

## 5. Model family whose readiness is being studied

0054 is model-specific. The later numerical preregistration must mechanically translate the frozen 0048 candidate to the 4h clock without adding features or hyperparameter search.

The intended estimator family is:

- 7 bounded antisymmetric ETH/SOL relative-state features: four non-overlapping momentum-age buckets, persistence, symmetric relative position and relative quote-volume participation;
- fixed no-fitted-intercept ridge logistic dynamic component with ridge lambda = 1;
- expanding Laplace-smoothed matured-label prevalence prior `pi`;
- raw probability `sigmoid(logit(pi) + beta'X)`;
- 28-calendar-day equivalent refit cadence = 168 4h bars;
- full target maturity = 56 days = 336 4h bars;
- primary symmetric prior-preserving temperature calibration `sigmoid(logit(pi) + gamma * eta)`, `eta=beta'X`, `gamma>=0`.

0054 may estimate `beta` and `gamma` only to measure estimation precision/readiness. Their predictive accuracy is forbidden to score.

## 6. Development / reserved temporal firewall

To prevent 0054 from choosing readiness rules using the same later outcomes that a subsequent predictive study would score, 0054 freezes a methodology-development prefix.

### 6.1 Methodology-development target firewall

0054 may use an ETH/SOL target label only if the **entire maximum 336-bar future target path has completed by 2022-12-31 20:00 UTC**.

Equivalently, the latest label origin usable for any 0054 fit/precision calculation is computed mechanically as:

`2022-12-31 20:00 UTC - 336*4h`.

No ETH/SOL target value, winner label, realized margin or prediction score with any portion of its future path after 2022-12-31 20:00 UTC may be read by the 0054 measurement code.

### 6.2 Reserved suffix

Origins from 2023-01-01 00:00 UTC onward are reserved against target inspection by 0054. 0054 may inspect **label-blind** feature validity, BTC eligibility, timestamps and target-maturity availability in this suffix solely to count prospective support for a later separately preregistered predictive study.

This is still DEVELOPMENT history, not independent OOS, because earlier BRRK research has exposed the broader historical period. The firewall only prevents 0054's new readiness rule from being tuned on post-2022 4h target outcomes.

## 7. Core design principle — readiness is a stopping rule, not a fixed row count

0054 rejects the following design:

> try several fixed burn-ins and keep whichever produces the nicest predictive result.

Instead, at each frozen 168-bar refit point, readiness is evaluated from estimator uncertainty only. The output is the earliest causal refit at which fixed precision criteria remain satisfied for three consecutive refits.

There is no burn-in grid and no best-N selection.

## 8. Serial-dependence treatment

The maximum target horizon is 336 4h bars. The later numerical preregistration will use a Bartlett-kernel heteroskedasticity/autocorrelation-consistent long-run covariance estimator for score contributions with fixed lag:

`L_HAC = 335 eligible-origin steps`.

This is deliberately tied to the already frozen maximum target-overlap scale; it is not selected from 0054 data.

A numerical admissibility floor is fixed prospectively:

`N_HAC_FLOOR = 2 * 336 = 672 matured eligible observations`.

This floor is **not** the readiness threshold. It only prevents a 335-lag covariance estimator from being invoked when the available sequence is shorter than twice the dependence horizon. Actual readiness additionally requires the precision gates below.

The later implementation must fail closed on non-finite covariance, non-positive required curvature, invalid dimensions or numerical nonconvergence.

## 9. Training-readiness precision gate

Let `beta_r` be the fixed-lambda ridge estimate at refit `r`, using only matured eligible methodology-prefix origins causally available by `r`.

Let `s_t = X_t (Y_t - p_t)` denote the dynamic-model score contribution and let `Omega_r` be its frozen Bartlett HAC long-run covariance estimate. Let `H_r` be the penalized observed Hessian. The sandwich covariance is:

`V_beta,r = H_r^{-1} Omega_r H_r^{-1}`.

The prevalence prior is conditioned on for this gate; 0054 is measuring precision of the 7-dimensional **dynamic component**, not creating a second burn-in gate for the simple Laplace prevalence estimator.

### 9.1 Data-independent canonical probe library

To prevent the uncertainty target from being selected from observed feature states, the probe library is frozen as:

`Q = {0} union {+0.5 e_j, -0.5 e_j, +1.0 e_j, -1.0 e_j for j=1..7}`.

There are exactly 29 probes. `e_j` is the j-th coordinate basis vector.

For probe `q`, define centered dynamic probability:

`p_dyn(q) = sigmoid(beta_r' q)`.

Use the delta method with `V_beta,r` to obtain the two-sided 95% interval width `W_beta,r(q)`.

### 9.2 Frozen training-readiness tolerances

A refit is `TRAINING_PRECISION_PASS` iff all hold:

1. matured eligible training observations >= 672;
2. all model/HAC calculations are finite and numerically valid;
3. 90th percentile of the 29 probability interval widths <= 0.10;
4. maximum of the 29 probability interval widths <= 0.20.

Training becomes **ready** only after `TRAINING_PRECISION_PASS` occurs at **three consecutive 168-bar refit points**.

The 0.10/0.20 widths are governance precision tolerances, not claims of a universal statistical theorem. They are frozen before 0054 numerical output and have zero predictive-performance selection authority.

## 10. Shadow-calibration readiness

Shadow raw forecasts begin only after training readiness has been achieved. Each shadow forecast is emitted causally before its outcome exists and can enter the calibration pool only after the full 336-bar target has matured.

At each subsequent 168-bar refit, fit the frozen prior-preserving temperature parameter `gamma>=0` on matured methodology-prefix shadow pairs only.

For shadow pair `t`, with dynamic logit `eta_t=beta'X_t`, define calibration score contribution:

`u_t = eta_t * (Y_t - p_cal,t)`.

Estimate the long-run variance of `u_t` using the same fixed Bartlett HAC lag 335. Use the calibration curvature to obtain `Var(gamma)`.

### 10.1 Data-independent calibration probe grid

Freeze dynamic logits:

`E = {-2.0, -1.0, -0.5, -0.2, +0.2, +0.5, +1.0, +2.0}`.

For each `eta` in E, define centered calibrated dynamic probability:

`p_cal_dyn(eta) = sigmoid(gamma * eta)`.

Use the delta method to obtain two-sided 95% interval width `W_gamma,r(eta)`.

### 10.2 Frozen calibration-readiness tolerances

A refit is `CALIBRATION_PRECISION_PASS` iff all hold:

1. matured eligible shadow pairs >= 672;
2. the frozen temperature fit is identified under the later preregistered numerical rules;
3. HAC/curvature calculations are finite and valid;
4. maximum 95% interval width across all eight calibration probes <= 0.10.

Calibration becomes **ready** only after `CALIBRATION_PRECISION_PASS` occurs at **three consecutive 168-bar refit points**.

A gamma boundary solution at zero is not automatically a methodology failure if it is a valid identified optimum and its uncertainty criterion passes; 0054 is testing estimability, not whether the dynamic component has positive alpha.

## 11. 0054 outputs

The unique later 0054 measurement may output only methodology/readiness quantities, including:

- earliest training-precision pass refits and final three-refit training-readiness timestamp;
- matured training count at training readiness;
- HAC/numerical diagnostics required to audit the decision;
- earliest shadow origin;
- earliest calibration-precision pass refits and final three-refit calibration-readiness timestamp;
- matured shadow-pair count at calibration readiness;
- earliest formal origin that a future study could use under the frozen readiness rule;
- label-blind prospective reserved-suffix formal-row count;
- complete 336-row reserved-suffix support blocks;
- trailing partial rows;
- final methodology classification.

0054 must not output model NLL, Brier, AUC, balanced accuracy, directional precision/recall, realized-margin correlation, confidence breakpoint, portfolio performance or economic returns.

## 12. Primary success/failure taxonomy

The numerical preregistration must preserve this hierarchy.

### PASS

`PASS_4H_NATIVE_READINESS_METHOD_ELIGIBLE_FOR_NEW_PREDICTIVE_STUDY`

requires all of:

1. training readiness is achieved using only methodology-prefix matured labels;
2. calibration readiness is achieved using only methodology-prefix matured shadow labels;
3. the reserved post-2022 suffix contains at least 12 complete 336-row eligible formal-support blocks after applying the frozen readiness activation and target-maturity rules;
4. no post-2022 ETH/SOL target outcome is inspected;
5. all governance and numerical-integrity checks pass.

This PASS authorizes only a **new separately preregistered predictive research ID**. It does not establish leadership predictability and does not authorize 0049 concentration.

### FAIL — training precision

`FAIL_4H_NATIVE_TRAINING_PRECISION_NOT_ESTABLISHED`

if the methodology prefix never achieves three consecutive training-precision passes.

### FAIL — calibration precision

`FAIL_4H_NATIVE_CALIBRATION_PRECISION_NOT_ESTABLISHED`

if training readiness is achieved but the methodology prefix never achieves three consecutive calibration-precision passes.

### FAIL — future support

`FAIL_4H_NATIVE_METHOD_READY_BUT_RESERVED_SUPPORT_INSUFFICIENT`

if both readiness stages pass but the label-blind reserved suffix has fewer than 12 complete 336-row blocks.

### INVALID / INCONCLUSIVE

Numerical/data integrity violation, forbidden target exposure, result-before-attempt persistence failure or preregistration drift must fail closed under an explicit invalid/inconclusive classification frozen before execution.

## 13. Governance protections

0054 must follow the existing program-governed sequence:

`design -> numerical/data preregistration -> implementation-only -> controlled exactly-once measurement -> immutable closeout`.

Before the unique 0054 measurement:

- reuse of the 0053 payload must be hash-bound;
- all feature/target/readiness mathematics must be frozen;
- the 2022-12-31 target firewall must be implementation-tested;
- post-2022 target columns/values must be inaccessible to the measurement path;
- attempt marker must be durably persisted before any methodology output;
- same-ID rerun, retuning and rescue must be false after a valid measurement.

## 14. Forbidden result-informed rescue

After any 0054 numerical output is observed, the same ID may not:

- change 0.10/0.20 training precision widths;
- change the calibration 0.10 width;
- change the three-consecutive-refit rule;
- change HAC lag/kernel;
- replace HAC with bootstrap as primary;
- change the 672 numerical floor;
- alter the canonical probe library or calibration grid;
- move the methodology-prefix cutoff;
- read post-2022 ETH/SOL target outcomes;
- substitute a fixed 365/672/1344/2190 count because it looks favorable;
- use predictive performance to choose any readiness parameter.

Any such result-informed method change requires a new research ID.

## 15. Interpretation boundary

A 0054 PASS means only:

> the frozen 4h candidate/calibration estimator family reached prospectively defined estimation-precision readiness early enough that a separately registered post-2022 historical-prequential predictive study has adequate label-blind dependence-aware support.

It does **not** mean the model predicts ETH/SOL leadership.

A later predictive study must freeze its own target, model, baselines, scoring and inference before it reads the reserved suffix's ETH/SOL targets.

## 16. Methodological references informing, but not numerically determining, this design

- Newey, W.K. and West, K.D. (1987), Econometrica 55(3), 703-708: positive semi-definite HAC covariance estimation.
- Riley, R.D. et al. (2019), Statistics in Medicine 38, 1276-1296: prediction-model sample size should target overfitting/precision properties rather than rely on a universal events-per-variable rule.
- Riley, R.D. et al. (2024 preprint), Fisher-information decomposition for individual prediction precision: motivates expressing adequacy through uncertainty of predicted probabilities rather than an arbitrary row count.

The exact 0054 HAC horizon, probes and 0.10/0.20 tolerances are BRRK governance choices frozen prospectively; the cited literature does not select those exact constants.

## 17. Production authority

No change:

- canonical BRRK unchanged;
- Phase 6 unchanged;
- production gross cap unchanged;
- `production_authorized_components=[]`;
- `production_authorized=false`;
- `signature_authorized=false`;
- `order_submission_authorized=false`.
