# BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-0066 — DESIGN FREEZE

Date: 2026-08-14
Stage: DESIGN ONLY / NO 0066 HISTORICAL MEASUREMENT
Baseline main: `91239d49f3faf328d59e4e3bcad2fe00bdcd1794`

## 1. Scientific question

Replace one-off return forecasting with an event-first research program:

1. abstract BTC and SOL price paths into objectively defined decline and sideways episodes;
2. grade episodes primarily by duration and secondarily by path severity;
3. ask whether the already frozen 0062 indicator universe contains information that an episode will begin within the next 1/3/5/10/20 sessions;
4. use a prospectively frozen validation-only selection rule to decide which indicators/models are allowed into multiple economic gross-controller backtests;
5. compare all controllers in one exactly-once historical tournament against the frozen 0064 passive-cash benchmark.

The event labels are constructed from price only. Indicator values may not alter event definitions, thresholds, duration buckets, onset extraction or support rules.

## 2. Evidence status

This is DEVELOPMENT history and is not independent OOS. 0065 is closed. The fact that 0065 descriptively favored low-order quadratic structure is RESULT_INFORMED and is acknowledged only as motivation for including one prespecified quadratic classifier among several architectures; it receives no privileged selection rule.

No same-ID reuse of 0065 results, interaction pruning or 0065 retuning is allowed.

## 3. Frozen data

Use only the already frozen 0062 market evidence panel:

- `research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json`
- git blob `64ebf5c6deaf3f34dbeac715378f196ff0f4fafe`
- payload SHA256 `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`
- slice `BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1`
- 2020-08-11 through 2026-08-02; 2183 daily rows
- BTC / ETH / SOL OHLCV fields already admitted by 0062
- loader `research.brrk_beta_handoff_0047.engine.frames_from_market_evidence`
- loader blob `059b55961e279dab41ba29b5b017de0922e4f33c`
- 0062 feature engine blob pinned at preregistration
- network fetch forbidden; replacement data forbidden

Event outcomes use BTC and SOL close only. Predictors may use the complete frozen 0062 Tier-A atlas: 185 cells and 17 family scores. ETH remains predictor context only, not an event-outcome asset.

Economic backtests use the frozen BRRK equity/weights and 0064 cash economics exactly as pinned later in preregistration. Canonical BRRK-0011 and Phase 6 remain untouched.

## 4. Price-path event abstraction

### 4.1 Multi-scale trend scan

For each asset a in {BTC,SOL}, each eligible origin t, and each future horizon

`H = [10, 15, 20, 30, 45, 60, 90, 120, 180, 240]` sessions,

fit OLS on the future log-close path:

`log(C[t+j]) = alpha + beta*j + epsilon_j`, j=0..H.

Record the slope t-statistic `T_H`, terminal log return `R_H`, path maximum adverse excursion from t, and path log-range. The t-statistic is a standardized path-shape score only; it is NOT interpreted as a classical IID significance test.

Past-only scale at origin t is `sigma60`: standard deviation of daily log returns over the preceding 60 sessions, ddof=1, minimum 30 observations. No future volatility enters the threshold.

### 4.2 Decline candidate

Choose `H* = argmax_H |T_H|`, breaking ties toward the shorter horizon.

A DOWN candidate exists only if all are true:

- `T_H* <= -2.5`;
- `R_H* <= -1.0 * sigma60 * sqrt(H*)`;
- maximum adverse excursion magnitude is at least `1.5 * sigma60 * sqrt(H*)`.

Duration grade is determined only by H*:

- D1_SHORT: 10/15/20
- D2_MEDIUM: 30/45/60
- D3_LONG: 90/120
- D4_SECULAR: 180/240

Severity subgrade uses normalized maximum adverse excursion `Z_MAE = MAE/(sigma60*sqrt(H*))`:

- S1: 1.5 <= Z_MAE < 2.5
- S2: 2.5 <= Z_MAE < 4.0
- S3: Z_MAE >= 4.0

### 4.3 Sideways candidate

For each H, a sideways window qualifies if all are true:

- `|T_H| <= 1.25`;
- `|R_H| <= 0.50 * sigma60 * sqrt(H)`;
- future log-close range <= `1.75 * sigma60 * sqrt(H)`.

If multiple horizons qualify, choose the LONGEST qualifying H. Duration grades use the same 10/15/20, 30/45/60, 90/120, 180/240 buckets and labels S1_SHORT, S2_MEDIUM, S3_LONG, S4_SECULAR.

DOWN takes precedence over SIDEWAYS at the same origin. Otherwise the origin is OTHER.

### 4.4 Unique episode onset extraction and risk set

For each asset and event type, a candidate run is contiguous candidate dates of the same duration grade. The episode onset is the first date of the run. After an onset, later same-type candidate onsets are suppressed for `ceil(H*/2)` sessions. A later candidate with a strictly LONGER duration grade may start a new hierarchical episode only after 10 sessions.

Dates inside an already-started event's suppression interval are OUTSIDE the classifier risk set; they are not treated as clean negative examples for predicting a new onset.

