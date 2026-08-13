# BRRK-BTC-CASH-ABSOLUTE-RISK-DIAGNOSTIC-0060 — DESIGN FREEZE

Date: 2026-08-13  
Status: **DESIGN FROZEN / NUMERICAL PREREGISTRATION ABSENT / NOT IMPLEMENTED / NOT RUN**  
Proposed governance mode: `PROGRAM_GOVERNED_V1`  
Proposed research stage: `STAGE_1_INFORMATION_TEST`  
Proposed objective type: `MECHANISM_TEST`  
Proposed research domain: `RISK_CONTROL`

This document freezes the scientific architecture for a new BTC-to-Cash absolute-risk mechanism diagnostic. It is design only. It creates no numerical preregistration, no dataset release, no runner, no historical result, no BTC/Cash trigger, no gross-risk map, no re-entry rule, no strategy NAV, no canonical BRRK change, no Phase-6 change, no production authorization, no signing authority and no order-submission authority.

Research ID:

`BRRK-BTC-CASH-ABSOLUTE-RISK-DIAGNOSTIC-0060`

Proposed family:

`BRRK_BTC_TO_CASH_GROSS_RISK`

The study asks:

> Does a fixed low-dimensional causal BTC absolute-risk state contain recurrent information about subsequent BTC downside severity and cash-relative terminal underperformance, before any BTC-to-Cash threshold, holding rule, re-entry rule, gross allocation map or portfolio economics is defined?

0060 is deliberately a **pure mechanism diagnostic**. It does not attempt threshold calibration, fixed-rule validation, portfolio optimization or production promotion.

---

## 1. Why 0060 exists

### 1.1 Binding 0059 closure

`BRRK-BETA-DETERIORATION-BTC-TAKEOVER-DIAGNOSTIC-0059` is immutable `FAIL_NO_MONOTONE_CONTINUATION_INFORMATION / CLOSED`.

0059 validly tested one frozen equal-weight Beta-deterioration state against future BTC-over-Beta continuation value on the required horizon family. G0 integrity and G1 support passed, but G2 monotone information failed because only 20d was weakly positive while 60d, 120d and 240d were negative. G3 temporal recurrence and G4 dependence-aware robustness also failed.

Therefore 0060 may not:

- promote the favorable exposed 0059 20d statistic;
- delete or reweight 0059 D1/D2/D3 components;
- change 0059 normalization, support, block bootstrap, horizon family or classification rule;
- convert 0059 component diagnostics into an after-the-fact Beta-to-BTC rule;
- reuse the 0058 `(L=120, kappa=0.5)` descriptive argmax;
- reopen ETH/SOL micro-timing from 0057;
- claim that 0059 DEVELOPMENT history is independent OOS.

0060 is scientifically different from 0059 because both the predictor object and the outcome object change:

```text
0059 predictor object                 symmetric ETH/SOL Beta deterioration relative to BTC
0059 outcome object                   BTC-over-Beta continuation value

0060 predictor object                 BTC-only absolute-risk state
0060 outcome object                   future BTC downside / cash-relative loss
```

0060 is not a rescue of Beta-to-BTC timing. BTC-to-Cash is a separate gross-risk layer that 0059 explicitly did not test.

### 1.2 Binding 0043–0046 evidence

The exhaustion lineage established an important separation between **continuous risk information** and **operational trigger translation**.

- 0043 found useful causal deterioration information in momentum/trend disagreement, price structure and volatility/downside families.
- 0044 prospectively compressed that information into a low-dimensional equal-weight state and passed its episode-aware discrimination gates.
- 0045 then failed to translate the state into the exact frozen WATCH/RISK state machine with adequate sensitivity and timing.
- 0046 solved stickiness only by becoming too sparse and also failed.

0060 uses this lineage only as mechanism and dimensionality evidence. It does **not** reopen the 0045/0046 trigger family and does not copy their state-transition, persistence or recovery rules.

### 1.3 Binding continuous-gross and cycle-exit evidence

`EXPOSURE-SMOOTH-0038-CONTINUOUS-BETA` historically validated a continuous exposure mechanism but remained `SHADOW_ONLY / NOT_PROMOTED`.

