# P5.2 Feature Evidence Closeout

Status: **COMPLETE / IMMUTABLE EVIDENCE / DESCRIPTIVE CLOSEOUT**  
Study: `P5.2-FEATURE-FAMILIES-V1`  
Immutable result commit: `61d585afb64afbe3ead6422e7e62cde6c59fad40`  
Immutable summary SHA256: `3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627`

## What P5.2 did and did not do

P5.2 measured frozen causal feature families against the already-frozen `P5.1-EVENT-TAXONOMY-V1` events and high-volatility non-top controls.

It produced immutable descriptive evidence for 29 available features across four families:

- BTC trend maturity;
- momentum exhaustion;
- leadership migration;
- canonical breadth.

All 29 available features passed the frozen coverage gate. Six requested data families remain explicitly `DATA_SOURCE_PENDING`: BTC dominance, broad-market breadth, comparable historical funding, historical open interest, historical basis/premium and liquidation history.

P5.2 did **not** select a final feature set, state thresholds, a state machine, production behavior or production authorization. The immutable result explicitly records:

```text
feature_set_selected = false
state_thresholds_selected = false
selection.status = DESCRIPTIVE_EVIDENCE_ONLY
production_authorized = false
```

## R2 recovery provenance

The first one-time run `31217880218` failed only while serializing an already-computed `Series` because pandas 3.0 does not accept `Series.reset_index(names=...)`.

No immutable result was written, validator did not run, result commit was skipped, and feature metrics were not printed.

The audited correction `P5.2-POST-COMPUTE-SERIALIZATION-R2` changed only the pandas serialization path to equivalent `rename -> to_frame -> index.name -> reset_index` semantics. It changed no event, feature, lookback, bucket, coverage threshold or research statistic and used no observed feature metrics to choose the correction.

R2 run `31218363897` completed calculation, immutable validation and result commit successfully.

## Post-result descriptive diagnostics

A separate non-authorizing closeout analyzer reads only the immutable P5.2 CSVs and writes derived diagnostics under:

`research/analysis/p5_2_closeout/`

The analyzer snapshots all immutable result-file hashes before and after execution and must prove zero mutation. Its metadata explicitly sets:

```text
analysis_status = POST_RESULT_DESCRIPTIVE_DIAGNOSTICS_ONLY
selection_or_threshold_authority = NONE
```

The primary diagnostic buckets are the frozen P5.1 `target_lead` (-14..-7d) and `near_event` (-6..0d) windows.

## Family-level result

No single family dominates the evidence strongly enough to justify a one-factor cycle-top model.

Across non-control events in the two primary buckets, median absolute robust-z versus pooled controls is approximately:

| Family | Median abs-z | P90 abs-z | abs-z >= 2 count |
| --- | ---: | ---: | ---: |
| BREADTH | 0.674 | 1.949 | 2 |
| MOMENTUM_EXHAUSTION | 0.674 | 1.803 | 8 |
| LEADERSHIP_MIGRATION | 0.610 | 2.008 | 11 |
| BTC_TREND_MATURITY | 0.551 | 2.300 | 19 |

Interpretation: all four families contain useful structure, but the evidence is heterogeneous and state-dependent. P5.3 should combine complementary families rather than promote a single indicator or family.

## Structural evidence that matters for P5.3

The statements below are **P5.3 design constraints / evidence priorities**, not feature promotion or threshold selection.

### 1. Volatility state is strong context, but not a terminal-top discriminator by itself

`btc_rv20_ann` and `btc_rv20_to_rv60` repeatedly show large separation from the high-volatility controls.

However, the sign/pattern appears across terminal, second-wind, nonterminal-toplike and deterioration contexts. For example, `btc_rv20_ann` is below the pooled high-vol controls in all four groups, with especially large absolute separation in second-wind, nonterminal-toplike and deterioration events.

Therefore volatility state is useful as **regime texture / maturity context**, but treating low or contracting realized volatility as a direct terminal-top trigger would create false positives.

### 2. ETH/BTC leadership migration is a strong late-bull / rotation marker, not an automatic exit signal

`eth_btc_log_return_20d` is one of the strongest near-event features:

```text
terminal near-event             robust-z ~ +3.39
second-wind near-event median   robust-z ~ +2.50
nonterminal-toplike median      robust-z ~ +3.11
```

This is exactly why BTC leadership loss cannot be interpreted as automatically bearish. Strong ETH relative leadership appears in terminal and nonterminal/second-wind structures.

P5.3 therefore needs an explicit `LATE_BULL_ROTATION` state separated from de-risk / FLAT states.

`eth_btc_log_return_40d` provides additional persistence context; BNB relative strength is secondary and more context-dependent. SOL/BTC relative features are weaker/more mixed in this V1 evidence.

### 3. Price-versus-RSI divergence is the strongest terminal lead hypothesis, but there is only one terminal event