This produces an immutable price-only event atlas with onset date, asset, type, duration grade, H*, severity, realized path statistics and episode support counts.

No indicator is read when constructing this atlas.

## 5. Prediction targets and early-warning horizons

For each asset separately define:

- T1_ANY_DOWN: D1-D4
- T2_MAJOR_DOWN: D2-D4 OR severity S2/S3
- T3_ANY_SIDEWAYS: S1-S4
- T4_LONG_SIDEWAYS: S2-S4

Early-warning horizons are exactly `L=[1,3,5,10,20]` sessions.

For an at-risk prediction date t, binary target `Y_L[t]=1` iff at least one qualifying target onset occurs in the strictly future window `(t, t+L]`; otherwise `Y_L[t]=0`. Therefore a 10D model means "an onset will occur within the next 10 sessions", not "the onset occurs exactly 10 sessions later".

The same unique onset may contribute positive labels to several nested warning horizons; multiplicity/dependence handling therefore treats the five horizons as correlated hypotheses rather than independent samples.

This yields 2 assets x 4 targets x 5 warning horizons = 40 frozen event/horizon tracks.

Support gate per track counts UNIQUE underlying onsets, not positive prediction-date rows:

- at least 8 TRAIN+VALIDATION unique positive onsets;
- at least 3 FINAL-EVALUATION unique positive onsets;
- otherwise classification is `LOW_SUPPORT_DESCRIPTIVE_ONLY` and no confirmatory predictive claim is allowed for that track.

D4/S4 episodes are always reported in the atlas even if their dedicated predictive support is insufficient.

## 6. Frozen temporal protocol

Because labels may use up to 240 future sessions, every fit may use only labels whose complete 240-session event-construction window has ended strictly before that fit date.

- Warm-up / expanding training: earliest common 0062 feature support onward.
- VALIDATION prediction dates: 2023-01-01 through 2023-12-31.
- FINAL event-prediction evaluation dates: 2024-01-01 through the last origin whose 240-session event-construction window is fully observed in the frozen panel.
- ECONOMIC evaluation dates: 2024-01-01 through 2026-08-02; post-label-maturity tail is allowed for economics because live-style probability generation requires no future event label.
- refit cadence: every 20 sessions.
- forecast made after close t may alter only portfolio return row t+1.

All preprocessing/scaling/orientation must be fit-sample only.

## 7. Indicator early-warning atlas

Evaluate every frozen 0062 signal unit:

- 185 raw cells
- 17 family scores
- total 202 signal units

for every supported asset/target/warning-horizon track.

For each signal:

- freeze orientation from TRAIN only using the sign of train point-biserial correlation with the binary warning target;
- on VALIDATION and FINAL EVALUATION report ROC-AUC, PR-AUC, prevalence, PR-AUC lift over prevalence, Brier score, and four chronological block metrics;
- no evaluation-period sign flipping;
- multiplicity correction is simultaneous across all reported signal/track hypotheses.

The atlas is descriptive/selection evidence; no post-evaluation indicator selection is permitted.

## 8. Frozen predictor architecture tournament

Eight architecture classes are prospectively compared:

P01 `FAMILY_RIDGE_LOGIT` — 17 family scores, L2 logistic.

P02 `RAW_ELASTIC_NET_LOGIT` — all 185 cells, elastic-net logistic.

P03 `VALIDATION_SCREENED_SIGNAL_LOGIT` — deterministic validation-only top-signal model. Per asset/target/horizon, select at most 12 units by validation PR-AUC lift, requiring positive lift in >=3/4 validation blocks; no more than two selected units per 0062 family; ties by preregistered signal ID. Final evaluation may not change the selected set.

P04 `PCR_LOGIT` — PCA on 185 cells followed by L2 logistic.

P05 `THEORY_QUADRATIC_LOGIT` — 17 family linear terms + 17 squares + the same 10 prespecified theory interactions admitted in 0065, with strong L2 shrinkage. This method is explicitly RESULT_INFORMED but not privileged.

P06 `SHALLOW_GBDT_CLASSIFIER` — bounded depth 1/2 gradient boosting.

P07 `DISCRETE_TIME_HAZARD_LOGIT` — pooled nested-horizon event-onset hazard model using family scores plus frozen warning-horizon indicators, causal by construction.

P08 `STACKED_PROBABILITY_ENSEMBLE` — nonnegative convex validation-only stack of P01-P07 probabilities; no final-evaluation reweighting.

All hyperparameter grids and exact solver settings must be numerically frozen in PREREGISTRATION before implementation.

## 9. Validation-only selection rule

For each asset/target:

1. each architecture chooses hyperparameters on VALIDATION only;
2. choose a preferred warning horizon from [1,3,5,10,20] by highest validation PR-AUC lift, tie-breaking toward the LONGER horizon;
3. architecture ranking uses validation PR-AUC lift, then ROC-AUC, then lower Brier;
4. final event evaluation never changes architecture, warning horizon, signal set, calibration or thresholds.

