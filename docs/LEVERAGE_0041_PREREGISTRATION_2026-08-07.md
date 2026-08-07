# LEVERAGE-0041 preregistration — leverage architecture / sweet spot

Date: 2026-08-07
Status: **PREREGISTERED BEFORE FIRST RUN**
Base main: `14dd9f2fb828d860b8552816814982dc4bd89b10`

## Purpose

LEVERAGE-0040 is complete, immutable and `NO_PROMOTION`. This follow-on experiment does not rescue or reinterpret that result. It tests a materially different implementation architecture motivated by the observation that the 1.20 region produced attractive historical CAGR but failed funding, liquidation-distance and synthetic-gap hard gates under the LEVERAGE-0040 architecture.

The objective remains:

```text
maximize expected long-run compounded wealth / CAGR
subject to survival, drawdown, catastrophic, funding, liquidation,
execution-capacity and parameter-robustness constraints
```

Risk is a hard constraint, not a quantity to minimize for its own sake.

## Frozen experiment ID

`LEVERAGE-0041`

Do not reuse LEVERAGE-0039 or LEVERAGE-0040. Do not modify the immutable LEVERAGE-0040 result or digest.

Immutable predecessor summary SHA256:

`3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0`

## Frozen candidate region

Requested research caps:

```text
1.00 / 1.05 / 1.10 / 1.15 / 1.20 / 1.25 / 1.30
```

`1.20` is the focal design point only. It receives no favorable selection treatment.

The selected sweet spot, if any, must be an **interior** cap with both immediate neighbors passing every hard gate, inside a contiguous all-pass region of at least three caps. If passing caps in the same qualifying region are within 1.0 percentage point of annualized CAGR, select the lower cap.

## Frozen strategy layer

No BRRK research economics are retuned:

- directional target: BRRK-0011;
- target assets: BTC / ETH / SOL / BNB;
- XRP: feature-only;
- defensive scale remains `[0,1]`;
- decision boundary remains 00:00 UTC daily;
- BRRK relative targets, HMM/regime features, semantic states, defensive-scale formula, P3.3 rebalance semantics and P3.4 contribution handling remain frozen.

At cap 1.00, the **requested economic target path** must exactly reproduce the frozen BRRK-0011 <=1 target path before any >1 candidate is valid. Implementation PnL is allowed to differ because LEVERAGE-0041 intentionally changes routing/collateral architecture.

## New implementation architecture

Architecture ID:

`SPOT_FIRST_BASE_PLUS_PERP_OVERLAY_V1`

### Explicit collateral reserve

- 25% of NAV is reserved as explicit USDC-like cross-margin collateral;
- reserve return is modeled as 0%;
- the reserve may not also be counted as spot financing;
- no external or hidden collateral is assumed.

### Base long exposure

For BTC / ETH / SOL:

- use verified P2.4 spot-first routing when identity, capacity and cost evidence permits;
- total spot financing may not exceed 75% of current NAV;
- any residual base-long exposure is implemented with perp.

For BNB:

- retain canonical `PERP_ONLY_DEFAULT`.

Any short economic exposure remains perp-only. This experiment does not introduce or optimize a new short strategy.

### Incremental leverage

Economic exposure above the cap=1.00 target is perp-only.

The overlay may scale the frozen target but may not alter cross-asset relative weights or defensive-state semantics.

## Funding-aware overlay reduction

Funding is still an implementation cost, not alpha.

At each legal daily boundary:

1. compute trailing 168h realized Hyperliquid funding debit divided by average absolute routed perp notional;
2. convert to bps/day;
3. clamp favorable credits to zero for the reducer;
4. apply:

```text
debit <= 5 bps/day       -> overlay funding scale = 1.0
5 < debit < 10 bps/day   -> overlay funding scale = (10 - debit) / 5
debit >= 10 bps/day      -> overlay funding scale = 0.0
missing required data     -> overlay funding scale = 0.0
```

This rule may only reduce incremental leverage. It may never increase exposure above the requested cap. The 5/10 bps thresholds are frozen before the first LEVERAGE-0041 result and may not be optimized afterward.

## Hard risk gates

The predecessor safety boundaries are not relaxed:

- operating DD candidate budgets: 35% / 40% / 45% / 50%;
- catastrophic drawdown limit: 70%;
- frozen defensive scenario CVaR/CDaR budget: 20%;
- historical crash windows retained;
- synthetic one-day uniform gaps through -50% retained;
- cross-asset gap scenarios retained;
- worst-20d volatility multipliers 1.5x / 2x / 3x retained;
- degraded depth/fill stresses retained;
- native Hyperliquid funding plus 2x / 3x / 5x debit stress retained;
- missing required evidence fails closed.

### Liquidation-distance gate

Liquidation analysis must use **actual routed perp notionals** and the explicit 25% cash reserve. Spot notional may not be misclassified as perp notional or silently treated as additional cross-margin collateral.

A promotable candidate must have no modeled liquidation in mandatory historical/synthetic stress and must maintain modeled adverse-move distance to liquidation **strictly greater than 55%** in every promotable candidate state. This is the existing 50% maximum preregistered one-day gap plus a 5 percentage-point buffer.

## Robustness

Frozen start dates:

`2022-12-10 / 2023-03-01 / 2023-06-01 / 2024-01-01`

Stationary-block bootstrap mean block lengths:

`7 / 21 / 63 days`

Bootstrap resamples: `10000`

Fixed seed: `20260807`

No >1 candidate is promotable unless the full start-date/bootstrap requirements and the broad-region rule pass.

## Benchmarks

Every material result must report:

1. BTC buy-and-hold;
2. BTC/ETH/SOL/BNB equal-weight buy-and-hold;
3. frozen corrected BRRK-0011 <=1 baseline;
4. immutable LEVERAGE-0040 cap=1.00 comparator.

Matched execution-cost cases remain 5 / 10 / 20 / 50 bps per absolute weight change, with P2.3/P2.4 route economics itemized and no silent double counting of VWAP/slippage.

## Selection rule

Do not select the best isolated in-sample point.

Among caps inside a qualifying contiguous all-pass region, select the highest matched after-cost CAGR. Apply the 1.0 percentage-point near-tie rule in favor of the lower cap. A boundary cap cannot be the sweet spot because it lacks passing neighbors on both sides.

## Production boundary

This experiment is research-only.

Even if LEVERAGE-0041 promotes a research cap, the cap presented to P4.6 is the **next lower preregistered grid point** and may never exceed 1.20 under LEVERAGE-0041.

`production_authorized_components = []`

Current production gross cap remains `1.0`.

## RUN_ONCE boundary

Preregistration does **not** authorize execution.

Before the one-time study can run, the implementation contract, target-path parity, input-evidence, liquidation-model and applicable CI/governance gates must be green. After that, a separate explicit owner `RUN_ONCE` instruction is required.

After any LEVERAGE-0041 candidate result is observed, no cap grid, funding threshold, reserve, stress threshold, benchmark, seed, selection rule or economic implementation may be retuned under the same experiment ID.
