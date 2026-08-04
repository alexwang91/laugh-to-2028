# PIT-ALPHA-0018 — Entry Rank / Eligibility Exit

Date: 2026-08-04  
Status: **VALID PREREGISTERED EXPERIMENT / CHURN MECHANISM IMPROVED / PORTFOLIO REJECTED**

## Question

`AUDIT-0017` showed that 83.41% of `PIT-ALPHA-0016` turnover came from replacing one alt name with another and that the median holding spell was one day. The only authorized change was therefore:

```text
Top-2 rank fills vacant slots
        ↓
incumbent remains held while its existing
own-trend, relative-to-BTC, history and liquidity
eligibility remain valid
        ↓
exit only on eligibility loss or BTC risk-off
```

No exit-rank threshold, minimum holding period, calendar schedule, higher listing-age rule, liquidity change, preferred coin list, funding, dispersion, volatility gate, covariance optimizer or leverage was added.

## Data integrity

- Historical ordinary Binance spot-USDT candidates: **648**
- Symbols returning historical rows: **646**
- API calls: **1,114**
- Fetch errors: **0**
- Evaluation: **2021-05-01 through 2026-08-02**
- Evaluation observations: **1,920 completed daily observations**
- Currently inactive/non-TRADING assets historically eligible: **152**
- Signal on completed day `t`; holdings applied to `t+1`

Frozen portfolio rules remained:

- 240 consecutive completed daily rows;
- completed-day quote volume >= $25m;
- own trend > 0 and relative-to-BTC trend > 0;
- entry rank `(0.5 own trend + 0.5 relative trend) / rv30`;
- gross <= 1;
- risk-on structure 50% BTC core / 50% alt sleeve;
- universal single-alt cap 35% of beta budget;
- 0.05 L1 rebalance band;
- 5 bps per absolute weight change.

Deterministic tests confirmed:

1. rank reordering does not replace eligible incumbents;
2. an eligibility failure creates an immediate vacancy and replacement;
3. BTC risk-off removes alt incumbents;
4. mandatory exits are not blocked by the 0.05 band.

## Portfolio result

| Strategy | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|
| **PIT-ALPHA-0018 eligibility-exit** | **$22,437** | **16.62%** | **-66.86%** | 53.12% | **0.555** | **0.249** | **141.86** |
| PIT-ALPHA-0016 daily Top-2 | $18,354 | 12.25% | -69.12% | 52.89% | 0.480 | 0.177 | 349.62 |
| BTC dynamic gross<=1 | $17,362 | 11.07% | -54.31% | 40.86% | 0.461 | 0.204 | 40.44 |
| Fixed V1 gross<=1 | $51,185 | 36.43% | -59.72% | 48.11% | 0.889 | 0.610 | 131.81 |

Relative to the rejected daily Top-2 implementation, 0018:

- increases CAGR by **4.37 percentage points**;
- improves MDD by about **2.26 percentage points**;
- raises Sharpe from 0.480 to **0.555**;
- raises Calmar from 0.177 to **0.249**;
- reduces reported turnover by about **59.4%**.

This confirms that daily leaderboard replacement was a real mechanical defect.

It does **not** make the portfolio acceptable. The drawdown remains -66.86%, materially worse than BTC dynamic and fixed V1, and the long-run result remains far below fixed V1.

## Holding persistence

| Statistic | PIT-ALPHA-0016 | PIT-ALPHA-0018 |
|---|---:|---:|
| Holding spells | 653 | **188** |
| Distinct alt symbols held | 113 | **64** |
| Median holding duration | 1 day | **3 days** |
| Mean holding duration | — | **11.40 days** |
| 95th-percentile duration | — | **58.3 days** |
| Maximum duration | — | **260 days** |
| Positive-contribution spells | 41.96% | **40.96%** |

The state machine captures several right-tail trends that daily Top-2 repeatedly interrupted. Examples include:

- SOL: 260-day spell, asset return about +452%, contribution +0.535;
- AXS: 131-day spell, contribution +0.405;
- DOGE: 107-day spell, contribution +0.262;
- SUI: 112-day spell, contribution +0.113;
- RNDR: 94-day spell, contribution +0.112;
- LINK: 78-day spell, contribution +0.107.

However, only about 40.96% of spells make a positive arithmetic contribution. Persistence improves right-tail capture but does not turn the broad candidate set into a generally profitable portfolio.

## Turnover decomposition