The later P5.4/P5.5 lineage froze multiple state-to-gross maps in `[0,1]` and evaluated 3 state profiles x 4 gross-behavior maps. No profile/map combination passed the complete frozen validation stack; P5.5 closed `COMPLETE_IMMUTABLE_NO_PROMOTION_FAIL_STOP`.

Therefore 0060 is **not** allowed to become another gross-map search. It asks only whether a BTC-only absolute-risk state contains information worth translating in a later, separately governed research ID.

### 1.4 Capital hierarchy

0060 keeps the project hierarchy explicit:

```text
BTC                                  defensive crypto anchor
ETH / SOL / other Beta               outside the 0060 predictor and target
Cash                                 zero-risk comparison asset for diagnostic semantics
leverage                             forbidden
shorting                             forbidden
```

The study does not assume that BTC should be sold merely because Beta weakens. It asks the harder absolute question: when BTC itself is structurally deteriorating, is subsequent BTC downside measurably worse than a cash reference?

---

## 2. Material new mechanism and lineage semantics

0060 is a **new-target / new-layer mechanism fork**.

The program has already spent substantial evidence budget on relative timing:

```text
ETH vs SOL                            micro-timing / leadership line
Beta vs BTC                           defensive-handoff line
BTC vs Cash                           separate gross-risk line opened by 0060
```

0060 moves from relative-asset leadership to absolute crypto-risk information.

This distinction is substantive:

```text
relative timing question              which crypto asset should carry the risk budget?
absolute risk question                should the crypto risk budget itself remain fully exposed?
```

All historical data already observed by the researcher remain `RESEARCHER_EXPOSED_HISTORY`. A later registry owner must record 0060 as result-informed DEVELOPMENT research with lineage to 0043/0044/0045/0046, 0038/P5.4/P5.5 and 0059. It must not claim independent replication or temporally unseen validation.

---

## 3. Frozen universe and information boundary

Primary universe is exactly:

```text
BTC
```

Cash is a comparison numeraire, not a traded candidate under 0060.

No ETH, SOL, BNB, XRP, alt breadth, cross-sectional relative strength, stablecoin supply, on-chain holder cost, derivatives, funding, perp basis, options, volume/OBV, macroeconomic series, rates, equities or external sentiment may enter the 0060 state.

The design is deliberately **price-only and BTC-only** so that a first absolute-risk information test is not confounded by a new-data feature tournament.

If price-only absolute-risk information later fails, any on-chain holder-cost or other new-data mechanism requires a new research ID. It cannot be added to 0060 after result exposure.

All predictors at date `t` may use information no later than the completed UTC daily BTC close at `t`.

---

## 4. Frozen BTC trend architecture

0060 inherits the already established BRRK/0047 trend architecture rather than introducing a new momentum search.

For positive BTC price series `P_t = BTC_t`, define daily log return:

`r_t = log(P_t) - log(P_(t-1))`.

Use the pre-existing horizon family:

```text
H = [20, 60, 120, 240]
```

For each horizon `h`:

```text
momentum_h(t)  = log(P_t / P_(t-h))
scale_h(t)     = sample_std_ddof1(r over trailing h completed returns through t) * sqrt(h)
component_h(t) = tanh(momentum_h(t) / scale_h(t))
```

All four components are required when constructing the inherited trend aggregates.

Frozen weights:

```text
FAST = [0.15, 0.25, 0.30, 0.30]
SLOW = [0.10, 0.20, 0.30, 0.40]
```

`TREND_FAST(BTC)` and `TREND_SLOW(BTC)` are the corresponding weighted sums.

No alternative trend horizon, EMA pair, RSI variant, MACD variant or post-result lookback search is authorized.

---

## 5. Frozen low-dimensional BTC absolute-risk representation

0060 opens **one fixed three-axis state representation**. It is not a feature tournament and not a parameter grid.

Higher values on every axis mean greater BTC absolute-risk deterioration.

### Axis A1 — BTC fast/slow trend disagreement

Use two pre-existing 0043/0044 structural coordinates.

Raw coordinate 1:

`A1a_raw(t) = TREND_SLOW(BTC)_t - TREND_FAST(BTC)_t`.

Raw coordinate 2 is the causal persistence count of consecutive completed sessions through `t` for which:

`TREND_FAST(BTC) < TREND_SLOW(BTC)`.

Call it:

