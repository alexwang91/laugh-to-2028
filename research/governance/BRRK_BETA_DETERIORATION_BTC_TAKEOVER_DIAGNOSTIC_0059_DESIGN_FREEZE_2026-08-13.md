# BRRK-BETA-DETERIORATION-BTC-TAKEOVER-DIAGNOSTIC-0059 — DESIGN FREEZE

Date: 2026-08-13  
Status: **DESIGN FROZEN / NUMERICAL PREREGISTRATION ABSENT / NOT IMPLEMENTED / NOT RUN**  
Proposed governance mode: `PROGRAM_GOVERNED_V1`  
Proposed research stage: `STAGE_1_INFORMATION_TEST`  
Proposed objective type: `MECHANISM_TEST`  
Proposed research domain: `RISK_CONTROL`

This document freezes the scientific architecture for a new Beta-to-BTC defensive-takeover mechanism diagnostic. It is design only. It creates no numerical preregistration, no runner, no dataset release, no result, no portfolio allocation rule, no canonical change, no Phase-6 change, no production authorization, no signing authority and no order-submission authority.

Research ID:

`BRRK-BETA-DETERIORATION-BTC-TAKEOVER-DIAGNOSTIC-0059`

Proposed family:

`BRRK_BETA_TO_BTC_DEFENSIVE_HANDOFF`

The study asks:

> Does a low-dimensional causal deterioration state in the symmetric ETH/SOL Beta tier contain recurrent, monotone information about subsequent BTC-over-Beta continuation value, before any entry/exit threshold, allocation map or switching economics is defined?

0059 is deliberately a **pure mechanism diagnostic**. It does not attempt parameter calibration, fixed-rule strategy validation or portfolio promotion.

---

## 1. Why 0059 exists

### 1.1 Binding 0058 closure

`BRRK-BETA-BTC-CONTINUATION-PARAMETER-GEOMETRY-0058` is immutable `FAIL_NO_STABLE_PARAMETER_PLATEAU / CLOSED`.

0058 validly evaluated its exact preregistered two-parameter family and found no 5 bps interior cell satisfying both frozen gradient and Hessian flatness criteria. No admissible plateau existed and no representative was selected.

The exposed descriptive historical maximum at `L=120, kappa=0.5` has zero selection, freeze, continuation or rescue authority.

Therefore 0059 may not:

- reuse `L=120` because it was the 0058 argmax;
- reuse `kappa=0.5` because it was the 0058 argmax;
- zoom around the 0058 surface;
- refine the 0058 grid;
- relax the 0058 gradient threshold;
- relax the 0058 Hessian threshold;
- change the 0058 normalization to recover a plateau;
- substitute another 0058 component, medoid or boundary point;
- treat 0058 DEVELOPMENT history as independent OOS;
- rerun or recompute 0058 under any guise.

0058 establishes only that the exact two-parameter thresholded relative-continuation formulation lacked a broad stable parameter basin under its frozen geometry. It does not establish that every Beta-to-BTC defensive mechanism is false.

### 1.2 Binding 0057 closure

`BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-INTERFACE-REPLICATION-0057` is immutable `FAIL_SIMPLE_BETA_ROUTER_COST_FRAGILE / CLOSED`.

The ETH/SOL micro-timing line is closed. 0059 therefore uses no dynamic ETH-versus-SOL leader selection, no RM60 router, no alternative ETH/SOL lookback and no result-informed repair of 0057.

### 1.3 Binding 0043–0046 evidence

The exhaustion lineage contains an important distinction between **continuous state information** and **discrete trigger translation**.

- 0043 found useful DEVELOPMENT separation concentrated in a small number of causal deterioration families, especially fast/slow trend disagreement, price structure and volatility/downside structure.
- 0044 showed that a low-dimensional frozen state retained episode-aware discrimination.
- 0045 then failed to convert that state into the exact frozen WATCH/RISK trigger with adequate sensitivity/timing.
- 0046 solved the 0045 stickiness problem only by becoming too sparse and also failed.

0059 uses this as methodological evidence only: continuous state information can be worth testing even when an earlier absolute trigger translation fails. 0059 does **not** reopen the 0045/0046 exhaustion trigger lineage and does not copy their state machine.

### 1.4 Binding 0047–0055 evidence

0047 did not establish the exact frozen recurrent BTC-positive-episode durable BTC-to-Beta handoff structure. 0048 was support-inconclusive. 0053 showed that 4h row multiplication did not improve calendar-equivalent dependence support. 0054 and 0055 failed their frozen estimator-precision readiness criteria even after structural dimensionality reduction.

Therefore 0059 is intentionally:

