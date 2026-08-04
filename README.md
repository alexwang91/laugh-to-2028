# laugh-to-2028

一个以 **长期生存、可审计和减少回测自欺** 为目标的 crypto systematic-allocation research project。

当前核心不是继续在固定赢家币池上堆指标，而是依次验证：

1. 风险信号在 point-in-time、包含后来失败/退市资产的真实历史 universe 中是否仍成立；
2. alpha 排名是否真的优于随机；
3. 排名信息能否转化为可部署的增长、回撤、成本与换手组合；
4. 当机制有效但组合失败时，先完成因果归因，再授权下一种结构。

## Current status

| Layer | Evidence status | Decision |
|---|---|---|
| BTC dynamic beta | Frozen core concept | 保留 |
| Fixed-universe V1 | Strong historical result, materially selection-biased | 不直接外推 |
| **BRRK-0011** | **Frozen canonical research baseline** | 当前基线 |
| DISP-0013 | Benefit concentrated in few episodes | Shadow diagnostic |
| DISP-0014 | Strong fixed-panel result, selection-sensitive | 不 promotion |
| PIT-DISP-0015 | Broad PIT risk mechanism survives, growth trade-off fails | Shadow risk diagnostic |
| PIT-ALPHA-0016 rank | Beats 98% of placebos | Mechanism validated |
| PIT-ALPHA-0016 portfolio | High turnover, deep drawdown, weak persistence | Rejected |
| **AUDIT-0017** | **83.4% of turnover is name switching; median hold 1 day** | **Dominant failure identified** |
| Historical funding-aware PNL | Not validated | Archive work pending |
| Hyperliquid Plan B | Testnet/shadow implementation | Not production-ready |

---

## Canonical daily PNL — BRRK / dispersion research

![Exact daily backtest PNL](docs/pnl.svg)

The chart uses 1,332 persisted daily equity observations from 2022-12-10 through 2026-08-02, with completed UTC daily information, t→t+1 execution, 0.05 L1 rebalance band and 5 bps per absolute weight change.

| Strategy | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar | CDaR95 | Up capture | Down capture |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 baseline | $57,116 | 61.26% | -37.64% | 44.45% | 1.295 | 1.628 | 36.55% | 106.05% | 80.33% |
| **BRRK-0011** | **$62,247** | **65.10%** | **-33.72%** | 44.21% | **1.353** | **1.931** | 31.78% | **105.02%** | 72.99% |
| BRRK + fixed DISP-0014 | $63,084 | 65.71% | -30.60% | 39.01% | 1.488 | 2.147 | 28.85% | 98.45% | 62.40% |
| BRRK + dynamic PIT-DISP-0015 | $56,543 | 60.81% | -30.40% | 39.69% | 1.393 | 2.000 | 28.08% | 95.92% | 65.71% |

### PIT-DISP-0015 conclusion

The valid dead-pool-inclusive run used:

- 652 historical ordinary Binance spot-USDT candidates;
- 646 symbols with rows;
- zero fetch errors;
- 159 currently inactive/non-TRADING symbols historically eligible;
- mean daily eligible universe 30.62 assets.

Broad dynamic dispersion genuinely reduces MDD, CDaR, volatility and downside capture. However, it lowers CAGR from 65.10% to 60.81% and gives up substantial upside capture.

Fixed-panel and dynamic dispersion scales correlate only about **0.064**. Therefore the attractive BTC/ETH/SOL/BNB/XRP DISP-0014 result is materially panel-selection-sensitive.

**Decision:** BRRK-0011 remains baseline; DISP-0014 and PIT-DISP-0015 are diagnostics, not default portfolios.

Full result: [`research/results/PIT_DISP_0015_RESULT_2026-08-04.md`](research/results/PIT_DISP_0015_RESULT_2026-08-04.md)

Exact outputs: [`research/results/pit_disp_0015/`](research/results/pit_disp_0015/)

---

## PIT-ALPHA-0016 — dynamic alpha qualification

Separate exact daily chart: [`research/results/pit_alpha_0016/pnl_daily.svg`](research/results/pit_alpha_0016/pnl_daily.svg)

Evaluation: 2021-05-01 through 2026-08-02, 1,920 daily observations.

Frozen primary rules:

