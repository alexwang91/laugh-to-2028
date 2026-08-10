# BRRK-EXHAUSTION-PULSE-0046 — Exact Design Freeze

Date: 2026-08-10
Status: **DESIGN FROZEN / NOT PREREGISTERED / NOT RUN**
Governance scope: design-only continuation of Issue #160 after immutable `BRRK-EXHAUSTION-STATE-0044` PASS and immutable `BRRK-EXHAUSTION-TRIGGER-0045` FAIL.

This document freezes the proposed mathematical architecture tightly enough for a later formal `PROGRAM_GOVERNED_V1` preregistration. It is **not** that preregistration, creates no runner or result, and does not authorize dynamic gross, portfolio economics, canonical BRRK changes, Phase-6 changes, production, signing or order submission.

## 1. Binding prior evidence

The design is explicitly result-informed and therefore is not independent OOS research.

Binding positive evidence from closed 0044:

- frozen four-axis state representation retained advance discrimination after macro-episode dependence control;
- CORE4 primary PRE14_7 cross-episode AUC = 0.750;
- S2 trend disagreement was the strongest exposed component;
- S5 volume confirmation was negative evidence and remains excluded.

Binding negative evidence from closed 0045:

- primary TRUE PRE14_7 WATCH/RISK hit = 3/9;
- primary TRUE episode hit = 2/5;
- severe TRUE PRE14_7 hit = 3/7;
- severe near-peak RISK confirmation = 2/7;
- qualifying TRUE PRE21_0 new transition onsets = 0;
- WATCH+RISK occupied about 34.38% of sessions;
- no same-ID rescue is permitted and dynamic-gross stage eligibility remains false.

The design question is therefore not whether exhaustion **level** is informative. It is whether a **new deterioration transition** can be detected prospectively without recreating a sticky high-risk state.

## 2. Dialectical design decisions

### H1 — Use `CORE4 + S2 + S3 + S4` as the four detector coordinates

**Rejected.** CORE4 is already the equal-weight mean of S1, S2, S3 and S4. A coordinate-wise sparse detector is not invariant to replacing S1 by CORE4 while retaining S2/S3/S4 separately. That basis would implicitly duplicate S2/S3/S4 information and would especially privilege S2 after 0044 already exposed S2 as the strongest axis.

**Frozen correction:** primary detector coordinates are exactly the symmetric frozen axes:

```text
S1_MOMENTUM_DECELERATION
S2_TREND_DISAGREEMENT
S3_PRICE_STRUCTURE
S4_VOL_DOWNSIDE
```

CORE4 is retained only as an immutable static benchmark. S5, breadth, correlation, new indicators and S2-only variants are excluded.

### H2 — Add a Kalman/local-linear latent-state filter before changepoint detection

**Rejected for the primary 0046 candidate.** The frozen 0044 axes are already causal low-dimensional composites built from trailing-252 causal z-scores with minimum 60 observations and clipping to `[-3,+3]`. A second smoothing layer introduces additional process/observation-noise parameters and extra detection delay before a study whose target is only 7–14 sessions ahead.

The slope-change literature allows a causal historical regression to define the pre-change trend and then detects a new slope departure on the original signal. This gives the required trend adjustment without a second latent smoother.

**Frozen correction:** no Kalman filter, state-space filter, L1 trend filter, EMA smoother, raw differencing or additional latent-state model is part of the primary candidate.

### H3 — Difference S1–S4 and run a mean-shift CUSUM

**Rejected.** Differencing converts slope changes into level changes but inflates noise. The primary detector works on the original frozen axes after causal pre-change detrending.

### H4 — Keep BOCPD as a secondary 0046 candidate

**Rejected under this ID.** BOCPD has a legitimate run-length interpretation, but including a second independently parameterized detector creates a model-tournament/rescue path after the primary result. 0046 has exactly one result-bearing candidate. BOCPD may be studied only under a later new research ID with its own preregistration and family-trial accounting.

### H5 — Tune the threshold, scale or pulse duration against TRUE_EXHAUSTION labels

