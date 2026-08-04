# PIT-ALPHA-0016-DYNAMIC-ROTATION — Validated Result

Date: 2026-08-04

Status: **RANKING MECHANISM VALIDATED / PORTFOLIO SPECIFICATION REJECTED / NO PRODUCTION PROMOTION**

This was the first successful execution of the preregistered point-in-time dynamic-alpha experiment. No universe, age, liquidity, signal, rank, Top-N, BTC-core, concentration-cap, cost, placebo or delisting-stress parameter was changed after observing results.

## Research question

Does the frozen own-trend plus relative-to-BTC trend mechanism retain cross-sectional information when the strategy must select from the historical universe that actually existed at each date, including assets that later failed or became inactive?

## Frozen primary specification

- Historical ordinary Binance spot-USDT candidates.
- Later inactive/delisted symbols retained while historical daily rows exist.
- Minimum 240 consecutive completed daily observations.
- Completed-day quote volume >= $25m.
- Own trend > 0 and relative-to-BTC trend > 0.
- Rank = `(0.5 × own trend + 0.5 × relative trend) / rv30`.
- Top-2 primary selection.
- Gross exposure <= 1.
- Risk-on allocation: 50% of budget to BTC core, 50% to alt sleeve.
- Universal single-alt cap: 35% of total budget; overflow returned to BTC.
- 0.05 L1 rebalance band.
- 5 bps per absolute weight change.
- Completed day-t target held over t+1.

## Data integrity

- Historical candidates: **648**.
- Symbols with historical rows: **646**.
- API calls: **1,114**.
- Fetch errors: **0**.
- Panel: 2019-01-01 through 2026-08-02.
- Evaluation: 2021-05-01 through 2026-08-02, **1,920 daily observations**.
- Mean age/liquidity-eligible universe: **34.91** assets.
- Mean positive own-and-relative-trend eligible universe: **14.98**.
- Median positive-trend eligible universe: **9**; maximum **117**.
- No eligible alt on only **1.67%** of evaluation days.
- **152 currently inactive/non-TRADING symbols were historically eligible**.

The experiment therefore tested the ranking mechanism against a materially broader historical opportunity set rather than today's survivor list.

## Common-window performance

| Strategy | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|
| PIT Alpha Top-1 | $15,214 | 8.31% | -66.02% | 51.93% | 0.407 | 0.126 | 270.04 |
| **PIT Alpha Top-2 primary** | **$18,354** | **12.25%** | **-69.12%** | 52.89% | **0.480** | **0.177** | **349.62** |
| PIT Alpha Top-3 | $10,382 | 0.71% | -76.39% | 50.92% | 0.268 | 0.009 | 333.03 |
| Equal-weight all eligible | $2,219 | -24.91% | -82.93% | 53.48% | -0.266 | -0.300 | 352.62 |
| BTC hold | $11,018 | 1.86% | -76.63% | 54.97% | 0.309 | 0.024 | 0.00 |
| BTC dynamic gross <=1 | $17,362 | 11.07% | -54.31% | 40.86% | 0.461 | 0.204 | 40.44 |
| **Fixed V1 gross <=1** | **$51,185** | **36.43%** | **-59.72%** | 48.11% | **0.889** | **0.610** | **131.81** |

Monthly capture versus BTC:

| Strategy | Upside capture | Downside capture |
|---|---:|---:|
| PIT Alpha Top-2 | 75.09% | 52.78% |
| BTC dynamic | 82.42% | 70.77% |
| Fixed V1 | 109.79% | 65.03% |

The dynamic Top-2 portfolio beats BTC hold and slightly exceeds BTC dynamic CAGR, but does so with much deeper drawdown and worse Calmar. It is far behind fixed V1 in growth, risk-adjusted return and turnover.

## Placebo test — ranking information survives

The 100 preregistered placebo strategies used the identical point-in-time eligibility and portfolio rules, but replaced the trend rank with one fixed pseudorandom symbol priority per seed.

Top-2 primary:

- terminal NAV beat **98 of 100** placebo seeds;
- Calmar beat **98 of 100** placebo seeds;
- primary final value: **$18,354**;
- placebo median final value: **$2,326**;
- placebo 95th-percentile final value: **$10,137**;
- placebo median CAGR: **-24.23%**;
- placebo 95th-percentile CAGR: approximately **0.26%**;
- placebo median MDD: approximately **-87.10%**.

This is strong evidence that own-trend plus relative-strength ranking contains real cross-sectional information. The result is not explained by merely applying the same eligibility gate to arbitrary assets.

## Contribution concentration — not a single-winner result

Largest arithmetic gross contributors included:

