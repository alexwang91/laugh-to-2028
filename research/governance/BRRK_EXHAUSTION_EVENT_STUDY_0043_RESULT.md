# BRRK-EXHAUSTION-EVENT-STUDY-0043 — RESULT

Status: **COMPLETE / DEVELOPMENT DIAGNOSTIC ONLY / NO PROMOTION AUTHORITY**  
Execution: GitHub Actions `31381953131`, attempt 1  
Artifact: `9060216534` / `sha256:6df40bbe0112082f045cd4da7b461753382c6980a348609a35bed9967f1520c4`  
Full result SHA256: `1ca030e544d6e3391143c9ec47e202f9585ce8a846e0e46be583c31258958b43`  
Summary SHA256: `82579688952e990809a01044378b40cd44ceba84142307686cfa8ae05158c278`

## Scope

The frozen diagnostic scanned all 1,332 canonical BRRK sessions from `2022-12-10` through `2026-08-02`. It mechanically detected 16 local-peak candidates and separated them using the frozen competing-barrier taxonomy. User-provided historical dates were sanity checks only and did not determine labels, thresholds, feature weights, or score construction.

No portfolio counterfactual, gross-risk mapping, target modification, strategy promotion, Phase-6 modification, production authorization, signing, or order submission was executed.

## Event taxonomy result

```text
10% downside panel: 12 TRUE_EXHAUSTION / 4 CONTINUATION / 0 AMBIGUOUS
15% downside panel:  9 TRUE_EXHAUSTION / 6 CONTINUATION / 1 AMBIGUOUS
20% downside panel:  7 TRUE_EXHAUSTION / 6 CONTINUATION / 3 AMBIGUOUS
```

The 15% panel remains the primary descriptive panel. The 10% and 20% panels remain mandatory robustness evidence.

## Primary 15% panel — one-to-two-week warning window

`PRE14_7` means the mean causal score from 14 through 7 days before the mechanically detected local peak.

```text
EXHAUSTION_SCORE        AUC 0.7333
F7 BRRK disagreement   AUC 0.7556
F4 volatility/downside AUC 0.7111
F1 momentum decay      AUC 0.6889
F2 price structure     AUC 0.6889
F3 volume confirmation AUC 0.6000
F6 correlation stress  AUC 0.5778
F5 breadth/relative    AUC 0.5111
```

The total score therefore contains measurable advance separation, but the information is unevenly distributed across feature families. The strongest primary early-warning evidence is concentrated in BRRK internal long/short-horizon disagreement, volatility/downside asymmetry, price structure, and momentum decay rather than in breadth or correlation alone.

## Primary 15% panel — final week before peak

```text
EXHAUSTION_SCORE        AUC 0.7333
F4 volatility/downside AUC 0.8444
F7 BRRK disagreement   AUC 0.8222
F2 price structure     AUC 0.7333
F3 volume confirmation AUC 0.7111
F5 breadth/relative    AUC 0.7111
F6 correlation stress  AUC 0.6000
F1 momentum decay      AUC 0.4222
```

Momentum-decay information is strongest earlier and does not remain monotonically high into the final week. By contrast, volatility/downside stress and BRRK internal disagreement strengthen closer to the local peak.

## Severe 20% drawdown panel

For the most consequential local tops, separation is materially stronger.

`PRE14_7`:

```text
EXHAUSTION_SCORE        AUC 0.8571
F7 BRRK disagreement   AUC 0.8000
F2 price structure     AUC 0.7714
F4 volatility/downside AUC 0.7714
F1 momentum decay      AUC 0.7143
F6 correlation stress  AUC 0.7143
F3 volume confirmation AUC 0.6571
F5 breadth/relative    AUC 0.5714
```

`PRE7_0`:

```text
EXHAUSTION_SCORE        AUC 0.7429
F4 volatility/downside AUC 0.8571
F7 BRRK disagreement   AUC 0.8286
F2 price structure     AUC 0.8286
F5 breadth/relative    AUC 0.7714
F3 volume confirmation AUC 0.7143
F6 correlation stress  AUC 0.6857
F1 momentum decay      AUC 0.4286
```

This is consistent with a staged exhaustion process: momentum deceleration can appear earlier, then structural/volatility/internal-disagreement evidence becomes more useful near and shortly after the peak.

## Fixed warning-threshold panel — important negative evidence

The frozen total-score threshold panel used trailing 252-session percentiles and three-day persistence. No threshold was selected after result review.

```text
70th percentile: true-top hit 3/9 (33.3%), false trigger 1/6 (16.7%), true leads [10,21,21] days
80th percentile: true-top hit 2/9 (22.2%), false trigger 0/6,       true leads [10,21] days
90th percentile: true-top hit 1/9 (11.1%), false trigger 0/6,       true lead  [16] days
```

Therefore the first equal-weight total score is **not yet a usable absolute trigger**. It provides useful ranking/separation information, but a simple high-percentile rule sacrifices too much sensitivity. Any later trigger design must be a new result-informed research stage; this result may not be rescued by modifying thresholds under ID 0043.

## User-anchor sanity checks

Primary 15% panel:

```text
2023-12-25 -> detected 2023-12-25 / TRUE_EXHAUSTION / 60d min -20.85%
2024-03-31 -> detected 2024-03-31 / TRUE_EXHAUSTION / 60d min -21.95%
2024-11-24 -> nearest 2024-11-22 / AMBIGUOUS at 15% / 60d min -11.77%
2025-01-26 -> nearest 2025-01-18 / TRUE_EXHAUSTION / 60d min -28.74%
2025-10-06 -> nearest 2025-10-08 / TRUE_EXHAUSTION / 60d min -28.01%
```

The November 2024 anchor is mechanically classified as a moderate/slow exhaustion rather than a >=15% 60-session event; it is TRUE_EXHAUSTION in the 10% severity panel. This mismatch is retained rather than changing the frozen 60-session/15% definition.

## Redundancy finding

The audit froze 48 oriented raw features. Their correlation structure shows:

```text
|corr| >= 0.85 pairs                    14
effective-rank participation ratio      7.2046
```

One feature pair is exactly duplicated across family definitions: F1 fast-below-slow trend and F7 slow-fast disagreement have correlation `1.0`. RSI14/RSI28 decay, several volume/OBV transformations, and pairwise-vs-alt/BTC correlation measures are also highly redundant.

This confirms the prior methodological concern: many technical indicators are transformations of the same underlying state and must not be counted as independent votes. ID 0043 is closed against post-result pruning/reweighting. Any deduplicated low-dimensional state model must be frozen under a new research ID.

## Dependence / sample-size limitation

The 16 detected local peaks are not 16 fully independent macro regimes. For example, multiple failed rallies inside the broad 2024 drawdown are separate mechanically detected local peaks. The AUC values are therefore useful DEVELOPMENT diagnostics, not an independent statistical validation. A follow-up must use episode/block-aware validation and preserve this dependence limitation.

## Interpretation

The requested one-to-two-week signal appears **feasible but not yet operationally specified**:

- advance discrimination exists in the frozen data;
- it becomes stronger for the most severe drawdowns;
- the evidence is concentrated in a small number of state dimensions;
- a naive equal-weight absolute threshold is too insensitive;
- the next legitimate stage is a separately frozen, deduplicated state/trigger candidate with episode-aware validation before any portfolio economics are evaluated.

Production/signature/order authority remain false. Canonical BRRK-0011 and Phase 6 remain unchanged.