**Rejected.** Threshold calibration is label-blind and is completed and hash-locked before the event taxonomy may be loaded. No outcome label controls the detector threshold, candidate age range, baseline length, subset aggregation, pulse definition or null model.

## 3. Frozen input construction

The future preregistration must recompute the exact frozen 0044 axes from the exact 0043 causal feature implementation. No 0044 result file may be edited and no feature mathematics may be changed.

For every eligible daily session `t`, define the four-dimensional state vector:

\[
S_t=(S1_t,S2_t,S3_t,S4_t)^\top.
\]

The exact 0044 construction remains binding:

- S1 = equal mean of causal-z `f1_trend_decay7`, `f1_macd_hist_decay5`;
- S2 = equal mean of causal-z `f7_slow_fast_disagreement`, `f7_disagreement_persistence`;
- S3 = equal mean of causal-z `f2_prior_peak_shortfall`, `f2_days_since_high60`, `f2_ma20_slope10`;
- S4 = equal mean of causal-z `f4_rv10_vs_rv30`, `f4_down_up_semivol`, `f4_pnl_dd_duration_interaction`;
- each underlying causal z-score uses the immediately available trailing 252 sessions, minimum 60 observations, and clipping to `[-3,+3]`;
- higher oriented values mean more deterioration;
- predictors at date `t` may use information available no later than `t`.

No fitted axis weights are permitted.

## 4. Frozen primary detector

### 4.1 Candidate change ages

At current session `t`, scan exactly:

\[
\tau \in \{3,4,\ldots,32\}.
\]

For a candidate age `tau`, the candidate changepoint is:

\[
k=t-\tau.
\]

This age scan is the multiscale dimension. No favored age or post-result age subset may be selected.

### 4.2 Causal pre-change baseline

For every axis `j` and candidate changepoint `k`, use exactly the 64 sessions ending at `k`:

\[
S_{j,k-63},\ldots,S_{j,k}.
\]

Fit by ordinary least squares:

\[
S_{j,k-64+q}=a_{j,k}+b_{j,k}q+e_{j,q},\qquad q=1,\ldots,64.
\]

Define the baseline residual variance:

\[
\hat\sigma^2_{j,k}=\max\left(\frac{\sum_{q=1}^{64}e_{j,q}^2}{62},10^{-8}\right).
\]

The `10^-8` floor is a numerical guard only and is fixed prospectively.

Extrapolate the pre-change linear baseline to post-change age `r`:

\[
\hat\mu_{j,k+r}=a_{j,k}+b_{j,k}(64+r),\qquad r=1,\ldots,\tau.
\]

This baseline deliberately permits an existing local slope. The detector therefore asks whether deterioration has **accelerated relative to the immediately preceding trend**, rather than whether the state level is merely high.

### 4.3 One-sided slope GLR by axis

For each axis, candidate `k`, and current `t`, define:

\[
U_{j,k,t}=\frac{\sum_{r=1}^{\tau}r\left(S_{j,k+r}-\hat\mu_{j,k+r}\right)}
{\hat\sigma_{j,k}\sqrt{\sum_{r=1}^{\tau}r^2}}.
\]

Because higher axis values mean more deterioration, only positive incremental slope is admissible. The axis working log-likelihood contribution is:

\[
\ell_{j,k,t}=\frac{1}{2}\max(U_{j,k,t},0)^2.
\]

Negative or improving changes contribute zero rather than being converted into deterioration evidence.

### 4.4 Parameter-free symmetric subset mixture

Let `J={1,2,3,4}` and let `P+` contain all 15 non-empty subsets of `J`.

For each candidate changepoint:

\[
G_{k,t}=\log\left[
\frac{1}{15}\sum_{A\in P_+}
\exp\left(\sum_{j\in A}\ell_{j,k,t}\right)
\right].
\]

All 15 non-empty axis subsets receive equal prior weight. There is no fitted sparsity probability, no S2-specific bonus, no axis selection and no subset chosen from historical outcomes.