```text
historical ordinary Binance USDT universe
    ↓
240 consecutive completed daily rows
    ↓
completed-day quote volume >= $25m
    ↓
own trend > 0 AND relative-to-BTC trend > 0
    ↓
rank = (0.5 own trend + 0.5 relative trend) / rv30
    ↓
Top-2 primary
    ↓
gross <= 1; 50% BTC core / 50% alt sleeve
    ↓
universal single-alt cap 35%
    ↓
0.05 L1 band; 5 bps; t target held over t+1
```

### Data integrity

- 648 historical candidates;
- 646 with rows;
- 1,114 API calls and zero errors;
- mean age/liquidity-eligible universe 34.91;
- mean positive own-and-relative-trend universe 14.98;
- 152 currently inactive/non-TRADING symbols historically eligible.

### Portfolio results

| Strategy | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|
| PIT Top-1 | $15,214 | 8.31% | -66.02% | 51.93% | 0.407 | 0.126 | 270.04 |
| **PIT Top-2 primary** | **$18,354** | **12.25%** | **-69.12%** | 52.89% | **0.480** | **0.177** | **349.62** |
| PIT Top-3 | $10,382 | 0.71% | -76.39% | 50.92% | 0.268 | 0.009 | 333.03 |
| Equal-weight all eligible | $2,219 | -24.91% | -82.93% | 53.48% | -0.266 | -0.300 | 352.62 |
| BTC dynamic gross<=1 | $17,362 | 11.07% | -54.31% | 40.86% | 0.461 | 0.204 | 40.44 |
| **Fixed V1 gross<=1** | **$51,185** | **36.43%** | **-59.72%** | 48.11% | **0.889** | **0.610** | **131.81** |

### What passed

The 100 preregistered placebo portfolios used exactly the same eligibility and portfolio construction, replacing the trend rank with a fixed random symbol priority.

- Top-2 final NAV beat **98/100** placebo seeds;
- Top-2 Calmar beat **98/100** placebo seeds;
- placebo median final value: $2,326;
- placebo 95th percentile: $10,137;
- largest positive contributor share: only **13.14%**;
- top-three share: **34.93%**.

Therefore the rank contains real cross-sectional information and is not simply another single-SOL hindsight result.

### What failed

- Top-2 CAGR 12.25% versus fixed V1 36.43%;
- MDD -69.12% versus fixed V1 -59.72% and BTC dynamic -54.31%;
- turnover 349.62 versus fixed V1 131.81 and BTC dynamic 40.44;
- 2025+ CAGR is negative;
- at 10 bps CAGR falls to 8.57%;
- at 20 bps CAGR falls to 1.57% and almost all growth disappears.

### PIT-ALPHA-0016 decision

1. **Ranking mechanism validated.**
2. **Portfolio specification rejected.**
3. **BRRK-0011 remains canonical baseline.**
4. No 0016 parameter may be tuned on this window.

Full result: [`research/results/PIT_ALPHA_0016_RESULT_2026-08-04.md`](research/results/PIT_ALPHA_0016_RESULT_2026-08-04.md)

Exact outputs: [`research/results/pit_alpha_0016/`](research/results/pit_alpha_0016/)

---

## AUDIT-0017 — why the valid rank became a bad portfolio

The no-trading-change audit identifies a precise mechanical mismatch:

> **Medium-horizon trend signals were implemented as a daily leaderboard replacement system.**

### Dominant evidence

- eligible-set daily Jaccard: **0.630**;
- roughly **3 additions and 3 removals per day**;
- monthly first-to-last eligible-set Jaccard: only **0.249**;
- **653 holding spells across 113 alt symbols**;
- median holding period: **1 day**;
- positive-contribution spells: **41.96%**;
- total turnover: **350.62**;
- **83.41% of turnover comes from switching one alt name for another**;
- BTC-weight changes contribute only 7.18% of turnover;
- alt-sleeve size changes contribute only 9.41%.

### The rank is right-skewed, not broadly profitable

| Horizon after entry | Still eligible | Still Top-2 | Median forward return | Mean forward return |
|---:|---:|---:|---:|---:|
| 1 day | 79.88% | 51.46% | -0.58% | -0.28% |
| 3 days | 71.74% | 42.09% | -0.50% | -0.17% |
| 7 days | 65.13% | 33.64% | -1.50% | +0.65% |
| 14 days | 58.83% | 25.19% | -1.57% | +2.63% |
| 30 days | 52.07% | 19.35% | **-2.43%** | **+4.83%** |