- daily, not 4h;
- low-dimensional;
- nonparametric / rank-oriented at the information-test layer;
- free of a fitted dynamic probability model;
- free of a BTC-positive episode clock;
- free of a duration-aware hazard model;
- free of portfolio allocation economics.

No 0047/0048/0053/0054/0055 same-ID rescue is attempted.

### 1.5 Opportunity-cost / capital hierarchy evidence

0042 identified historically beneficial defensive scaling and material BTC retention inside the broader architecture, while explicitly withholding winner-cap counterfactual authority. The later repository lineage also formalized BTC as defensive anchor and ETH/SOL as the Beta tier.

0059 keeps that hierarchy:

```text
BTC                                  defensive anchor
ETH + SOL                            symmetric Beta risk tier
cash                                 outside the research question
leverage                             forbidden
shorting                             forbidden
```

BTC-to-cash timing remains a separate future layer and is not tested here.

---

## 2. Material new mechanism and lineage semantics

0059 is a **mechanism fork / new-target diagnostic**, not a parameter descendant of the failed 0058 surface.

0058 asked whether a thresholded two-parameter relative-continuation trading rule possessed a broad after-cost terminal-wealth plateau.

0059 asks a logically earlier question:

> Before defining any thresholded Beta/BTC trading rule, does a fixed low-dimensional deterioration state have stable monotone information about future BTC-over-Beta continuation value?

The difference is substantive:

```text
0058 target                         strategy parameter identifiability on J(L,kappa)
0058 primary object                after-cost log terminal wealth surface
0058 degrees of freedom            lookback L + threshold kappa

0059 target                         state informativeness / continuation-value ordering
0059 primary object                fixed causal state vs future BTC-over-Beta relative outcomes
0059 degrees of freedom            no trading threshold; no wealth-surface search
```

The later central registry should record 0059 as result-informed DEVELOPMENT with lineage to the immutable prior evidence. It may cite 0058 as a `MECHANISM_FORK` / `RESULT_INFORMED` ancestor and 0044/0047 as definition/evidence sources. It must not claim independent replication.

All reusable history already visible to the researcher remains `RESEARCHER_EXPOSED_HISTORY`.

---

## 3. Frozen asset universe and Beta representation

Primary universe is exactly:

```text
BTC / ETH / SOL
```

No BNB, XRP, meme assets, stablecoin timing, derivatives, funding, perp basis or external macro series may enter 0059.

### 3.1 Symmetric Beta signal proxy

Let completed UTC daily closes be `BTC_t`, `ETH_t`, `SOL_t`.

Define the symmetric Beta log-price proxy:

`b_t = 0.5 * log(ETH_t) + 0.5 * log(SOL_t)`.

Define the symmetric Beta/BTC relative log-price state:

`z_t = b_t - log(BTC_t)`

which is equivalently:

`z_t = 0.5*log(ETH_t/BTC_t) + 0.5*log(SOL_t/BTC_t)`.

This symmetric representation was frozen before the 0058 result and does not use any exposed 0058 winning parameter. ETH and SOL have equal ex-ante status. No hindsight winner selection is permitted.

### 3.2 Future Beta continuation outcome convention

0059 is not a trading backtest, but its later diagnostic needs a mechanically defined Beta continuation comparator.

For any future horizon `h` later frozen in preregistration, define origin-reset, no-rebalance Beta gross wealth:

`W_BETA(t,h) = 0.5*(ETH_(t+h)/ETH_t) + 0.5*(SOL_(t+h)/SOL_t)`.

Define BTC gross wealth:

`W_BTC(t,h) = BTC_(t+h)/BTC_t`.

Define BTC-over-Beta continuation advantage:

`Y_t(h) = log(W_BTC(t,h) / W_BETA(t,h))`.

Higher `Y_t(h)` means BTC delivered better subsequent continuation value than the symmetric Beta tier over that horizon.

This outcome is a diagnostic label/continuous target only. It is not a state-switching strategy and has no transaction-cost, turnover, CAGR, terminal-wealth or allocation authority under 0059.

---

## 4. Frozen causal trend architecture inherited from pre-0058 definitions

0059 may use the exact already-frozen V1/0047 trend architecture. It may not choose a new lookback from 0058 output.

For a positive price-like series `P_t`, define log return:

`r_t = log(P_t) - log(P_(t-1))`.

For each frozen horizon:

```text
H = [20, 60, 120, 240]
```

use the existing normalized trend component:

```text
momentum_h(t) = log(P_t/P_(t-h))
scale_h(t)    = rolling_std_h(r) * sqrt(h)
component_h(t)= tanh(momentum_h(t)/scale_h(t))
```