The multiscale score is:

\[
G_t=\max_{\tau=3,\ldots,32}G_{t-\tau,t}.
\]

If multiple ages tie exactly, choose the smallest `tau` deterministically. Report that age as `estimated_change_age_t`.

At the selected age, report all four individual `ell_j` values. Do not create a second threshold to label an axis as affected; the axis contributions are descriptive only.

## 5. Frozen label-blind threshold calibration

### 5.1 Information firewall

Threshold calibration may access only the S1–S4 predictor path and timestamps. It may not import, read or receive:

- TRUE_EXHAUSTION / CONTINUATION / AMBIGUOUS labels;
- event peak dates;
- macro-episode IDs;
- downside barrier dates;
- PRE14_7, PRE7_0, PRE21_0 or other outcome windows;
- 0044/0045 hit-rate results.

Future implementation must write a `CALIBRATION_LOCK` artifact containing the threshold and calibration provenance **before** the evaluation code may load the immutable event taxonomy.

### 5.2 Null generator

Fit exactly one label-blind VAR(1) to the four-axis predictor path:

\[
S_t=c+A S_{t-1}+\varepsilon_t.
\]

Use ordinary least squares with intercept. No lag-order search is permitted.

Requirements:

- spectral radius of `A` must be strictly less than 1; otherwise stop with `FAIL_NULL_MODEL_NONSTATIONARY` before label evaluation;
- center the fitted four-dimensional residual vectors by subtracting their sample mean;
- preserve each residual vector intact so contemporaneous cross-axis dependence and empirical heavy-tail shape are retained;
- resample residual vectors with a circular moving-block bootstrap of exactly 7 residual vectors per block;
- use RNG seed `460046`;
- initialize synthetic paths at the fitted unconditional mean `(I-A)^(-1)c`;
- use 256 burn-in sessions;
- generate 5,000 synthetic null paths, each 1,460 post-burn-in sessions long.

The real 0043/0044 outcome taxonomy is not used in any null-model fit or bootstrap operation.

### 5.3 False-alarm budget

Apply the exact frozen detector to every synthetic null path.

For threshold `b`, let `T_b` be the first session at which `G_t >= b`. If no threshold crossing occurs within 1,460 sessions, use censored value `1,461` only for the calibration lower-bound calculation.

Define:

\[
ARL^{trunc}_0(b)=\frac{1}{5000}\sum_{m=1}^{5000}\min(T_b^{(m)},1461).
\]

The frozen false-alarm target is:

\[
ARL^{trunc}_0(b)\ge 365\text{ sessions}.
\]

Because truncation can only reduce the true mean stopping time, satisfying the truncated target is conservative for the model-implied ARL.

Choose the smallest threshold satisfying the target by deterministic 60-iteration bisection over `[0, max_simulated_G + 1]`. Store the resulting IEEE-754 float, full-precision decimal representation, VAR coefficients, residual-data digest, bootstrap seed, synthetic-score digest and code SHA in `CALIBRATION_LOCK`.

No alternate ARL target, null model, bootstrap length, seed or threshold may be tried after event labels are loaded.

## 6. Frozen pulse semantics

Define raw alarm state:

\[
A_t=1[G_t\ge b].
\]

Define the **Transition Pulse** only as a threshold upcrossing:

\[
P_t=1[G_t\ge b\ \text{and}\ G_{t-1}<b].
\]

The first valid detector session cannot emit a pulse because no prior valid score exists.

There is:

- no WATCH state;
- no RISK state;
- no persistence vote;
- no cooldown parameter;
- no refractory parameter;
- no recovery threshold;
- no hysteresis state machine.

A persistent above-threshold spell therefore creates one pulse onset, not a permanent series of repeated pulses. Stickiness is measured separately through raw alarm occupancy and alarm-spell duration rather than hidden by a cooldown rule.

## 7. Frozen evaluation taxonomy and metrics

