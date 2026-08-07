# P5.2 Feature Families — Frozen Evidence Plan

Status: **FROZEN BEFORE FIRST FEATURE-EVIDENCE RUN**  
Contract: `P5.2-FEATURE-FAMILIES-V1`  
Base main: `86497cdd663a89ca4d54c898b7acbac1cc07d836`  
Taxonomy: `P5.1-EVENT-TAXONOMY-V1`

## Purpose

P5.2 measures how candidate feature families behave across the frozen P5.1 events and non-top controls.

It does **not** select the final feature set, fit P5.3 state thresholds, rewrite BRRK relative ranking, or authorize production.

The goal is to produce descriptive, causal evidence before state-model design.

## Data authority

### Canonical prices

Daily:

```text
BTCUSDT
ETHUSDT
SOLUSDT
BNBUSDT
XRPUSDT
Binance spot
UTC 1d completed bars
2020-10-01 through 2025-12-31
```

4h momentum:

```text
BTCUSDT
Binance spot
4h completed bars
```

At a 00:00 UTC daily evaluation boundary only the 4h bar completed at or before that boundary is usable. The new 4h bar opening at 00:00 is not usable.

Missing required canonical price data fails closed. No forward fill.

## Available V1 feature families

### BTC trend maturity

- 20d / 40d log return;
- 20d / 40d annualized log-price slope;
- KAMA(10,2,30) gap and 10d slope;
- distance from trailing 90d high;
- consecutive days within 5% of trailing 90d high;
- 20d annualized realized volatility;
- RV20 / RV60 ratio.

### Momentum exhaustion

- daily Wilder RSI14 / RSI28;
- completed-4h Wilder RSI14 / RSI28 sampled at daily boundary;
- 20d price-versus-RSI percentile-rank divergence;
- 14d fraction of RSI14 observations >=70;
- failure distance from the trailing 14d RSI14 maximum.

Daily and 4h RSI are both included. Neither is visually preselected.

### Leadership migration

- ETH/BTC, SOL/BTC, BNB/BTC 20d and 40d relative log returns;
- cross-sectional dispersion of 20d returns across BTC/ETH/SOL/BNB.

Historical BTC dominance remains `DATA_SOURCE_PENDING` until a repository-validated historical source is adopted. It is not replaced with an unnamed proxy.

### Breadth

- fraction of ETH/SOL/BNB outperforming BTC over 20d;
- fraction of ETH/SOL/BNB/XRP outperforming BTC over 20d;
- SOL/BNB high-beta participation versus BTC;
- 10d breadth acceleration;
- contraction from the trailing 10d breadth maximum.

The five-series measure is explicitly **canonical-five breadth**, not total-market breadth. Broader market breadth remains `DATA_SOURCE_PENDING`.

## Data-source gaps carried explicitly

V1 does not fabricate substitutes for:

- BTC dominance;
- broad-market breadth;
- historical open interest;
- continuous historical basis/premium panel;
- liquidation proxy;
- a cross-event funding source with comparable 2021 and 2025 coverage.

These gaps are written to `pending_features.csv` in the result.

## Event evidence

All features are summarized under the unchanged P5.1 relative buckets:

```text
early_warning    -28 .. -15
target_lead      -14 ..  -7
near_event        -6 ..   0
immediate_after   +1 .. +28
medium_after     +29 .. +90
```

For each event × bucket × feature the run reports:

- count;
- mean;
- median;
- min / max;
- first / last;
- last-minus-first delta;
- control median / MAD;
- signed robust-z of event median versus pooled high-volatility controls where MAD > 0.

This is descriptive evidence. P5.2 does not choose P5.3 thresholds from these outputs.

## Coverage gate

Every feature declared `AVAILABLE_V1` must have at least 95% nonmissing coverage across required event-evaluation rows. Missing values are not imputed to obtain a pass.

## One-time evidence run

The frozen feature suite is executed once after:

1. contract tests pass;
2. P5.1 taxonomy hash matches;
3. Binance fixed-window data-access preflight passes;
4. no P5.2 result already exists.

The run commits immutable source snapshots, resolved event anchors, feature panel, event summaries, coverage, pending-data gaps, summary JSON and digest.

Standing research authorization covers this one-time research run. It does not authorize any production transition.

## Forbidden

- moving P5.1 windows or anchors after seeing feature evidence;
- changing RSI/KAMA/lookback definitions after event evidence;
- inventing an unvalidated dominance or broad-market proxy and labeling it as the requested feature;
- using future information in a feature at time `t`;
- fitting P5.3 state thresholds in the P5.2 result run;
- changing BRRK relative weights;
- production authorization.

## P5.2 completion meaning

A completed P5.2 result means **feature evidence exists**. It does not mean a feature is promoted into the cycle model.

After P5.2 closes, P5.3 may use the frozen evidence to define candidate state-model structures and thresholds under a new governed step.