Most entries lose modestly. A small number of persistent winners create the positive mean. Strict daily Top-2 membership exits incumbents long before those right-tail trends can compound, even though many remain valid own-trend-positive and relative-trend-positive assets.

### Fixed-V1 overlap

- only **15.65%** of PIT alt exposure was in an active fixed-V1 alt;
- any overlap occurred on **28.70%** of days;
- mean daily return on overlap days: **+0.1439%**;
- mean daily return on non-overlap days: **+0.0396%**.

This does not justify hard-coding ETH/SOL/BNB. It shows that fixed V1 spent more time in persistent major trends, while broad PIT Top-2 repeatedly rotated through less durable names.

### Tail and compounding drag

The worst days were genuine tail events, not transaction-cost artifacts. The largest drawdown reached -69.12%. Across its drawdown/recovery episode, additive gross return was positive, but volatility sequence and 11.42 percentage points of cost left compounded net wealth nearly flat by recovery.

### Authorized next structure

The audit authorizes exactly one new hypothesis:

```text
Top-2 rank selects entries
        ↓
incumbent remains held while own trend > 0
and relative-to-BTC trend > 0
        ↓
replace only when it becomes ineligible,
BTC enters risk-off, or a vacancy exists
```

This is **entry-rank / eligibility-exit**. It directly targets name-switch churn without adding a rank-buffer threshold, minimum holding period or monthly calendar parameter.

Full result: [`research/results/AUDIT_0017_PIT_ALPHA_ATTRIBUTION_2026-08-04.md`](research/results/AUDIT_0017_PIT_ALPHA_ATTRIBUTION_2026-08-04.md)

Exact audit evidence: [`research/results/audit_0017_pit_alpha_attribution/`](research/results/audit_0017_pit_alpha_attribution/)

---

## Current research queue

### P0 — preregister the entry-rank / eligibility-exit experiment

The next experiment must:

- keep the complete PIT universe, 240-day age and $25m liquidity rules;
- keep the validated own/relative trend entry rank;
- keep gross<=1, BTC regime/core, 35% universal alt cap, 0.05 band and stated costs;
- replace incumbents only when they become ineligible or risk-off forces exit;
- report turnover decomposition, holding duration, right-tail capture, cost stress and subperiods;
- receive a new experiment ID;
- not tune an exit rank, minimum hold or calendar frequency.

### P1 — historical funding + Spot/Perp Router

Use accessible archives and separately attribute funding, fees, basis and slippage for an unchanged target exposure.

### P2 — Hyperliquid execution hardening

Metadata precision, fill reconciliation, partial fills, slicing, idempotency, L2 target-notional simulation, reduce-only emergency protection and testnet parity.

### P3 — leverage last

Do not reconsider 1.30–1.50 beta before universe, costs, funding and execution are controlled.

---

## Execution architecture

`execution/plan-b-bot/` contains the Hyperliquid testnet/shadow skeleton. It is not production-ready.

Known gaps:

- metadata-derived size precision;
- fill and reversal reconciliation;
- partial-fill/resting/rejected handling;
- order slicing;
- persistent idempotency and audit log;
- reduce-only emergency protection;
- endpoint hardening and mainnet double-confirmation;
- deterministic parity with research targets.

---

## Research discipline

- completed information only;
- t→t+1 no-lookahead execution;
- stated transaction costs included;
- preregister material tests;
- preserve later failed/inactive assets in historical eligibility;
- report the whole registered family rather than selecting a winner;
- rejected portfolio specifications remain rejected;
- mechanism validation is not portfolio promotion;
- attribution may authorize a structure, not tune thresholds;
- optimize future validity, not maximum historical CAGR.

Detailed stopping rules: [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)

Research evolution: [`docs/RESEARCH_HISTORY.md`](docs/RESEARCH_HISTORY.md)

Research roadmap: [`research/RESEARCH_ROADMAP_AFTER_0015.md`](research/RESEARCH_ROADMAP_AFTER_0015.md)

---

This repository is research software, not a representation that future returns will match backtests.
