# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P4.4 — execute the preregistered LEVERAGE-0040 search/stress suite exactly once
```

PR #88 merged the final pre-run prerequisites as:

`8d512479c5b2a0522409afbf0b63b817de6c6fe0`

## All pre-run gates are now closed

```text
P4.1 defensive scaler             frozen 0 .. 1
LEVERAGE-0039                    STOPPED_PRE_RUN / NO RESULT / DO NOT REUSE
LEVERAGE-0040                    PREREGISTERED / MERGED / NOT RUN
two-layer cap=1 wiring           PASS / MERGED
liquidation-distance model       PASS / MERGED
>1 multiplier policy             FROZEN PRE-RESULT / MERGED
production gross cap             1.0 unchanged
production authorization         none
```

`production_authorized_components = []` remains unchanged.

## Frozen multiplier policy

```text
leverage_multiplier = 1 + (candidate_cap - 1) × frozen_defensive_scale
final_scale = defensive_scale + (candidate_cap - 1) × defensive_scale²
candidate caps = 1.00 / 1.10 / 1.20 / 1.30
```

Do not alter this formula, its allowed inputs, or the cap grid after observing results under `LEVERAGE-0040`.

## Frozen liquidation model

`research/leverage_0040/P4_3_LIQUIDATION_MODEL_V1.json`

`research/leverage_0040/liquidation_model.py`

Uses the frozen Hyperliquid cross-margin snapshot and requires explicit cross-account equity + actual perp notionals. Spot collateral and Portfolio Margin are not assumed. Missing accounting fails closed.

## Frozen LEVERAGE-0040 study

```text
research caps                1.00 / 1.10 / 1.20 / 1.30
operating MDD candidates     35% / 40% / 45% / 50%
frozen defensive tail gate  20% CVaR/CDaR
cost grid                    5 / 10 / 20 / 50 bps
catastrophe boundary         70%
```

Mandatory benchmarks:

- BTC buy-and-hold;
- BTC/ETH/SOL/BNB equal-weight buy-and-hold;
- frozen corrected BRRK <=1;
- each P4 candidate.

Mandatory evidence/stress:

- full machine-readable candidate matrix;
- matched 5/10/20/50 bps economics;
- Hyperliquid native funding common-window panel and preregistered debit-spike stress;
- Binance full-history proxy only as a stress proxy, never Hyperliquid level estimate;
- 2021 spring, 2021 Nov/bear transition, 2022, 2024, 2025, recent 2026 windows;
- synthetic gap and volatility shocks;
- degraded fill/depth/capacity scenarios;
- liquidation-distance table;
- start-date robustness;
- stationary-block bootstrap;
- final select/fail decision without post-result retuning.

## PR #88 evidence

Final head `9ed8c627afd9800f8c4a8cf79246a07bc89e6108`:

- prerequisite #4 / `31178219708`: SUCCESS, 14 passed
- Phase 0 #149 / `31178220870`: SUCCESS, 257 passed + 5/5 integration
- Research #55 / `31178223443`: SUCCESS
- P3.2 parity #42 / `31178219593`: SUCCESS
- P4 cap=1 #8 / `31178220456`: SUCCESS
- latest governance #209 / `31178603896`: SUCCESS
- merge `8d512479c5b2a0522409afbf0b63b817de6c6fe0`

## Still blocked

```text
LEVERAGE-0040 SEARCH RUN:       NO
RESULT SELECTED:                NO
OPERATING BUDGET FROZEN:        NO
PRODUCTION >1 RUNTIME:          NO
PRODUCTION AUTHORIZED:          NO_CHANGE
```

Also blocked/separate:

- any rescue/retune after results under 0040;
- search >1.30 without new experiment ID;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response redesign;
- shorts / XRP target exposure;
- P5 exit intelligence;
- production leverage authorization.

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
merge docs-only post-#88 normalization
-> fresh LEVERAGE-0040 search branch from normalized main
-> implement result runner strictly from frozen prereg + multiplier + liquidation contracts
-> execute complete suite exactly once
-> commit immutable result artifacts
-> P4.5 select/fail decision
-> P4.6 remains separate production gate
```
