# FUNDING-CROSSVENUE-0002 — Binance / Hyperliquid overlap audit

Date: 2026-08-04  
Status: **VALID NO-PNL AUDIT / CLASSIFIED AS SIGN-REGIME PROXY / LEVEL PROXY REJECTED**

## Purpose

Determine whether Binance official USD-M funding can represent Hyperliquid native funding over common history.

This audit used no portfolio weights and calculated no strategy PNL. It compared BTC, ETH, SOL, BNB and XRP from 2023-05-01 through 2026-07-31 using preregistered UTC eight-hour clock blocks.

Alignment was frozen before the first valid run:

```text
00:00–07:59 UTC
08:00–15:59 UTC
16:00–23:59 UTC
```

Each event timestamp was floored to its clock block. The primary block rate was the arithmetic sum of all funding events inside the block; the secondary rate compounded `(1 + event rate)` within the block. No interpolation or forward fill was used.

## Coverage

Coverage was complete over each asset's native common window.

| Asset | First common block | Last common block | Paired 8h blocks | Paired coverage |
|---|---|---|---:|---:|
| BTC | 2023-05-12 00:00 UTC | 2026-07-31 16:00 UTC | 3,531 | 100% |
| ETH | 2023-05-12 00:00 UTC | 2026-07-31 16:00 UTC | 3,531 | 100% |
| SOL | 2023-05-12 00:00 UTC | 2026-07-31 16:00 UTC | 3,531 | 100% |
| BNB | 2023-05-12 00:00 UTC | 2026-07-31 16:00 UTC | 3,531 | 100% |
| XRP | 2023-06-18 00:00 UTC | 2026-07-31 16:00 UTC | 3,420 | 100% |

The Hyperliquid event-count distribution also confirms its historical interval change:

- approximately the first 81 common blocks contained one event per eight-hour block;
- three transition blocks contained seven hourly events;
- 3,447 blocks for BTC/ETH/SOL/BNB contained eight hourly events;
- XRP's common sample was effectively hourly throughout.

## Main comparison

| Asset | Pearson | Spearman | Sign agreement | Mean Binance / 8h | Mean Hyperliquid / 8h | HL−Binance mean bias | Bias / mean abs HL |
|---|---:|---:|---:|---:|---:|---:|---:|
| BTC | 0.646 | 0.553 | 79.69% | 0.00006638 | 0.00012991 | +0.00006352 | 41.64% |
| ETH | 0.612 | 0.623 | 81.53% | 0.00006749 | 0.00013105 | +0.00006355 | 40.49% |
| SOL | 0.673 | 0.641 | 74.00% | 0.00004562 | 0.00011236 | +0.00006674 | 33.80% |
| BNB | 0.612 | 0.616 | **38.23%** | **-0.00001711** | **+0.00002888** | +0.00004599 | 26.32% |
| XRP | 0.652 | 0.620 | 75.82% | 0.00006600 | 0.00008362 | +0.00001763 | 11.09% |

### Cumulative additive rates over common history

| Asset | Binance | Hyperliquid | Difference |
|---|---:|---:|---:|
| BTC | 0.2344 | 0.4587 | +0.2243 |
| ETH | 0.2383 | 0.4627 | +0.2244 |
| SOL | 0.1611 | 0.3968 | +0.2357 |
| BNB | **-0.0604** | **+0.1020** | +0.1624 |
| XRP | 0.2257 | 0.2860 | +0.0603 |

For a persistent long, positive cumulative rates represent funding paid. These cumulative figures are source comparison diagnostics, not strategy costs, because no held-notional path was applied.

## Additive versus compounded aggregation

Within an eight-hour block, the difference between additive and compounded Hyperliquid rates was economically negligible at this data precision:

- mean absolute discrepancy was approximately `2e-8` to `5e-8` per block;
- Binance had one event per block, so additive and compounded rates were effectively identical.

The later PNL attribution may use additive block rates as its primary accounting series, while retaining compounded rates as an audit column.

## Stability by year

The relationship is not constant enough to justify a single cross-venue level conversion.

Examples:

- BTC Pearson correlation ranged from about 0.37 to 0.70 across calendar years;
- ETH ranged from about 0.39 to 0.64;
- SOL ranged from about 0.54 to 0.78 and had relatively stable sign agreement;
- XRP remained directionally useful but had a large negative 2023 level bias and positive later bias;
- BNB sign agreement remained poor every year, approximately 31%–49%, despite positive rank correlations.

Therefore a fitted scalar such as `Hyperliquid = k × Binance` would be unstable and is not authorized.

## Preregistered classification

The fixed gates produced:

```text
proxy_classification = sign_regime_proxy
```

Asset checks:

| Asset | Level gate | Sign/regime gate |
|---|---:|---:|
| BTC | Pass | Pass |
| ETH | Pass | Pass |
| SOL | Pass | Pass |
| BNB | **Fail** | **Fail** |
| XRP | Pass | Pass |

Because the level classification required all five assets to pass, Binance is rejected as a general Hyperliquid level proxy.

Four of five assets passed the sign/regime gate, so Binance is retained as a long-history sign/regime proxy and stress source.

## Decision for later funding attribution

A frozen-holdings funding experiment is now authorized only under separate, non-blended scenarios:

1. **Hyperliquid native overlap scenario** — primary venue-specific estimate from each asset's actual native common history;
2. **Binance full-history proxy scenario** — long-history sign/regime and stress scenario, explicitly not a Hyperliquid point estimate;
3. **Price-only canonical baseline** — unchanged BRRK-0011 target and transaction-cost path;
4. **Theoretical zero-funding spot upper bound** — implementation bound only, not proof that all required spot inventory exists on the execution venue.

Prohibited in the next experiment:

- fitting a Binance-to-Hyperliquid multiplier;
- blending the two sources into one synthetic rate;
- dropping BNB;
- changing target weights according to funding;
- choosing a funding threshold from PNL;
- increasing leverage;
- interpreting Binance all-history funding as actual Hyperliquid historical funding.

## Exact evidence

Validated outputs include:

- `funding_crossvenue_0002_report.json`;
- `paired_8h_blocks.csv`;
- `coverage.csv`;
- `annual_metrics.csv`;
- `hyperliquid_event_count_distribution.csv`;
- raw source-event extracts in the workflow artifact;
- complete workflow log;
- frozen preregistration JSON.

The repository should persist the compact report and paired-block evidence under:

```text
research/results/funding_crossvenue_0002/
```