A predictive architecture/target track is confirmatory only if FINAL evaluation satisfies all:

- G0 data / event / temporal identity;
- G1 support gate;
- G2 ROC-AUC > 0.50 and PR-AUC lift > 0;
- G3 >=3/4 chronological blocks have ROC-AUC >0.50 and PR-AUC above prevalence;
- G4 preferred warning horizon is >=5 sessions OR an adjacent pair among {3,5},{5,10},{10,20} both satisfy G2;
- G5 simultaneous dependence-aware bootstrap LCB for PR-AUC lift is strictly >0.

## 10. Economic controller tournament

Use only validation-frozen model outputs. No controller may inspect final CAGR to choose a predictor.

Frozen controllers:

C01 `BTC_ANY_DOWN_5D`
C02 `SOL_ANY_DOWN_5D`
C03 `MAX_BTC_SOL_ANY_DOWN_5D`
C04 `BTC_MAJOR_DOWN_10D`
C05 `MAX_BTC_SOL_MAJOR_DOWN_10D`
C06 `MULTILEAD_DOWN_BLEND_3_5_10`
C07 `DOWN_PLUS_SIDEWAYS`
C08 `STACKED_EVENT_RISK`

For C01-C07, the underlying predictor architecture for each required target is the single validation winner frozen by Section 9. C08 uses P08 directly.

Probability-to-gross map is frozen by validation probability quantiles, not final outcomes:

- below validation 90th percentile risk: outer multiplier g=1.00
- >=90th percentile: g=0.50 for DOWN risk; g=0.75 for SIDEWAYS-only risk
- >=97.5th percentile DOWN risk: g=0.25
- if multiple rules fire, take the minimum g
- no leverage, no shorting, no smoothing

C06 uses the maximum standardized risk percentile across 3/5/10-session warning probabilities. C03/C05 use the maximum risk percentile across BTC and SOL. C07 applies DOWN first and SIDEWAYS only if no stronger DOWN rule fires.

Benchmark economics are the frozen 0064 primary passive-cash system. Outer overlay transaction cost = 10 bps per unit change in outer multiplier. Forcing g=1 must reconstruct 0064 within frozen tolerance.

Economic winner gates:

- E0 identity/timing/cost contract;
- E1 terminal wealth and calendar CAGR strictly exceed 0064;
- E2 MDD noninferior to 0064;
- E3 >=3/4 chronological economic blocks have positive relative log growth;
- E4 simultaneous moving-block-bootstrap one-sided LCB of relative daily log growth strictly >0 across all valid controllers;
- E5 dependence / cost / no-lookahead checks pass.

## 11. Multiplicity and overfit diagnostics

Numerical preregistration must freeze:

- aligned non-circular moving-block bootstrap length 60;
- 4000 replicates;
- deterministic seed 660066;
- Type-7 95th percentile simultaneous correction across confirmatory predictive tracks and separately across economic controllers;
- 8-slice CSCV / PBO diagnostic across the eight economic controllers where support permits;
- declared trial budget includes every hyperparameter configuration, every final predictive architecture and every final economic controller. Indicator-atlas cells are separately counted as hypothesis cells and receive their own simultaneous correction.

## 12. Classification

Primary research classifications:

- `PASS_EVENT_EARLY_WARNING_AND_ECONOMIC_CONTROLLER` if >=1 predictive track passes G0-G5 and >=1 controller passes E0-E5;
- `PASS_EVENT_EARLY_WARNING_ONLY` if >=1 predictive track passes G0-G5 but no controller passes E0-E5;
- `FAIL_NO_ROBUST_EVENT_EARLY_WARNING` if supported tracks exist but none pass G0-G5;
- `FAIL_NO_ROBUST_EVENT_CONTROLLER` if predictive evidence passes but no controller passes economics;
- `MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_EVENT_SUPPORT` if all confirmatory target families fail G1;
- contract/data/implementation/persistence/exactly-once violation => `INVALID_EXECUTION`.

## 13. Governance / exactly once

Required order:

1. DESIGN
2. DESIGN merge
3. owner-first numerical/data PREREGISTRATION
4. prereg merge
5. IMPLEMENTATION-ONLY with synthetic/artificial data only
6. implementation merge
7. CONTROLLED-EXECUTION BOUNDARY
8. boundary merge
9. exactly one historical execution attempt
10. immutable CLOSEOUT

Once `RUN_ATTEMPT.marker` is durably persisted, same-ID rerun, retune, rescue, event-threshold change, indicator pruning, warning-horizon change, controller change or cost change is permanently forbidden.

`production_authorized=false`
`signature_authorized=false`
`order_submission_authorized=false`

Canonical BRRK-0011, closed 0064, closed 0065 and Phase 6 receive no modification or promotion from this study.

## 14. Design-stage prohibition

At DESIGN stage:

- do not compute the 0066 event atlas;
- do not inspect 0066 indicator/event associations;
- do not compute any 0066 classifier metric;
- do not compute any 0066 controller CAGR/NAV/MDD;
- historical actual variants evaluated = 0.