`A1b_raw(t) = FAST_BELOW_SLOW_PERSISTENCE_t`.

Interpretation: a slower positive/less-negative trend can persist after the faster layer has deteriorated. Persistence distinguishes a one-day crossing from a sustained structural disagreement without creating an action threshold.

### Axis A2 — BTC price-structure deterioration

Use three pre-existing 0043 price-structure coordinates, all BTC-only.

1. distance below the trailing 60-completed-session high:

`A2a_raw(t) = log(HIGH60_BTC(t) / BTC_t)`

where:

`HIGH60_BTC(t) = max(BTC_(t-59), ..., BTC_t)`.

2. completed sessions since the most recent occurrence of that trailing 60-session high:

`A2b_raw(t) = SESSIONS_SINCE_HIGH60_BTC(t)`.

3. negative 10-session log slope of the causal MA20 level:

```text
MA20_t       = mean(BTC_(t-19), ..., BTC_t)
A2c_raw(t)   = -log(MA20_t / MA20_(t-10))
```

Higher A2c means the local MA20 structure is falling more sharply.

Interpretation: A2 measures failed-high geometry, time away from the recent high and local price-structure slope without requiring a peak label or future barrier.

### Axis A3 — BTC volatility/downside asymmetry

Use three pre-existing 0043 volatility/downside coordinates.

Let daily BTC log returns be `r_t`.

1. realized-volatility acceleration:

```text
RV10_t       = sample_std_ddof1(r over last 10 completed returns)
RV30_t       = sample_std_ddof1(r over last 30 completed returns)
A3a_raw(t)   = log(RV10_t / RV30_t)
```

If the preregistered implementation requires explicit validity handling for zero volatility, that handling must be frozen before any historical outcome is released.

2. downside/upside semivolatility ratio over 20 completed returns:

```text
DOWN20_t = sqrt(mean(r_i^2 for negative r_i in the trailing 20-return window under the exact preregistered empty-side convention))
UP20_t   = sqrt(mean(r_i^2 for positive r_i in the trailing 20-return window under the exact preregistered empty-side convention))
A3b_raw(t) = log(DOWN20_t / UP20_t)
```

The exact zero/empty-side validity convention must be frozen in numerical preregistration before any 0060 target is evaluated.

3. negative-return share over 20 completed returns:

`A3c_raw(t) = count(r_i < 0 over trailing 20) / 20`.

Interpretation: A3 measures volatility acceleration, downside asymmetry and persistence of negative daily outcomes. It is not ATR-, volume- or derivative-based.

### 5.4 Causal normalization

Every raw coordinate above is normalized causally using the inherited 0043/0044 convention:

1. trailing 252 completed sessions through `t` only;
2. minimum 60 valid historical observations;
3. trailing mean;
4. sample standard deviation `ddof=1`;
5. zero standard deviation -> invalid/NaN under the exact preregistered convention;
6. z-standardize;
7. clip to `[-3,+3]`.

Call normalized coordinates `A1a_z`, `A1b_z`, `A2a_z`, `A2b_z`, `A2c_z`, `A3a_z`, `A3b_z`, `A3c_z`.

### 5.5 Fixed axis scores

Define:

```text
A1_t = mean(A1a_z, A1b_z)                  only when both are valid
A2_t = mean(A2a_z, A2b_z, A2c_z)           only when all three are valid
A3_t = mean(A3a_z, A3b_z, A3c_z)           only when all three are valid
```

No available-feature averaging is permitted inside the primary state. Missing required coordinates make that origin invalid.

### 5.6 Fixed joint state

Define the sole primary candidate representation:

`BTC_ABSOLUTE_RISK_STATE_t = (A1_t + A2_t + A3_t) / 3`.

No fitted weights, PCA, regression coefficients, feature selection, nonlinear learner, hidden-state model, changepoint model, tree model, neural model or post-result reweighting are allowed.

A1/A2/A3 and the eight underlying coordinates may be reported separately only as descriptive decomposition/redundancy diagnostics. They create no competing candidate models and cannot control the primary classification.

---

## 6. Frozen future outcome semantics

0060 must distinguish two economically different objects:

1. **terminal cash-relative underperformance** — was BTC actually below its origin price at horizon end?
2. **pathwise adverse excursion** — how much downside did BTC experience before horizon maturity, even if it later recovered?