with exact denominator/validity semantics to be inherited from the repository implementation and hash-bound in later preregistration.

Exact frozen weights:

```text
FAST = [0.15, 0.25, 0.30, 0.30]
SLOW = [0.10, 0.20, 0.30, 0.40]
```

`TREND_FAST(P)` and `TREND_SLOW(P)` are the corresponding weighted sums when all required components are valid.

These horizons and weights predate 0058 and therefore have no relationship to the exposed 0058 argmax.

---

## 5. Frozen low-dimensional deterioration representation

0059 opens **one fixed three-axis state representation**. It is not a feature tournament and not a parameter grid.

All predictors at date `t` may use information no later than the completed UTC close at `t`.

Higher values on every axis are oriented to mean **greater evidence that continuing Beta risk is deteriorating relative to sheltering in BTC**.

### Axis D1 — Beta own fast/slow trend disagreement

Construct the synthetic Beta price-like series:

`B_t = exp(b_t)`.

Define:

`D1_raw(t) = TREND_SLOW(B)_t - TREND_FAST(B)_t`.

Mechanism interpretation: the slower Beta trend can remain positive while the faster layer deteriorates first. This transfers the pre-0058 fast/slow disagreement concept to the symmetric Beta tier.

No new horizon or fitted coefficient is introduced.

### Axis D2 — Beta price-structure distance to recent high

Define the trailing 60-completed-session Beta high:

`HIGH60_B(t) = max(B_(t-59), ..., B_t)`.

Define:

`D2_raw(t) = log(HIGH60_B(t) / B_t)`.

Mechanism interpretation: increasing distance below the recent Beta high is a simple close-based price-structure deterioration state. The 60-session high family was frozen in the 0043/0044 price-structure lineage before 0058.

0059 deliberately uses only this simple close-based distance-to-high coordinate from the broader historical price-structure family. It does not add RSI, MACD, volume, OBV, breadth, correlation or a fitted structural model.

### Axis D3 — Beta-versus-BTC relative fast/slow disagreement

Construct the positive relative price-like series:

`R_t = exp(z_t)`.

Define:

`D3_raw(t) = TREND_SLOW(R)_t - TREND_FAST(R)_t`.

Mechanism interpretation: if Beta relative leadership is losing speed before the slower relative trend fully decays, BTC may be taking over as the defensive leader even while the long-horizon Beta/BTC state remains elevated.

This is not the 0058 score `S_t(L)` and has no `kappa` threshold.

### 5.4 Causal normalization

0059 inherits the pre-0058 0043/0044 causal normalization convention rather than creating a new normalization after seeing 0058 results.

For each `D1_raw`, `D2_raw`, `D3_raw` at date `t`:

1. use only the trailing 252 completed sessions through `t`;
2. require at least 60 valid observations;
3. compute trailing mean and sample standard deviation under the exact repository convention later frozen in preregistration;
4. z-standardize causally;
5. clip to `[-3,+3]`.

Call the normalized axes `D1_t`, `D2_t`, `D3_t`.

### 5.5 Fixed joint score

Define one fixed equal-weight deterioration state:

`BETA_DETERIORATION_STATE_t = (D1_t + D2_t + D3_t) / 3`.

No fitted weights, PCA, regression coefficients, tree model, neural model, feature selection or post-result reweighting are allowed.

The three component axes must also be reported separately for interpretation and redundancy diagnostics, but they do not create three competing candidate models. The joint equal-weight state is the sole candidate representation controlling 0059 classification.

---

## 6. Frozen outcome-horizon principle

0059 must not pick one future horizon because it looks best on the exposed history.

The later numerical preregistration must use the **entire pre-existing canonical horizon family**:

```text
20 / 60 / 120 / 240 completed daily sessions
```

For each valid origin, compute `Y_t(h)` for every horizon with complete future maturity.

No horizon is selected post hoc. No local search over `h` is allowed. No additional `30/40/90/180` horizon may be introduced after result exposure.

The preregistration must freeze a simultaneous multi-horizon interpretation rule before any 0059 target values are released. It may require directional consistency across several/all horizons, but it may not choose the historically strongest horizon as the primary result after execution.

Because `h` is not optimized and all four inherited horizons are mandatory, 0059 is not a parameter-calibration ID.

---

## 7. Primary scientific hypothesis

Primary hypothesis:

> Higher `BETA_DETERIORATION_STATE_t` is associated with larger subsequent `Y_t(h)` across the frozen canonical horizon family, meaning that a worsening low-dimensional Beta state is monotonically associated with stronger future BTC-over-Beta continuation value.