| Asset | Contribution | Current status |
|---|---:|---|
| SOL | +0.4711 | TRADING |
| BTC core | +0.4607 | TRADING |
| XRP | +0.3211 | TRADING |
| EGLD | +0.2098 | TRADING |
| AXS | +0.2089 | TRADING |
| DOGE | +0.1959 | TRADING |
| TRX | +0.1841 | TRADING |
| YGG | +0.1399 | TRADING |
| FTM | +0.1314 | BREAK |
| OM | +0.1303 | BREAK |

- largest positive contributor share: **13.14%**;
- top-three positive contributor share: **34.93%**;
- currently inactive/non-TRADING assets' total arithmetic contribution: approximately **-0.0121**, close to flat/slightly negative.

Therefore the Top-2 result is not another disguised single-SOL backtest. The broad ranking mechanism distributed positive contribution across multiple survivors and later-inactive assets.

## Annual and subperiod instability

Top-2 calendar returns:

- 2021 partial: **-3.98%**;
- 2022: **-31.26%**;
- 2023: **-14.96%**;
- 2024: **+231.91%**;
- 2025: **+10.77%**;
- 2026 through Aug 2: **-11.06%**.

Top-2 subperiods:

| Start | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| 2022-01-01 | 15.18% | -62.92% | 0.529 | 0.241 |
| 2023-01-01 | 33.00% | -61.58% | 0.794 | 0.536 |
| 2024-01-01 | 58.08% | -34.14% | 1.186 | 1.701 |
| 2025-01-01 | -0.93% | -27.02% | 0.147 | negative |
| 2026-01-01 | negative | -14.85% | -1.413 | negative |

The result is dominated by a strong 2024 regime and fails to demonstrate durable post-2024 continuation.

## Transaction-cost stress

| Cost | Final $10k | CAGR | MDD | Sharpe | Calmar |
|---:|---:|---:|---:|---:|---:|
| 5 bps | $18,354 | 12.25% | -69.12% | 0.480 | 0.177 |
| 10 bps | $15,407 | 8.57% | -70.90% | 0.417 | 0.121 |
| 20 bps | $10,854 | 1.57% | -74.61% | 0.291 | 0.021 |

The ranking signal survives 10 bps in nominal terms, but the portfolio edge is highly turnover-sensitive. At 20 bps almost all economic growth disappears.

## Delisting-exit stress

The registered 0%, -25% and -50% first-missing-day haircuts produced identical results.

This does **not** mean delisting risk is zero. It means that in this exact historical run, no asset was still held on the first day its daily row disappeared: the point-in-time liquidity/trend rule exited those positions before the missing-row event. This stress test therefore did not bind and cannot be used as evidence that all real-world delistings would be harmless.

## Decision against preregistered promotion gate

### Requirements passed

- Clearly beats the median placebo and 98% of placebo seeds.
- Contribution is diversified; no asset provides >50% of positive contribution.
- Later inactive assets were genuinely included and did not mechanically destroy the signal.
- Remains positive at 10 bps.

### Requirements failed

- Does not approach fixed V1 performance.
- MDD is worse than both fixed V1 and BTC dynamic.
- Turnover is approximately 2.65× fixed V1 and 8.65× BTC dynamic.
- The 2025+ subperiod is not positive.
- At 20 bps the edge is nearly eliminated.
- Risk-adjusted performance is insufficient for deployment or replacement of BRRK-0011.

## Final research decision

1. **The cross-sectional ranking mechanism is validated.** Own-trend plus relative-strength selection is not pure hindsight and strongly outperforms random priority inside the same historical universe.
2. **The preregistered portfolio specification is rejected.** Daily point-in-time Top-2 rotation does not provide an acceptable growth/drawdown/turnover trade-off.
3. **BRRK-0011 remains the canonical research baseline.** Fixed V1 cannot yet be declared survivor-free, but it remains the best tested deployable research architecture.
4. **PIT-ALPHA-0016 is not eligible for live or shadow portfolio promotion.** It remains a mechanism-validation experiment.
5. **No 0016 parameter may be tuned on this window.** Do not change Top-N, liquidity floor, history requirement, rank weights, BTC-core allocation or cap to rescue the result.
6. The next task is a **no-trading-change attribution audit** explaining why a rank that beats 98% of placebos still produces poor portfolio economics. Required dimensions include turnover/churn, holding duration, entry cohorts, asset tail-loss events, rank persistence and differences from fixed V1 selection timing.
7. Any future low-turnover or monthly-selection design requires a new experiment ID and preregistration after the attribution audit; it is not an amendment to 0016.

## Evidence files

Exact outputs are preserved under `research/results/pit_alpha_0016/`:

- `dynamic_alpha_report.json`;
- `daily_equity.csv`;
- `daily_held_weights_long.csv`;
- `daily_universe_counts.csv`;
- `asset_contribution.csv`;
- `placebo_metrics.csv`;
- `pnl_daily.svg`;
- full workflow log.