For any future horizon `h` later frozen in preregistration, define BTC gross wealth from origin:

`W_BTC(t,h) = BTC_(t+h) / BTC_t`.

Cash gross wealth is defined only as the diagnostic numeraire:

`W_CASH(t,h) = 1`.

No interest rate, stablecoin yield, lending yield or treasury return is introduced under 0060.

### 6.1 Terminal cash-relative loss

Define:

`TERMINAL_LOSS_t(h) = max(0, log(W_CASH(t,h) / W_BTC(t,h)))`

which simplifies to:

`TERMINAL_LOSS_t(h) = max(0, -log(BTC_(t+h) / BTC_t))`.

Higher values mean BTC ended the horizon further below its origin while Cash preserved nominal capital.

### 6.2 Pathwise adverse excursion from origin

Define:

`ADVERSE_EXCURSION_t(h) = max_{u=1..h} max(0, -log(BTC_(t+u) / BTC_t))`.

This is the worst origin-relative BTC loss reached before horizon maturity.

It is deliberately not the maximum drawdown from an intra-window running peak, because a decision made at origin `t` cannot capture gains that occur after `t` and then retroactively define the cash comparison entry level.

### 6.3 Why both outcome coordinates are mandatory

A state that predicts only transient pathwise dips but systematically precedes strong terminal recovery is not sufficient evidence for a future BTC-to-Cash translation study.

Conversely, a state that predicts terminal underperformance but has no stable relation to pathwise downside may be too weak to support a risk-control interpretation.

The later numerical preregistration must therefore freeze a joint interpretation over both outcome families before any 0060 future outcome is released. It may not discard whichever outcome family is inconvenient after execution.

0060 does not define the economic value of avoiding these losses. No strategy NAV, transaction cost, turnover, CAGR, Calmar or portfolio MDD is computed under this ID.

---

## 7. Outcome-horizon principle

0060 must not select a single future horizon after observing which one looks best.

The numerical preregistration must use a prospectively frozen multi-horizon family. The inherited program horizons `20 / 60 / 120 / 240` are the default design anchor because they already exist in the BRRK trend architecture and prior continuation studies.

However, the exact inferential role of each horizon is a **numerical preregistration decision** and is not finalized by this DESIGN document. Before any historical 0060 target values are computed, preregistration must state:

- the complete mandatory horizon set;
- whether all horizons are co-primary or whether a mechanically justified subset is primary with the remainder mandatory diagnostics;
- a rationale that is based on BTC-to-Cash risk-control semantics rather than any observed 0059 or 0060 result;
- the exact simultaneous success/failure rule that prevents post-hoc winning-horizon selection.

No new `30/40/90/180` horizon search may be introduced after result exposure.

---

## 8. Primary scientific hypothesis

Primary hypothesis:

> Higher `BTC_ABSOLUTE_RISK_STATE_t` is monotonically associated with larger subsequent BTC `TERMINAL_LOSS_t(h)` and larger `ADVERSE_EXCURSION_t(h)` across the prospectively frozen horizon family, with recurrence across chronological history and dependence-aware uncertainty control.

Adversarial alternative:

> The state has no stable monotone information about future BTC absolute downside, or apparent information is confined to one horizon/time segment, disappears under dependence-aware inference, or applies only to transient dips without corresponding terminal cash-relative deterioration.

This is an information/mechanism question. No action threshold is implied by a positive result.

---

## 9. Planned inferential architecture to freeze numerically before execution

The exact numerical/data preregistration is intentionally a separate stage after DESIGN merge.

It must freeze, at minimum:

1. exact immutable UTC daily BTC dataset identity and source provenance;
2. exact evaluation start/end and any already-exposed DEVELOPMENT classification;
3. exact warm-up for the 240-session trend architecture and 252-session causal normalization;
4. exact validity conventions for zero volatility, empty downside/upside semivol sides and persistence initialization;
5. exact mandatory future horizon family;
6. exact origin eligibility and common-origin handling across terminal-loss and adverse-excursion targets;
7. exact primary monotone association statistic(s);
8. exact simultaneous two-outcome/multi-horizon success rule;
9. exact chronological robustness partition and recurrence requirement;
10. exact dependence-aware uncertainty method for overlapping future windows and serial dependence;
11. exact block length, replicate count, seed and quantile convention if moving-block/bootstrap inference is used;
12. exact minimum-support gate;
13. exact non-gating decomposition diagnostics for A1/A2/A3 and raw-coordinate redundancy/effective rank;
14. exact classification precedence;
15. exact immutable result schema, exactly-once attempt semantics and persistence requirements.