Only after `CALIBRATION_LOCK` exists may evaluation load the exact immutable 0043 taxonomy and 0044 macro episodes. No observation after `2026-08-02` may enter the 0046 DEVELOPMENT result.

Reuse exactly the frozen 0045 window definitions:

```text
PRE14_7      = sessions -14 through -7 relative to event peak
PRE14_0      = sessions -14 through 0 inclusive
PRE21_0      = sessions -21 through 0 inclusive
```

Primary metrics:

1. primary -15% TRUE_EXHAUSTION event pulse-hit rate in PRE14_7;
2. primary -15% CONTINUATION_FALSE_TOP event false-pulse rate in PRE14_0;
3. primary TRUE macro-episode pulse-hit rate in PRE14_7;
4. primary CONTINUATION macro-episode false-pulse rate in PRE14_0;
5. severe -20% TRUE_EXHAUSTION event pulse-hit rate in PRE14_7;
6. number of primary TRUE events with a pulse onset in PRE21_0;
7. median qualifying onset lead among those TRUE events;
8. raw alarm occupancy `mean(A_t)` over all eligible evaluation sessions;
9. median and 90th-percentile duration of consecutive raw-alarm (`A_t=1`) spells;
10. total pulse count and pulse-date distribution;
11. selected change-age distribution and four-axis contribution values.

Episode metrics use the exact frozen episode grouping and give each usable macro episode one vote, exactly as in 0044/0045.

## 8. Frozen hard gates

A later 0046 result may receive the proposed classification `PASS_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBLE` only if **all** of the following pass:

1. episode diversity satisfies the same minimum diversity rule as 0045;
2. primary TRUE event PRE14_7 pulse-hit rate >= 0.50;
3. primary CONTINUATION event PRE14_0 false-pulse rate <= 0.34;
4. primary TRUE episode PRE14_7 pulse-hit rate >= 0.60;
5. primary CONTINUATION episode PRE14_0 false-pulse rate <= 0.50;
6. severe -20% TRUE event PRE14_7 pulse-hit rate >= 0.57;
7. at least four primary TRUE events have a causal pulse onset in PRE21_0;
8. median qualifying onset lead is between 7 and 21 sessions inclusive;
9. raw alarm occupancy <= 0.175 of eligible sessions;
10. median raw-alarm spell duration <= 7 sessions;
11. 90th-percentile raw-alarm spell duration <= 14 sessions;
12. calibration completed before label loading and `ARL0_trunc >= 365`;
13. no threshold, age range, baseline length, axis role, null model, bootstrap rule, success gate or pulse definition changed after any 0046 outcome was observed;
14. canonical BRRK-0011, Phase 6, execution configuration, production authorization, signing and order-submission authority remain unchanged.

The `0.175` occupancy ceiling is explicitly result-informed: it prospectively demands approximately a 50% reduction from failed 0045 WATCH+RISK occupancy (~34.38%) and is rounded upward rather than claiming false precision.

If any hard gate fails, the proposed classification is `FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY`. Failure remains immutable negative evidence and cannot be rescued under the same ID.

A PASS **does not** make dynamic gross eligible. It only makes a separately preregistered future-only pulse-validation stage eligible.

## 9. Dependence-aware uncertainty reporting

No daily IID p-values are permitted.

After the locked detector has been evaluated:

- event/hit-rate uncertainty is reported with a 10,000-replicate macro-episode cluster bootstrap, seed `460047`, resampling complete frozen macro episodes with replacement and retaining every event inside each sampled episode;
- occupancy and alarm-spell uncertainty is reported with a 10,000-replicate circular moving-block bootstrap over the daily evaluation path using fixed 21-session blocks and seed `460048`;
- confidence intervals are descriptive and cannot rescue a failed hard point-estimate gate;
- leave-one-macro-episode-out results are reported as influence diagnostics only, with no refit of detector parameters and no claim of independent OOS evidence.

## 10. Immutable benchmarks

Only after the 0046 detector is fully frozen and evaluated may the report compare its results with:

- frozen 0044 CORE4/S2 discrimination statistics;
- frozen 0045 trigger-state results, including zero PRE21_0 onsets and 34.38% WATCH+RISK occupancy.

Those benchmarks are descriptive. They cannot change 0046 calibration, gates or detector mathematics.

## 11. Falsification conditions

0046 should fail rather than be rescued if any of these occurs:

- useful hits are concentrated in too few macro episodes to satisfy the frozen episode gate;
- the raw alarm remains sticky and violates occupancy or spell-duration gates;
- continuation false pulses exceed the frozen budget;
- severe-event or PRE14_7 timing gates fail;
- the detector only works after giving S2 special treatment;
- the label-blind null model is non-stationary;
- any outcome label is accessed before the threshold lock;
- threshold or scan range is adjusted after labels or event outcomes are visible;
- an alternative filter, BOCPD, CUSUM, feature set, subset prior or refractory rule is tried under the same ID after failure;
- any portfolio/gross economics are evaluated under 0046.

## 12. Why this architecture is narrower than Issue #160's first draft

The first design synthesis correctly reframed the problem from risk level to transition timing, but it still contained unnecessary researcher degrees of freedom: `CORE4 + S2 + S3 + S4` duplicated information, a separate latent-state filter introduced smoothing parameters, `GLR/CUSUM-style` did not identify one statistic, and BOCPD as a secondary comparator created a second model path.

This freeze removes those freedoms before a result-bearing preregistration exists.

The primary candidate is now exactly one architecture:

```text
frozen S1/S2/S3/S4
    -> 64-session causal pre-change linear detrending
    -> one-sided slope GLR per axis
    -> equal mixture over all 15 non-empty axis subsets
    -> multiscale max over change ages 3..32
    -> label-blind VAR(1) residual-block-bootstrap threshold with ARL0>=365
    -> threshold-upcrossing Transition Pulse
```

## 13. Literature basis

Primary methodological references informing the design, without importing their parameters blindly:

1. Cao, Y., Xie, Y., Gebraeel, N. (2015), *Multi-Sensor Slope Change Detection*, arXiv:1509.00114. Gradual degradation is modeled as a slope change affecting an unknown subset of streams; the paper develops window-limited mixture/GLR procedures, ARL/EDD calibration and explains why differencing can reduce signal-to-noise ratio.
2. Chen, Y., Wang, T., Samworth, R. J. (2022), *High-Dimensional, Multiscale Online Changepoint Detection*, JRSS-B 84(1), 234–266. Motivates multiscale online evidence aggregation and explicit null patience/false-alarm control under sparse changes.
3. Pishchagina, L., Romano, G., Fearnhead, P., Runge, V., Rigaill, G. (2026), *Online multivariate changepoint detection: leveraging links with computational geometry*, JRSS-B 88(1), 171–194. Shows exact sparse likelihood-ratio recovery is practical in low dimension and reinforces treating sparse affected-coordinate structure explicitly.
4. Adams, R. P., MacKay, D. J. C. (2007), *Bayesian Online Changepoint Detection*, arXiv:0710.3742. Supports the conceptual importance of recent-change/run-length semantics, but BOCPD is deliberately excluded from the 0046 candidate to preserve one-candidate discipline.

## 14. Governance boundary and exact next step

This design freeze creates no formal research registry row, exposure registration, runner, result artifact, parameter candidate result, dynamic-gross stage or production authority.

The exact next step after this design-only change is merged is a **separate formal preregistration PR** for `BRRK-EXHAUSTION-PULSE-0046` that copies this architecture without alteration, registers the exposed development dataset and lineage, and freezes exactly one candidate before any detector result is released.

Until that preregistration is merged:

```text
0046 preregistration             NOT CREATED
0046 runner                      NOT CREATED
0046 calibration                 NOT RUN
0046 result                      NONE
0046 portfolio economics         FORBIDDEN
dynamic-gross eligibility        FALSE
canonical BRRK change            NONE
Phase-6 change                   NONE
production authorization         NO_CHANGE / FALSE
```
