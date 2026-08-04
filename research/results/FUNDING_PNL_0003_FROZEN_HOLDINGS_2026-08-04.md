# FUNDING-PNL-0003 — Frozen BRRK-0011 holdings

Date: 2026-08-04  
Status: **VALID PREREGISTERED ATTRIBUTION / ALL-PERP IMPLEMENTATION REJECTED / SPOT-FIRST ROUTER AUTHORIZED FOR TESTING**

## Purpose

Measure funding drag on the exact persisted BRRK-0011 daily held weights without changing direction, coin weights, gross exposure or leverage.

This experiment did not optimize a funding threshold and did not route positions. It applied funding to the frozen holdings under separate source scenarios.

## Frozen inputs

- exact held weights: `research/results/pit_disp_0015/daily_weights.csv`;
- price and existing 5 bps turnover-cost equity: `research/results/pit_disp_0015/daily_equity.csv`;
- assets: BTC, ETH, SOL, BNB and XRP;
- daily held-notional approximation: every funding block on a UTC date uses the exact persisted weight for that date;
- positive funding means a long pays;
- no interpolation, forward fill, source blending or fitted multiplier.

Accounting:

```text
asset funding contribution = - held weight × funding rate
portfolio block return     = sum of asset contributions
UTC-day funding factor     = product(1 + block return)
combined daily return      = (1 + canonical price/cost return)
                             × daily funding factor - 1
```

## Data completeness

| Scenario | UTC 8h blocks | Dates | Missing blocks | Incomplete asset blocks |
|---|---:|---:|---:|---:|
| Binance full proxy, 2022-12-10–2026-07-31 | 3,990 | 1,330 | 0 | 0 |
| Binance common overlap, 2023-06-18–2026-07-31 | 3,420 | 1,140 | 0 | 0 |
| Hyperliquid native common overlap | 3,420 | 1,140 | 0 | 0 |

Mean gross held exposure on common funding blocks was approximately **0.7431**.

## Full Binance long-history proxy scenario

This is a sign/regime and stress proxy, not a Hyperliquid funding level estimate.

| Scenario | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|---:|
| Price-only BRRK-0011 | **$62,247** | **65.29%** | **-33.72%** | 44.24% | **1.354** | **1.937** |
| Binance all-perp proxy | $50,259 | 55.85% | -34.79% | 44.21% | 1.222 | 1.605 |

Funding effect:

- compounded funding return: **-19.26%**;
- additive funding contribution: **-21.39%**;
- final NAV reduction: approximately **$11,989** from a $10,000 start comparison;
- CAGR reduction: approximately **9.44 percentage points per year**.

Annual compounded funding effects:

| Year | Funding effect |
|---:|---:|
| 2023 | -7.12% |
| 2024 | -9.75% |
| 2025 | -3.65% |
| 2026 through Jul 31 | -0.04% |

Asset additive attribution:

| Asset | Contribution |
|---|---:|
| BTC | **-14.14%** |
| SOL | **-5.76%** |
| ETH | -2.17% |
| BNB | **+0.68%** |
| XRP | 0.00% |

Negative funding received contributed approximately **+2.63%**, while positive funding paid cost approximately **-24.02%**. Negative carry therefore offset only about 11% of the positive-funding burden.

## Exact Binance versus Hyperliquid common window

Window: 2023-06-18 through 2026-07-31.

| Scenario | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|---:|
| Price-only | **$47,998** | **65.37%** | **-33.72%** | 44.23% | **1.355** | **1.939** |
| Binance all-perp common | $39,875 | 55.82% | -34.79% | 44.20% | 1.222 | 1.604 |
| **Hyperliquid native all-perp** | **$31,228** | **44.08%** | **-37.04%** | 44.06% | **1.046** | **1.190** |

Relative to price-only, Hyperliquid all-perp funding reduces:

- final value by approximately **$16,770**;
- CAGR by approximately **21.29 percentage points per year**;
- Sharpe from 1.355 to **1.046**;
- Calmar from 1.939 to **1.190**;
- and worsens MDD by approximately **3.32 percentage points**.

