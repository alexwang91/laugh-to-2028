# P4 leverage architecture correction — 2026-08-07

Status: **pre-run correction; no leverage result exists**

## Finding

The Master Plan defines dynamic leverage as:

```text
BRRK directional weights
× regime / risk defensive scaler
× optional leverage multiplier
= final target economic exposure
```

The original `LEVERAGE-0039` preregistration instead proposed extending the upper bound of the frozen corrected defensive selector itself from `1.0` to `1.10 / 1.20 / 1.30`.

The frozen BRRK chain computes:

```text
meta_scale = corrected_selector(...)
defensive_scale = 1 - P(RISK_OFF) * (1 - meta_scale)
defensive_scale = clip(defensive_scale, 0, 1)
```

With `meta_scale > 1`, keeping the clip prevents any >1 final defensive scale. Removing the clip would make higher `P(RISK_OFF)` increase exposure whenever `meta_scale > 1`, reversing the intended defensive semantics.

This contradiction was identified before any `LEVERAGE-0039` search, candidate matrix, selection or economic result existed.

## Decision

```text
LEVERAGE-0039 = STOPPED_PRE_RUN
result          = NO_RESULT_EVER_PRODUCED
```

The stopped preregistration is preserved and may not be rewritten or rescued.

A new experiment ID is required because the economic architecture changes materially:

```text
LEVERAGE-0040
```

Its preregistered architecture is:

```text
frozen defensive_scale ∈ [0,1]
separate leverage_multiplier ∈ [1, cap]
final_scale = defensive_scale × leverage_multiplier
```

At cap `1.00`, the multiplier is identically `1.0`, so the complete path must reproduce the frozen BRRK baseline exactly before any >1 candidate is evaluated.

## Master Plan coverage restored

`LEVERAGE-0040` additionally makes the following previously omitted requirements mandatory before first run:

1. BTC buy-and-hold benchmark;
2. BTC/ETH/SOL/BNB equal-weight buy-and-hold benchmark;
3. explicit funding-spike stress;
4. explicit degraded-fill/depth/capacity stress.

The already captured official Hyperliquid margin snapshot remains valid pre-result implementation evidence and is reused for liquidation-distance modeling.

## Boundaries unchanged

This correction does not:

- change BRRK-0011 relative weights, HMM, features or semantic states;
- change the corrected 0–1 defensive selector;
- change the 20% scenario CVaR/CDaR budget;
- change P3.3 or P3.4 semantics;
- promote EXPOSURE-SMOOTH-0038;
- absorb F23 funding-response logic;
- add short or XRP target exposure;
- add P5 exit logic;
- authorize production gross >1;
- authorize production trading.

`production_authorized_components = []` remains unchanged.

## Next gate

```text
validate/merge the pre-run correction
-> fresh P4.3 runner branch
-> implement two-layer leverage runner
-> cap=1 exact historical parity
-> execute LEVERAGE-0040 once
-> preregistered stress suite
-> selection/failure decision
-> separate deployment/production authorization gate
```
