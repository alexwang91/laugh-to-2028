# FUNDING-DATA-0001 — Official source audit

Date: 2026-08-04  
Status: **VALID DATA AUDIT / SOURCE GATE PASSED / NO PNL OR ROUTING AUTHORIZED**

## Purpose

Establish whether reproducible historical funding data exists before calculating funding PNL or designing a Spot/Perp Router.

The audit made no change to strategy targets, holdings, leverage or execution. It tested two fixed sources:

1. Binance official public USD-M monthly funding archive as a long-history centralized-exchange proxy;
2. Hyperliquid official `info` endpoint with `type=fundingHistory` as the native venue source.

## Binance official archive

Root prefix:

```text
data/futures/um/monthly/fundingRate/
```

The root contained **920 archived symbols**. All five registered targets were present and parseable.

| Symbol | First month | Last complete month | Months | Internal missing months |
|---|---:|---:|---:|---:|
| BTCUSDT | 2020-01 | 2026-07 | 79 | 0 |
| ETHUSDT | 2020-01 | 2026-07 | 79 | 0 |
| SOLUSDT | 2020-09 | 2026-07 | 71 | 0 |
| BNBUSDT | 2020-02 | 2026-07 | 78 | 0 |
| XRPUSDT | 2020-01 | 2026-07 | 79 | 0 |

First, midpoint and latest-month samples for every target used stable fields:

```text
calc_time
funding_interval_hours
last_funding_rate
```

Observed median interval was **8 hours** in all sampled Binance files. Exact timestamps include millisecond-level jitter, so later alignment must use event timestamps rather than assuming perfectly exact clock values.

The archive contains positive, negative and zero rates. Several examples demonstrate that historical funding can be economically large and asset-specific; therefore a constant annual-rate approximation is not acceptable.

## Hyperliquid native fundingHistory

Endpoint:

```text
POST https://api.hyperliquid.xyz/info
{"type":"fundingHistory", ...}
```

Returned fields:

```text
coin
fundingRate
premium
time
```

### Fixed early probe

Window: 2023-05-01 through 2023-06-01.

- BTC, ETH, SOL and BNB each returned 60 rows from approximately 2023-05-12 through 2023-05-31.
- Median interval was approximately **8 hours**.
- XRP returned zero rows, consistent with its later native-market history.

### Fixed recent probe

Window: 2026-07-25 through 2026-08-03.

All five targets returned **240 rows**, with a median interval of exactly **1 hour**.

| Coin | Recent rows | Median interval | Positive rows | Negative rows | Mean rate/event |
|---|---:|---:|---:|---:|---:|
| BTC | 240 | 1h | 223 | 17 | 0.0000086074 |
| ETH | 240 | 1h | 206 | 34 | 0.0000068692 |
| SOL | 240 | 1h | 160 | 80 | 0.0000024904 |
| BNB | 240 | 1h | 221 | 19 | 0.0000097933 |
| XRP | 240 | 1h | 153 | 87 | 0.0000024612 |

These values are source diagnostics, not forecasts or routing thresholds.

## Critical implementation finding

Hyperliquid historical funding frequency is not constant across the full venue history:

```text
early native history: approximately 8-hour events
current native history: hourly events
```

Therefore future funding PNL must be calculated event by event:

```text
funding PNL event = - position_notional_fraction × funding_rate
```

for a long position when the rate is positive, using the position actually held at the event timestamp.

A fixed APR, fixed number of daily events, or daily-average shortcut is not an acceptable primary calculation.

## Source-role decision

### Binance

Approved as:

- reproducible long-history funding source;
- clearly labelled centralized-exchange proxy;
- suitable for complete event-level historical attribution after cross-venue calibration.

Not approved as:

- a direct substitute for Hyperliquid funding;
- evidence that Binance and Hyperliquid have the same sign, magnitude or timing.

### Hyperliquid

Approved as:

- native source for venue-specific funding and premium;
- suitable for common-history comparison and future shadow/live accounting;
- capable of returning recent hourly funding for all five target assets.

## Audit decision

All preregistered data-source success gates passed:

- all five Binance targets present;
- all five Binance target archives parseable;
- no internal missing Binance months;
- all five Hyperliquid recent probes parseable;
- event fields and intervals identified;
- early-window absence reported rather than filled.

This audit authorizes a **separate no-PNL cross-venue overlap audit**. It does not yet authorize historical funding PNL or a trading router.

The next step must compare Binance and Hyperliquid over common timestamps, after aggregating Hyperliquid hourly events to comparable 8-hour windows where appropriate. Required statistics include:

- sign agreement;
- Pearson and Spearman correlation;
- mean/median bias;
- MAE/RMSE;
- cumulative-rate difference;
- per-asset and per-year stability;
- explicit interval-change handling.

Only after that comparison may Binance be used as a calibrated historical proxy in a frozen-holdings funding attribution.

## Exact evidence

The validated machine-readable outputs are persisted under:

```text
research/results/funding_data_0001/
```

Expected files:

- `funding_data_0001_report.json`;
- `binance_monthly_coverage.csv`;
- `binance_sample_diagnostics.json`;
- `hyperliquid_probe_diagnostics.json`;
- `funding_data_0001.log`;
- frozen preregistration JSON.