For the sole explicit terminal event (2021 November), `btc_price_rsi_rank_divergence_20d` is the strongest `target_lead` separator:

`robust-z ~ +3.37`.

The same feature is materially weaker or opposite-signed in the second-wind median and weaker in nonterminal-toplike/deterioration groups.

This makes divergence an important **terminal-hazard hypothesis** for P5.3, but not a validated terminal rule. P5.1 V1 contains only one explicit terminal event, so cross-cycle terminal robustness cannot be established from this evidence alone.

P5.3/P5.5 must prevent this one 2021 case from becoming a hand-tuned threshold.

### 4. Breadth acceleration helps describe transition shape, but is not terminal-specific in the lead window

`breadth_acceleration_10d` is strong in the terminal `target_lead` bucket (`robust-z ~ +2.70`), but is also elevated in second-wind and nonterminal-toplike lead windows.

Near the terminal event it remains positive (`~ +1.35`) while the grouped second-wind/nonterminal-toplike medians are weaker/negative. This suggests that **trajectory / change of breadth** may be more useful than breadth level alone.

P5.3 should test breadth as a transition/state feature rather than a standalone exit switch.

### 5. Raw RSI level alone is insufficient

The terminal `target_lead` values of daily RSI14/28 and 4h RSI14/28 are not exceptional versus controls. Daily RSI14 becomes more separated near the terminal event, but similar or larger near-event separation also appears in nonterminal-toplike and deterioration contexts.

The 4h RSI family is particularly strong in the late-2025 deterioration near-event context, not in the terminal target-lead window.

Therefore P5.3 should not encode `RSI > X = top`. RSI is more defensible as part of an exhaustion/failure-transition state combined with divergence, volatility and leadership structure.

### 6. Distance from high helps distinguish second-wind from top-like structure near the event

`btc_distance_from_90d_high` shows opposite/group-dependent behavior: second-wind observations differ from terminal/nonterminal-toplike/deterioration observations, especially near event anchors.

This makes high-distance / high-level structure a useful state-context feature, not an isolated trigger.

### 7. Several simple trend-level features are lower-priority structural inputs

Raw 20d/40d BTC returns, simple annualized trend slopes and KAMA slope show relatively modest separation in the primary buckets compared with volatility context, ETH/BTC leadership and selected exhaustion/transition features.

This does not delete them from the evidence. It means P5.3 should avoid giving them privileged state-defining authority without additional validation.

### 8. Discrete breadth features need different treatment from continuous robust-z rankings

Several discrete breadth/consolidation variables have zero MAD in the pooled controls for some buckets, so robust-z is undefined. Absence from robust-z rankings is therefore **not evidence that the variable is useless**.

P5.3 should handle such variables as categorical/ordinal state evidence or use a preregistered comparison appropriate to discrete variables rather than retroactively inventing a favorable continuous score.

## P5.3 architecture implications

P5.2 supports a multi-state structure rather than a scalar top score.

The P5.3 state vocabulary remains:

```text
NORMAL_BULL
BTC_LEADERSHIP_MATURING
LATE_BULL_ROTATION
EXHAUSTION_WATCH
DE_RISK_1
DE_RISK_2
FLAT
```

The strongest architectural implication is:

```text
low/contracting volatility alone                  != terminal top
ETH/BTC leadership / broad alt participation      != automatic bearishness
rotation + healthy structure                      -> LATE_BULL_ROTATION candidate
exhaustion/divergence + structure deterioration   -> EXHAUSTION_WATCH / de-risk candidate
hard multi-family deterioration                   -> stronger de-risk / FLAT candidate
```

P5.3 must preserve BRRK relative ranking. The cycle layer controls total directional risk state, not which BRRK asset wins the relative ranking.

## Mandatory P5.3 constraints

1. Do not move P5.1 events/anchors.
2. Do not alter the immutable P5.2 result.
3. Do not convert post-result descriptive rankings into hand-picked thresholds.
4. Do not claim cross-cycle terminal robustness from one terminal event.
5. Do not fabricate BTC dominance, OI, funding, basis or liquidation proxies under the missing feature names.
6. Keep `LATE_BULL_ROTATION` distinct from de-risk states.
7. Use multi-family evidence; no single RSI/volatility/relative-strength switch.
8. Preserve BRRK-0011 relative asset ranking.
9. P5.3 is research only; production authorization remains none.

## Closeout

```text
P5.1 = COMPLETE / MERGED / FROZEN
P5.2 = COMPLETE / IMMUTABLE EVIDENCE / DESCRIPTIVE CLOSEOUT
P5.2 final feature-set selection = NONE
P5.2 state-threshold selection = NONE
production gross cap = 1.0
production_authorized_components = []
next = P5.3 STATE MODEL RESEARCH
```