Adversarial alternative:

> The state has no stable monotone association with future BTC-over-Beta continuation value, or any apparent association is confined to one horizon/time segment and therefore does not support a recurrent defensive-takeover mechanism.

This is an information/mechanism question. No trading threshold is implied by a positive result.

---

## 8. Planned inferential architecture to freeze numerically before execution

The exact numerical preregistration is intentionally a separate stage after DESIGN merge. It must freeze the complete diagnostic contract before any 0059 outcome is computed.

At minimum it must bind:

1. exact common UTC daily source slice and immutable payload identity;
2. exact warm-up rule for the 240-session trend architecture and 252-session causal normalization;
3. exact origin eligibility and target-maturity handling for 20/60/120/240 horizons;
4. exact primary monotone association statistic for `BETA_DETERIORATION_STATE` versus `Y(h)`;
5. exact simultaneous multi-horizon success/failure rule;
6. exact chronological robustness partition and minimum directional consistency;
7. exact dependence-aware uncertainty method that respects overlapping forward horizons and serial dependence;
8. exact block length, replicate count, seed, quantile convention and simultaneous-inference semantics if moving-block/bootstrap inference is used;
9. exact support/minimum-effective-history gate before inferential metrics become eligible;
10. exact secondary diagnostics for D1/D2/D3 and their correlation/effective-rank structure;
11. exact result classification precedence;
12. exact immutable result schema and persistence requirements.

Numerical gates may not be chosen after any 0059 future outcome, rank statistic, time-segment result or plot is visible.

No portfolio backtest is authorized by the later preregistration unless a future separate research ID explicitly opens portfolio translation.

---

## 9. What 0059 is not allowed to compute

Under this research ID, including its later exactly-once execution, the following are forbidden:

- a BTC/Beta entry threshold;
- an exit threshold;
- hysteresis;
- minimum holding period;
- cooldown;
- turnover-minimizing band;
- dynamic allocation weight;
- 100% Beta versus 100% BTC switching NAV;
- full-cycle strategy terminal wealth;
- strategy CAGR;
- strategy MDD;
- transaction-cost strategy comparison;
- `L`/`kappa` parameter surface;
- gradient or Hessian rescue of 0058;
- ETH-versus-SOL router;
- BTC-to-cash rule;
- leverage;
- shorting;
- funding/perpetual implementation;
- production trading.

Future `Y_t(h)` continuation outcomes are allowed only as diagnostic labels/continuous targets under the preregistered mechanism test. They must not be converted into a portfolio counterfactual inside 0059.

---

## 10. Explicit forbidden variable additions

0059 may not add a variable merely because the frozen three-axis score looks weak.

The following are outside the 0059 candidate representation:

- 0058 `L`, `kappa`, `sigma240` score geometry or any transformation selected from the 0058 surface;
- 0057 RM60 ETH/SOL leader signal or any alternate ETH/SOL micro-timing lookback;
- RSI/RSI variants;
- MACD variants;
- realized-volatility filters;
- semivolatility filters;
- ATR;
- volume / OBV / trade-count confirmation;
- breadth;
- cross-asset correlation;
- alt beta to BTC;
- 4h features;
- state age / BTC-positive episode clock;
- BOCPD / changepoint model;
- hidden-Markov state;
- machine-learned probability;
- funding, basis, open interest or derivatives crowding;
- macro variables;
- cash-state variables.

Some of these information families may be scientifically legitimate under a future **new research ID**. They have no same-ID rescue authority here.

---

## 11. Why this is not a 0058 result-informed rescue

The design has four firewalls.

### Firewall A — no exposed 0058 parameter enters 0059

No `L=120`, `kappa=0.5`, nearby value, local grid shape, gradient, Hessian or argmax is used.

### Firewall B — the predictor families existed before 0058

Fast/slow trend disagreement, 60-session price-structure distance-to-high, causal 252-session normalization and the canonical 20/60/120/240 trend family were frozen in 0043/0044/0047 before 0058 was executed.

### Firewall C — the scientific target changed

0058 searched for a broad stable parameter region in after-cost terminal wealth for a thresholded switching mechanism.

0059 tests continuous state informativeness against future BTC-over-Beta continuation outcomes with no thresholded strategy.

### Firewall D — no immediate economic promotion path

Even a full 0059 PASS can only make a **new research ID** eligible for a separately preregistered translation/calibration study. 0059 cannot freeze a trading threshold, validate a portfolio or alter canonical BRRK.

Therefore 0059 is result-aware in the legitimate sense that it knows 0058 failed, but it does not repair the failed surface using information revealed by that surface.

---

## 12. Classification philosophy

