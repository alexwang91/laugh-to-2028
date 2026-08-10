# BRRK-EXHAUSTION-STATE-0044

Status: **PREREGISTERED / NOT RUN**  
Governance: **PROGRAM_GOVERNED_V1**  
Authority: **RESEARCH ONLY / NO TRIGGER / NO PORTFOLIO TRANSLATION / NO PRODUCTION AUTHORITY**  
Parent evidence: `research/governance/BRRK_EXHAUSTION_EVENT_STUDY_0043_RESULT.md`

## Purpose

0043 established that the already exposed BRRK history contains measurable one-to-two-week exhaustion discrimination, especially before severe drawdowns, but also showed that 48 raw indicators collapse to roughly seven effective dimensions and that a naive absolute threshold is too insensitive.

0044 is the structural-simplification stage. It does **not** ask how much gross risk to cut and does **not** select a trigger. It asks whether a frozen low-dimensional state representation can preserve the advance signal after repeated local peaks inside the same unrecovered drawdown are treated as dependent observations.

## Frozen primary state representation

Every raw input is recomputed using the exact causal orientation and trailing-252-session z-score semantics from 0043: minimum 60 observations and clipping to `[-3,+3]`.

### S1 — Momentum Deceleration

Equal-weight mean of:

- `f1_trend_decay7`
- `f1_macd_hist_decay5`

RSI14/RSI28 remain acknowledged diagnostic representations but are excluded from the 0044 primary state because 0043 showed substantial oscillator redundancy. They may not be reintroduced under this ID after results are observed.

### S2 — Trend Disagreement

Equal-weight mean of:

- `f7_slow_fast_disagreement`
- `f7_disagreement_persistence`

The exactly duplicated `f1_fast_below_slow` representation is excluded.

### S3 — Price Structure

Equal-weight mean of:

- `f2_prior_peak_shortfall`
- `f2_days_since_high60`
- `f2_ma20_slope10`

This axis is intended to convert visually recognizable failed-high / double-top / lower-high deterioration into causal numeric structure.

### S4 — Volatility / Downside

Equal-weight mean of:

- `f4_rv10_vs_rv30`
- `f4_down_up_semivol`
- `f4_pnl_dd_duration_interaction`

### CORE4

`CORE4 = mean(S1,S2,S3,S4)` with equal axis weights. No fitted coefficients or label-dependent weights are allowed.

## Frozen secondary volume diagnostic

### S5 — Volume Confirmation

Equal-weight mean of:

- `f3_down_up_volume_ratio`
- `f3_price_obv_divergence20`

`CORE5 = mean(S1,S2,S3,S4,S5)` is a **secondary diagnostic only**. It cannot control 0044 pass/fail and cannot rescue a CORE4 failure. Its purpose is to quantify whether the user's requested price-volume confirmation contributes incremental information after the stronger 0043 dimensions are distilled.

Breadth and correlation are excluded from 0044 candidate construction because their 0043 primary PRE14_7 family discrimination was weak. They may not be re-added under this ID after result release.

## Frozen event taxonomy

0044 reuses 0043 exactly:

- centered local peak half-window: 7 days;
- prior 30-session NAV gain >= +5%;
- next-14-session pullback <= -5%;
- 21-day candidate declustering;
- outcome window: 60 sessions;
- fresh-high barrier: +2%;
- downside panels: -10%, -15% primary, -20%;
- labels: `TRUE_EXHAUSTION`, `CONTINUATION_FALSE_TOP`, `AMBIGUOUS`;
- primary warning window: `PRE14_7`;
- secondary near-peak window: `PRE7_0`.

No event definition may be changed after 0044 output is observed.

## Macro-episode dependence rule

The 16 local peaks found in 0043 are not assumed independent. Sorted candidate peaks are grouped mechanically:

1. the first candidate starts an episode;
2. the episode anchor is that candidate's canonical BRRK NAV;
3. later candidates remain in the same episode until canonical BRRK NAV first reaches at least `anchor_nav * 1.02`;
4. the first candidate after that recovery starts a new episode;
5. if the recovery never occurs before the frozen historical end, all later candidates remain in the same episode.

Future NAV is used here only to define retrospective dependence blocks, never as a predictor.

## Cross-episode AUC

Primary discrimination does not count every event pair equally. For each TRUE episode versus CONTINUATION episode pair:

1. compare all usable TRUE-event scores in the TRUE episode with all usable CONTINUATION-event scores in the CONTINUATION episode;
2. compute pairwise concordance with ties worth 0.5;
3. average within that episode pair;
4. average equally across episode pairs.

This prevents one broad drawdown containing multiple failed rallies from receiving disproportionate weight.

A leave-one-episode-out influence panel removes one episode at a time and recomputes the same fixed-score cross-episode AUC. This is an influence/robustness check on exposed DEVELOPMENT history, **not** independent OOS evidence and not a model refit.

## Hard pass gates

A full PASS requires all of the following:

1. at least four usable macro episodes, with TRUE events represented in at least two episodes and CONTINUATION events in at least two;
2. primary -15% `PRE14_7` CORE4 cross-episode AUC >= 0.70;
3. primary -15% `PRE14_7` CORE4 event-level AUC >= 0.68;
4. severe -20% `PRE14_7` CORE4 cross-episode AUC >= 0.75;
5. leave-one-episode-out primary CORE4 cross-episode AUC: minimum >= 0.55 and median >= 0.68;
6. exact four-axis equal-weight construction, causal predictors only, frozen history through 2026-08-02;
7. no canonical, execution, Phase 6, signing, order-submission, or production-authority change.

A failure closes 0044 with no trigger-stage eligibility. CORE5 cannot rescue it.

## Explicitly not allowed under 0044

- trigger threshold search;
- persistence-day search;
- WATCH/RISK/RECOVERY state thresholds;
- gross mapping;
- portfolio counterfactuals;
- fitted feature weights;
- PCA or alternative statistical compression;
- tree/boosting/neural models;
- alternative RSI/MACD variants;
- alternative event barriers or episode rules;
- new data after 2026-08-02;
- canonical or Phase 6 changes.

## Next-stage semantics

Only a full CORE4 PASS can make a **new separately preregistered trigger-design stage** eligible. Even then, the 0044 score is not automatically a trading signal. Trigger design and any later `gross=f(state)` mapping remain separate research stages.