The attribution convention includes the initial allocation and reports total turnover **142.86**, while the portfolio metrics function reports **141.86**. This one-unit difference is a reporting-convention issue and does not affect PNL.

Under the attribution convention:

| Source | Turnover | Share |
|---|---:|---:|
| BTC-weight changes | 26.52 | 18.56% |
| Alt-sleeve-size changes | 34.41 | 24.09% |
| Within-alt name switching | 81.93 | 57.35% |
| **Total** | **142.86** | 100% |

Name switching remains the largest component, but its absolute amount falls sharply from the AUDIT-0017 level. The authorized state-machine change therefore operated through the intended mechanism.

## Ranking validation under the same state machine

The same 100 fixed-random-priority placebo seeds were rerun using the **same eligibility-exit state machine**.

- 0018 final NAV beat **98/100** placebo seeds;
- 0018 Calmar beat **98/100** placebo seeds;
- placebo median final value: **$6,073**;
- placebo 95th-percentile final value: **$16,896**;
- 0018 final value: **$22,437**.

Therefore the own-trend plus relative-strength rank remains informative after turnover is reduced. The failure is not that ranking is random.

## Contribution concentration

- Largest positive contributor share: **19.06%**
- Top-three positive contributor share: **48.01%**
- Positive contributing assets: **27**
- Aggregate contribution from assets currently inactive/non-TRADING: **+0.140**

The result is not dependent on one current survivor, but contribution becomes more concentrated than in 0016 because longer holding deliberately lets a small number of winners compound.

## Cost stress

| Cost | Final $10k | CAGR | MDD | Sharpe | Calmar |
|---:|---:|---:|---:|---:|---:|
| 5 bps | $22,437 | 16.62% | -66.86% | 0.555 | 0.249 |
| 10 bps | $20,903 | 15.06% | -67.88% | 0.529 | 0.222 |
| 20 bps | $18,140 | 12.00% | -69.82% | 0.478 | 0.172 |

0018 is substantially more cost-robust than 0016. At 20 bps it still has material cumulative growth. The remaining failure is therefore not primarily transaction cost.

## Subperiod failure

Annual returns:

| Year | 0018 |
|---:|---:|
| 2021 partial | +7.23% |
| 2022 | -29.66% |
| 2023 | +36.06% |
| 2024 | +173.20% |
| 2025 | **-10.03%** |
| 2026 through Aug 2 | **-11.06%** |

From 2025-01-01:

- CAGR: **-13.11%**
- MDD: **-32.05%**
- Sharpe: **-0.170**
- Calmar: **-0.409**

This directly violates the preregistered promotion requirement that 2025+ economics must not remain negative.

## Decision

### What is validated

1. The point-in-time own-trend plus relative-strength entry rank is not random.
2. Daily Top-2 replacement was a major implementation error.
3. Entry-rank / eligibility-exit materially lowers turnover and captures longer right-tail trends.
4. The ranking edge survives under the same lower-turnover state machine.

### What is rejected

1. `PIT-ALPHA-0018` is **not** promoted to live or shadow allocation.
2. MDD remains unacceptable.
3. 2025+ and 2026 economics remain negative.
4. Fixed V1 remains substantially superior historically, although selection-biased.
5. The broad dynamic-alpha portfolio still lacks a sufficiently reliable risk/entry-quality mechanism.

### Research stopping rule

No threshold or portfolio parameter may be changed under this experiment ID. Specifically, do not now add:

- a minimum holding period;
- an exit-rank buffer;
- a weekly/monthly calendar;
- a higher age or volume threshold;
- a named-coin preference;
- dispersion, funding, LPM, covariance or leverage as a rescue layer.

`BRRK-0011` remains the canonical research baseline.

The dynamic-alpha line now stops at mechanism evidence. Before any future alpha portfolio design, a no-trading-change attribution would need to identify a distinct, externally defensible cause of the 2025+ deterioration. The main project queue should move to historical funding / Spot-Perp routing and execution hardening, which can improve implementation without mining another PNL threshold from the same window.

## Exact evidence

The exact generated files are persisted under:

`research/results/pit_alpha_0018/`

including:

- `pit_alpha_0018_report.json`;
- `daily_equity.csv`;
- `daily_held_weights_long.csv`;
- `daily_selected_names.csv`;
- `daily_turnover_decomposition.csv`;
- `holding_spells.csv`;
- `asset_contribution.csv`;
- `placebo_metrics.csv`;
- `state_machine_events.csv`;
- `pnl_daily.svg`;
- complete workflow log.