Exact machine strings and numerical gates belong to the later preregistration, but design-level meanings are frozen.

A valid 0059 result must conceptually resolve to one of:

- `INSUFFICIENT_DEPENDENCE_AWARE_SUPPORT` — required support is unavailable under the frozen causal/maturity contract;
- `FAIL_NO_RECURRENT_MONOTONE_DEFENSIVE_TAKEOVER_INFORMATION` — the joint state lacks the preregistered cross-horizon/time/dependence-consistent monotone relationship;
- `PASS_DEFENSIVE_TAKEOVER_MECHANISM_STAGE_ELIGIBLE` — the fixed joint state passes all preregistered information/robustness gates and may motivate a new-ID translation/calibration stage;
- `INVALID_EXECUTION` — integrity, causal, schema or exactly-once contract failure.

A weak primary state cannot be rescued by selecting whichever of D1/D2/D3 happened to perform best. Component diagnostics are descriptive and cannot replace the joint primary candidate.

---

## 13. Follow-up authority if 0059 passes

A 0059 PASS would establish only:

> the frozen low-dimensional deterioration state contains recurrent DEVELOPMENT information about future BTC-over-Beta continuation ordering under the preregistered diagnostics.

It would **not** establish an economically optimal threshold or portfolio.

The next permissible research step after a PASS would require a new research ID. Depending on the frozen 0059 conclusion, that later ID could be a systematic parameter-calibration / translation study that prospectively defines a low-dimensional mapping from state to Beta/BTC allocation.

If a later study contains continuous parameters, it must use the project's governed parameter-geometry principles: prospectively frozen domain, sensitivity/curvature or other justified stability geometry, broad stable region, deterministic representative selection and a separate new-ID fixed-parameter validation stage.

No historical argmax selection is authorized.

---

## 14. Follow-up authority if 0059 fails or is inconclusive

If 0059 fails, the exact three-axis mechanism closes. Same-ID rescue is forbidden.

If 0059 is support-inconclusive, the exact measurement remains preserved and same-ID support-rule relaxation is forbidden.

Any later alternative must use a new research ID and explicitly disclose 0059 exposure. Examples that would require a new ID include:

- replacing distance-to-high with volatility/downside state;
- adding absolute BTC state;
- changing axis weights;
- changing normalization;
- using a thresholded event definition;
- adopting a changepoint model;
- using 4h data;
- changing the future target architecture;
- introducing BTC-to-cash.

---

## 15. Immutable result persistence requirement for later stages

Before any 0059 historical outcome is executed, the preregistration/result schema must freeze lossless persistence sufficient for audit without recomputation.

At minimum the unique execution should persist:

- exact source payload identity;
- every valid origin date;
- raw D1/D2/D3 values;
- normalized D1/D2/D3 values;
- joint `BETA_DETERIORATION_STATE`;
- `Y_t(h)` for every frozen horizon and eligible origin;
- origin eligibility / maturity flags;
- primary rank/association statistics;
- chronological robustness diagnostics;
- dependence-aware inference outputs;
- component-axis diagnostics and correlation/effective-rank summary;
- exact gate trace and final classification.

No post-closeout remeasurement may be used to recover omitted diagnostic state.

---

## 16. Design-stage prohibitions

Before this DESIGN merges, and before a later numerical preregistration merges, do not:

- load or calculate 0059 future `Y_t(h)` outcomes;
- compute any 0059 association statistic;
- plot the 0059 state against future returns;
- inspect conditional continuation-value bins;
- test alternative axis combinations;
- choose numerical gates from historical 0059 output;
- run any 0059 portfolio economics.

Implementation-only work later must be restricted to synthetic/toy/contract fixtures until preregistration has merged. Historical execution remains forbidden until a separately merged controlled-execution boundary exists.

---

## 17. Program authority remains unchanged

```text
Canonical BRRK-0011                    NO CHANGE
Phase 6                                NO CHANGE
BTC-to-cash layer                      NOT OPENED
leverage                               FORBIDDEN
shorting                               FORBIDDEN
production gross cap                   1.0
production_authorized_components       []
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

0059 is research-only DEVELOPMENT evidence.

---

## 18. Exact next stage after DESIGN merge

Only after this DESIGN is merged may 0059 enter a separate **numerical/data preregistration** stage.

That preregistration must create the central `PROGRAM_GOVERNED_V1` registry owner before any formal `research/brrk_...0059/` path is materialized, register the exposed-development dataset identity, freeze exact numerical association/support/temporal/dependence gates and freeze the immutable result schema.

No historical 0059 target or strategy result may be computed during DESIGN or preregistration.