Relative to the Binance common proxy, Hyperliquid produces:

- final NAV lower by **$8,647**;
- CAGR lower by **11.75 percentage points per year**;
- compounded funding return lower by approximately **18.02 percentage points**.

This confirms that using Binance as a Hyperliquid funding-level point estimate would materially understate native venue costs for this frozen strategy.

## Hyperliquid native funding attribution

Common-window funding effect:

- compounded funding return: **-34.94%**;
- additive funding contribution: **-42.97%**;
- positive funding paid: **-46.41%**;
- negative funding received: **+3.43%**.

Annual compounded funding effects:

| Year | Hyperliquid funding effect |
|---:|---:|
| 2023 partial | -10.33% |
| 2024 | **-20.44%** |
| 2025 | -8.58% |
| 2026 through Jul 31 | -0.26% |

Asset additive attribution:

| Asset | Contribution |
|---|---:|
| BTC | **-25.19%** |
| SOL | **-13.40%** |
| ETH | -3.05% |
| BNB | -1.33% |
| XRP | 0.00% |

BTC and SOL account for approximately 89.8% of the total Hyperliquid additive funding drag. The frozen strategy held no economically material XRP allocation over this window, hence zero XRP contribution.

## Additive versus compounded block sensitivity

- Binance has one event per eight-hour block; additive and compounded variants are effectively identical.
- Hyperliquid's hourly events create small within-block cross terms, but the resulting final NAV difference is only about **$3.17** on a $10,000 start over the full common window.

Therefore additive eight-hour block rates are an adequate primary accounting representation for this daily-held-notional approximation. The principal uncertainty is source/venue level and intraday notional drift, not additive-versus-compounded block aggregation.

## Interpretation

### Validated

1. Funding is economically material even though the strategy's average gross exposure is below one.
2. Full-perp implementation can erase a large portion of the historical BRRK advantage.
3. Hyperliquid native funding was substantially more expensive than the Binance proxy for this exact held path.
4. BTC and SOL are the dominant carry-cost contributors.
5. Negative funding receipts do not come close to offsetting positive funding paid.
6. Price-only backtests are not deployable PNL estimates for a full-perp implementation.

### Rejected

1. **All-perp gross<=1 implementation is rejected** as the default architecture.
2. Binance funding cannot be substituted for Hyperliquid native funding levels.
3. A fixed annual funding haircut is not adequate.
4. Funding cannot remain merely an after-the-fact reporting footnote.

## Decision

This result authorizes a separate deterministic **Spot/Perp Router** experiment while keeping the exact same directional target.

The next router must begin from a structural rule rather than a PNL-selected threshold:

```text
long exposure up to available spot capacity → spot
short exposure or gross above funded spot capacity → perp
perp overlay → actual funding applies
```

It must separately model:

- which target assets have executable spot markets on the intended venue or connected venue;
- spot and perp fees;
- spread/slippage and order-book depth;
- basis/mark-oracle differences;
- transfer/operational constraints;
- negative-funding benefit for optional perp exposure;
- partial fills and position reconciliation.

No router promotion is authorized yet. A theoretical zero-funding spot curve is only an upper bound and does not prove executable spot inventory or equivalent spot/perp price paths.

## Limitations

1. Daily-held-notional approximation ignores intraday notional drift after price moves.
2. Spot/perp basis and differences between spot close and perpetual mark are not included.
3. Existing price equity already includes the strategy's 5 bps weight-change cost, but does not include separate spot/perp venue fee schedules.
4. Hyperliquid results cover only the native common history, not the full BRRK backtest.
5. Binance full history remains a stress/sign-regime proxy only.

## Exact evidence

Validated outputs include:

- `funding_pnl_0003_report.json`;
- full- and common-window daily equity;
- daily funding factors and additive funding;
- block/asset attribution;
- exact common-window PNL SVG;
- complete workflow log;
- frozen preregistration JSON.

They should be persisted under:

```text
research/results/funding_pnl_0003/
```
