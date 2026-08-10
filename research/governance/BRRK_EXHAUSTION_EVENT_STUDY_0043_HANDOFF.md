# BRRK-EXHAUSTION-EVENT-STUDY-0043 handoff

## State

`COMPLETE DEVELOPMENT DIAGNOSTIC / NO PROMOTION AUTHORITY`

The diagnostic was frozen before result execution and ran exactly once in GitHub Actions run `31381953131`, attempt 1. Full output remains artifact-bound by `research/governance/BRRK_EXHAUSTION_EVENT_STUDY_0043_EXECUTION.json`; the permanent interpreted result is `BRRK_EXHAUSTION_EVENT_STUDY_0043_RESULT.md`.

## Main finding

A genuine-vs-continuation distinction exists in the historical DEVELOPMENT data, especially for severe drawdowns, but the first equal-weight absolute trigger is too insensitive for use as a dynamic gross controller.

Primary `-15%` event panel: 9 TRUE / 6 CONTINUATION / 1 AMBIGUOUS. `PRE14_7` total AUC is `0.7333`; F7 BRRK disagreement `0.7556`, F4 volatility/downside `0.7111`, F1 momentum decay `0.6889`, F2 price structure `0.6889`. In the severe `-20%` panel, `PRE14_7` total AUC rises to `0.8571`.

The frozen 80th-percentile / 3-day total-score warning catches only 2/9 primary true events, although it generates 0/6 continuation false triggers and leads the two hits by 10 and 21 days. This negative evidence prevents direct threshold promotion.

## Methodology limitations retained

- 48 raw features have only about 7.20 effective dimensions; 14 pairs have absolute correlation >=0.85 and one F1/F7 state variable is an exact duplicate.
- local peaks are not fully independent macro episodes; several occur within the same broad drawdown.
- volume/OHLCV is researcher-exposed Binance retrospective DEVELOPMENT data.
- user-provided dates were sanity checks only and were not used to define labels or thresholds.

## Authority

```text
canonical BRRK changed      false
Phase 6 changed             false
portfolio economics run     false
production authorized       false
signature authorized        false
order submission authorized false
```

## Next legitimate step

If this line continues, create a new result-informed research ID before changing feature weights, removing correlated variables, defining a final trigger, mapping signal to gross exposure, or running any portfolio-economic counterfactual. The next design should be low-dimensional, deduplicated, and episode/block-aware.