No numerical gate may be chosen after any 0060 outcome, rank statistic, chronological block result, decomposition result or plot is visible.

---

## 10. Explicitly forbidden computations under 0060

0060 may not compute, search or select:

- BTC-to-Cash entry threshold;
- Cash-to-BTC re-entry threshold;
- hysteresis;
- persistence required for action;
- minimum holding period;
- cooldown;
- stop loss;
- take profit;
- 100/0, 80/20, 70/30, 50/50 or any other BTC/Cash allocation map;
- continuous `gross = f(state)` curve;
- P5.4/P5.5 gross-map variants;
- a rescue of `EXPOSURE-SMOOTH-0038`;
- transaction-cost optimization;
- turnover optimization;
- strategy NAV;
- terminal portfolio wealth;
- CAGR;
- Calmar;
- portfolio MDD;
- dynamic leverage;
- shorting;
- derivatives;
- 4h/intraday rescue;
- ETH/SOL relative timing;
- Beta-to-BTC timing;
- stablecoin-liquidity features;
- on-chain holder-cost features;
- volume/OBV/breadth/correlation features;
- funding/perp-basis/options features;
- macro/rates/equity features;
- fitted probability model;
- HMM;
- changepoint search;
- BOCPD;
- CUSUM threshold search;
- Kalman-state search;
- tree/boosting/neural model;
- feature tournament;
- same-ID component deletion/reweighting after result exposure.

The eight raw coordinates and three axes are frozen as one primary representation family. Descriptive component outputs create no authority to prune the state.

---

## 11. Relationship to 0059 and anti-rescue boundary

0060 must not be interpreted as "0059 but using BTC instead of Beta" in a way that preserves failed 0059 selection freedom.

The scientifically material differences are:

```text
0059 asks relative defensive takeover       BTC vs symmetric Beta
0060 asks absolute gross-risk deterioration BTC vs nominal Cash

0059 state contains Beta/BTC relative axis  yes
0060 state contains any relative asset axis no

0059 target is relative continuation        yes
0060 targets absolute terminal/path loss    yes

0059 could conceptually choose crypto asset no direct gross exit
0060 could only, after future PASS + new ID, motivate gross-risk translation
```

The 0059 favorable 20d value, component-level correlations and failed long-horizon results may not determine 0060 horizon selection, state weights or pass/fail gates.

---

## 12. Relationship to 0044/0045/0046 and anti-trigger boundary

0060 intentionally borrows only **feature-family architecture**, not the 0045/0046 action architecture.

0060 uses:

- trend disagreement;
- price structure;
- volatility/downside asymmetry;
- causal 252-session standardization;
- equal-weight low-dimensional aggregation.

0060 does not use:

- 0043 event peaks as labels;
- TRUE_EXHAUSTION / CONTINUATION_FALSE_TOP taxonomy;
- WATCH/RISK/RECOVERY states;
- 0045 persistence or hysteresis thresholds;
- 0046 pulse detector;
- 0046 ARL0 calibration;
- any event-clock or onset window.

A 0060 PASS would therefore not rescue 0045 or 0046. It would establish only that a BTC-only continuous absolute-risk state contains information about future downside.

---

## 13. Result-informed status and exposure accounting

0060 is explicitly result-informed by prior researcher-exposed DEVELOPMENT evidence.

At minimum the later registry lineage must acknowledge:

- 0043 / 0044 for low-dimensional deterioration-family evidence;
- 0045 / 0046 for failed trigger-translation evidence;
- `EXPOSURE-SMOOTH-0038` and P5.4/P5.5 for prior gross-map / exposure-translation evidence;
- 0059 for the failed Beta-to-BTC continuation-information mechanism and the explicit separation of BTC-to-Cash as a different layer.

No reusable historical window can become independent OOS merely because 0060 uses a different target.

---

## 14. Stage progression and irreversible boundaries

0060 must preserve the governed stage sequence:

```text
1. DESIGN
2. DESIGN merge
3. numerical/data PREREGISTRATION
4. PREREGISTRATION merge
5. IMPLEMENTATION-ONLY
6. IMPLEMENTATION merge
7. CONTROLLED-EXECUTION BOUNDARY
8. BOUNDARY merge
9. exactly one valid historical DEVELOPMENT execution
10. immutable CLOSEOUT
```

No stage may silently include the next irreversible scientific boundary.

Before preregistration merge there may be no historical target evaluation.

Implementation-only must be data-agnostic and use synthetic/toy/contract tests only.

Controlled execution must preserve exactly-once semantics with a durable attempt marker before any historical outcome is evaluated.

Once a valid result-bearing attempt is durably consumed, same-ID rerun, recomputation, retuning and rescue are unavailable except a narrowly defined marker-only finalization recovery that performs no scientific remeasurement.

---

## 15. PASS authority

A future 0060 PASS may authorize only:

> eligibility to open a **new research ID** that systematically translates the frozen BTC absolute-risk state into a BTC/Cash gross-risk architecture under separately preregistered threshold/allocation/re-entry/cost/robustness rules.

A PASS does **not** authorize:

- any BTC/Cash threshold;
- any gross level;
- any re-entry rule;
- any strategy modification;
- canonical BRRK modification;
- Phase-6 modification;
- leverage;
- shorting;
- signing;
- order submission;
- production deployment.

The later translation stage, if ever opened, must treat all 0060 historical outputs as exposed DEVELOPMENT evidence.

---

## 16. FAIL / INCONCLUSIVE authority

A future FAIL or INCONCLUSIVE result must be preserved without same-ID rescue.

0060 may not then:

- drop A3 because volatility/downside performed poorly;
- keep only A1 or A2 because they looked favorable;
- add momentum oscillators;
- change the 60-session high window;
- change MA20/10 slope geometry;
- alter RV10/RV30 or semivol windows;
- choose a favorable horizon;
- alter causal normalization;
- alter support or dependence controls;
- add on-chain holder cost;
- add stablecoin liquidity;
- move to 4h;
- define a trigger anyway.

A scientifically distinct new-data hypothesis may be opened under a new research ID only after 0060 closeout, with explicit exposure accounting. For example, an on-chain holder-cost information test would be a new-data fork, not a 0060 rescue.

---

## 17. Production and live-system boundary

0060 cannot change any live or canonical authority.

```text
Canonical BRRK-0011                    NO CHANGE
40/60 Winner lineage                   NO CHANGE
Phase 6                                NO CHANGE
Phase 7                                NO CHANGE
Phase 8                                NO CHANGE
production gross cap                   NO CHANGE
production_authorized_components       []
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

No signer, exchange order path or live execution code may be added by 0060.

---

## 18. Exact next legal step after DESIGN merge

Only after this DESIGN is reviewed, passes standing design-governance/no-drift checks and is merged to `main` may 0060 enter a separate numerical/data preregistration stage.

That preregistration must create the formal central registry owner and freeze:

- immutable dataset identity;
- exact support window;
- exact horizon family and horizon roles;
- exact target-validity conventions;
- exact monotone association statistics;
- exact simultaneous terminal-loss/adverse-excursion interpretation;
- exact temporal recurrence gate;
- exact dependence-aware inference;
- exact minimum support;
- exact classification precedence;
- exact immutable result schema;
- exactly-once execution semantics.

No historical 0060 target, state/outcome correlation, chronological block result, bootstrap result, strategy NAV or gross-risk economic result may be computed during DESIGN or before the later preregistration is merged.

---

## 19. Design conclusion

0060 opens one narrow question:

> Before trying to decide how much Cash to hold, can a simple causal BTC-only structural deterioration state identify periods in which BTC itself is more exposed to future absolute downside?

The candidate state is intentionally low-dimensional, equal-weight and price-only. It combines:

```text
A1   BTC fast/slow trend disagreement + persistence
A2   BTC price-structure deterioration
A3   BTC volatility/downside asymmetry
```

The future outcomes separate terminal cash-relative loss from pathwise adverse excursion. No trigger, gross map or trading economics exist under this ID.

A strong result may justify a later translation study under a new ID. A weak, contradictory or dependence-fragile result closes this exact mechanism without adaptive rescue.
