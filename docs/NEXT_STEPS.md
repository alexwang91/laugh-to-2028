# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P4.3 LEVERAGE-0040 two-layer runner + cap=1 parity
```

PR #84 corrected the leverage architecture before any leverage search and merged as:

`5cfc7996ef59cc6552d1ec5bdfbc74affdaf53b4`

## Frozen authority

```text
P4.1 defensive scaler       frozen 0 .. 1; unchanged
LEVERAGE-0039              STOPPED_PRE_RUN / NO RESULT / DO NOT REUSE
LEVERAGE-0040              PREREGISTERED / MERGED / NOT RUN
production gross cap       1.0 unchanged
production authorization   none
```

`production_authorized_components = []` remains unchanged.

## LEVERAGE-0040 architecture

```text
BRRK directional weights
× frozen defensive_scale in [0,1]
× separate leverage_multiplier in [1, candidate cap]
= final target economic exposure
```

The frozen defensive selector may not be extended or reinterpreted above 1.0.

Research caps:

```text
1.00 / 1.10 / 1.20 / 1.30
```

At cap `1.00`, leverage multiplier is identically `1.0`, therefore the complete historical path must reproduce frozen BRRK before any >1 candidate is evaluated.

## Preregistered risk/economic gates

```text
operating MDD candidates     35% / 40% / 45% / 50%
frozen defensive tail gate  20% CVaR/CDaR
cost grid                    5 / 10 / 20 / 50 bps
catastrophe boundary         70%
```

Mandatory benchmarks:

- BTC buy-and-hold;
- BTC/ETH/SOL/BNB equal-weight buy-and-hold;
- frozen corrected BRRK-0011 <=1;
- P4 leverage candidates.

Mandatory stresses:

- 2021 spring crash;
- 2021 November/bear transition;
- 2022 severe drawdown;
- 2024 identified stress;
- 2025 multi-peak/deleveraging year;
- recent 2026;
- synthetic gap/volatility shocks;
- Hyperliquid native funding debit 2x/3x/5x stress;
- degraded depth/slippage and partial-fill/capacity stress;
- liquidation distance using frozen Hyperliquid margin metadata.

Funding remains implementation cost/stress only. F23 is separate.

## Frozen Hyperliquid margin snapshot

`research/leverage_0039/hyperliquid_margin_snapshot.json`

```text
captured_at_utc      2026-08-07T09:11:25Z
relevant SHA-256     38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd
raw meta SHA-256     ef4b108e65806d05dab615f533dd113fd86210d2e55a82a005fcad89a7f9aff8
```

This is pre-result research evidence and may be reused by the 0040 runner. It is not production authorization.

## PR #84 evidence

Final head `19711b85d3ab4bf1abae28dfd25926a7e682d6d2`:

- Phase 0 #140 / `31174963182`: SUCCESS
- Research evidence #46 / `31174960649`: SUCCESS
- P3.2 parity/golden #33 / `31174960611`: SUCCESS
- margin snapshot #15 / `31174960599`: SUCCESS
- latest governance #194 / `31175158261`: SUCCESS
- merge `5cfc7996ef59cc6552d1ec5bdfbc74affdaf53b4`

The pre-run architecture review found `DRIFT_2`; the validated correction restored `DRIFT_0` before any leverage result existed.

## Still blocked

```text
LEVERAGE-0040 SEARCH RUN:     NO
RESULT SELECTED:              NO
OPERATING BUDGET FROZEN:      NO
>1 RUNTIME IMPLEMENTED:       NO
CAP=1 LEVERAGE PARITY:        NOT RUN
PRODUCTION AUTHORIZED:        NO_CHANGE
```

Also blocked/separate:

- search >1.30 without a new experiment ID;
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
merge docs-only normalization
-> fresh P4.3 LEVERAGE-0040 runner branch from normalized main
-> implement separate post-defensive leverage multiplier
-> prove cap=1 exact historical parity
-> validate liquidation-distance calculation against frozen margin snapshot
-> only then execute LEVERAGE-0040 exactly once
-> run preregistered P4.4 stress suite
-> P4.5 select/fail decision
-> P4.6 separate deployment cap / production authorization gate
```
