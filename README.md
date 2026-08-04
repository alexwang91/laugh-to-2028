# laugh-to-2028

一个以 **长期生存、可审计和减少回测自欺** 为目标的 crypto systematic allocation research project。

当前主线是：在 point-in-time、包含后来失败与退市资产的真实历史 universe 中，验证现有 alpha 和风险控制是否仍然成立，而不是继续在固定赢家币池上堆指标。

## Current status

| Layer | Evidence status | Decision |
|---|---|---|
| BTC dynamic beta | Frozen core concept | 保留 |
| Fixed-universe V1 rotation | Historical alpha, materially selection-biased | 不直接外推 |
| **BRRK-0011** | **Frozen research baseline** | 当前基线 |
| DISP-0013 | Benefit concentrated in few episodes | Shadow diagnostic only |
| DISP-0014 | Strong fixed-panel result, now shown selection-sensitive | **不 promotion** |
| **PIT-DISP-0015** | **Valid survivorship-aware run; partial risk-mechanism validation** | Shadow risk diagnostic |
| Dynamic alpha universe | Not tested yet | **Next P0 research task** |
| Historical funding-aware PnL | Not validated | HTTP 451 / archive work pending |
| Hyperliquid Plan B | Testnet / shadow implementation | Not production-ready |

## Exact daily backtest PNL

![Exact daily backtest PNL](docs/pnl.svg)

> 上图来自 PIT-DISP-0015 成功运行后持久化的 **1,332 个真实日级净值点**，不再是年度收益复利近似。对应 CSV、held weights、动态币池规模、dispersion scale 和 inactive-symbol audit 位于 `research/results/pit_disp_0015/`。

### Common evaluation window

2022-12-10 至 2026-08-02；completed UTC daily data；t 日信息作用于 t+1；0.05 L1 rebalance band；5 bps / absolute weight change。

| Strategy | Final $10k | CAGR | MDD | Ann Vol | Sharpe | Calmar | Path CDaR95 | Up capture | Down capture |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 baseline | $57,116 | 61.255% | -37.635% | 44.454% | 1.295 | 1.628 | 36.550% | 106.05% | 80.33% |
| V1 + fixed DISP-0014 | $57,663 | 61.676% | -35.107% | 39.289% | 1.417 | 1.757 | 33.989% | 99.41% | 69.84% |
| V1 + dynamic PIT-0015 | $52,831 | 57.843% | -33.208% | 39.881% | 1.342 | 1.742 | 32.301% | 96.93% | 71.90% |
| **BRRK-0011 baseline** | **$62,247** | **65.104%** | **-33.715%** | 44.207% | **1.353** | **1.931** | 31.781% | **105.02%** | 72.99% |
| BRRK + fixed DISP-0014 | $63,084 | 65.709% | -30.603% | 39.010% | 1.488 | 2.147 | 28.850% | 98.45% | 62.40% |
| **BRRK + dynamic PIT-0015** | **$56,543** | **60.809%** | **-30.398%** | 39.691% | **1.393** | **2.000** | **28.078%** | 95.92% | **65.71%** |

## PIT-DISP-0015: decisive result

The frozen point-in-time rules were executed without post-result parameter changes:

```text
historical ordinary Binance spot-USDT candidates
    ↓
240 consecutive completed daily rows
    ↓
completed-day quote volume >= $25m
    ↓
minimum valid cross-section = 5
    ↓
20d cumulative-log-return cross-sectional dispersion
    ↓
raw scale = clip(expanding prior median / dispersion, 0.10, 1.00)
    ↓
g_t = 0.80 × g_(t-1) + 0.20 × raw scale
    ↓
scale frozen V1 exposure toward cash
```

### Data integrity

- 652 historical ordinary USDT candidates discovered;
- 646 returned historical rows;
- 1,120 API calls and **zero fetch errors**;
- mean eligible universe 30.62 assets, median 27, maximum 143;
- **159 currently inactive/non-TRADING symbols were historically eligible**;
- examples include MATIC, FTM, EOS, WAVES, RNDR, BTT, XMR, LRC and OM.

This is a genuine dead-pool-inclusive reconstruction rather than a backtest on today's survivors.

### What survived

Against BRRK-0011, dynamic broad-market dispersion:

- improves MDD by about **3.32 percentage points**;
- improves path CDaR95 by about **3.70 points**;
- lowers annualized volatility by about **4.52 points**;
- lowers downside capture from **72.99% to 65.71%**;
- raises Sharpe from **1.353 to 1.393**;
- raises Calmar from **1.931 to 2.000**;
- reduces turnover.

Therefore cross-sectional dispersion contains a real risk-compression mechanism that survives point-in-time universe construction.

### What did not survive

The same overlay:

- lowers CAGR from **65.10% to 60.81%** versus BRRK-0011;
- finishes about **$5,704 lower per $10,000 initial capital**;
- lowers upside capture from 105.02% to 95.92%;
- underperforms fixed-panel DISP-0014 on CAGR, Sharpe, Calmar and downside capture.

The fixed-panel and dynamic smoothed scales have only **0.064 correlation**. Their mean absolute difference is 0.122, and dynamic exposure is below the fixed-panel exposure on about 69.1% of days.

**Conclusion:** BTC/ETH/SOL/BNB/XRP fixed-panel dispersion is not a reliable proxy for broad historical crypto dispersion. The attractive DISP-0014 result is materially selection-sensitive.

## Canonical research decision

1. **BRRK-0011 remains the canonical research baseline.**
2. **DISP-0014 is downgraded** to a selection-sensitive fixed-panel diagnostic; it is not production eligible.
3. **PIT-DISP-0015 is retained** as a broad-market risk diagnostic / shadow overlay, not as the default portfolio.
4. No PIT-0015 threshold, liquidity floor, age rule, horizon, exposure floor or smoothing parameter will be tuned on this window.
5. The next major test is a **point-in-time dynamic alpha universe**. The V1 alpha layer must now face the same dead-pool test.

Full result: [`research/results/PIT_DISP_0015_RESULT_2026-08-04.md`](research/results/PIT_DISP_0015_RESULT_2026-08-04.md)

Exact outputs: [`research/results/pit_disp_0015/`](research/results/pit_disp_0015/)

## What we built

### 1. BTC Dynamic Beta

Completed UTC daily candles only: 20/60/120/240-day risk-adjusted momentum plus 30-day realized volatility. Negative-trend beta contracts toward 0.18–0.65; positive trend permits expansion above 1.0. Manual “last drop / bottom recovery” jumps were tested and rejected.

### 2. V1 Rotation

BTC defines regime. In risk-off, alt exposure is zero. In risk-on, an alt must have both positive absolute trend and positive relative-to-BTC trend before ranking and allocation.

The early fixed BTC/ETH/SOL/BNB result was strong, but SOL dominated historical alpha and the edge weakened materially after 2024. The next alpha test therefore cannot preselect today's winners.

### 3. BRRK regime risk layer

Early HMM alpha/reallocation variants sacrificed too much upside. BRRK restricts the regime model to risk authority: default to V1 and grant de-risking authority mainly when Risk-Off probability is high.

`BRRK-0011` is the corrected path-CDaR implementation baseline:

- CAGR 65.10%;
- MDD -33.72%;
- Sharpe 1.353;
- Calmar 1.931;
- downside capture 72.99%.

The mathematical CDaR correction had negligible economic impact, so the historical advantage was not created by the old drawdown implementation bug.

### 4. Dispersion research

- `DISP-0013`: extreme dispersion redirects alt exposure to BTC. Headline improvement was concentrated in a small late-2024 cluster; shadow only.
- `DISP-0014`: fixed five-asset median-ratio exposure scaling. Strong fixed-panel risk metrics, but PIT-0015 shows its timing is selection-sensitive.
- `PIT-DISP-0015`: broad point-in-time dispersion. Real risk compression, but insufficient growth/risk trade-off for promotion.

## Current snapshot — completed 2026-08-02 candle

- dynamic eligible universe: 10 assets;
- dynamic dispersion: 0.24757;
- prior expanding median: 0.23409;
- raw dynamic scale: 0.94557;
- smoothed dynamic scale: 0.71791;
- fixed-panel scale: 0.99992;
- BRRK final scale: 0.00960.

The broad and fixed-panel risk signals strongly disagree in this snapshot, consistent with their low historical correlation. This is a research diagnostic, not a standalone trade instruction.

## Funding status

The attempted Binance USD-M funding endpoint returned HTTP 451 on GitHub-hosted infrastructure. Therefore:

- no valid historical funding-aware PNL exists yet;
- current funding thresholds remain policy heuristics, not statistical optimization;
- future work must use accessible historical archives and separately attribute spot/perp carry, fees, basis and slippage.

## Execution architecture

`execution/plan-b-bot/` contains the Hyperliquid testnet/shadow skeleton:

```text
completed UTC daily candle
        ↓
trend / volatility signal
        ↓
target beta or portfolio weights
        ↓
account NAV and current exposure
        ↓
target position delta
        ↓
Hyperliquid testnet / shadow execution
```

Open engineering items include metadata-derived size precision, fill reconciliation, partial fills, slicing, persistent idempotency/audit logs, reduce-only emergency protection, endpoint hardening and mainnet safeguards.

## Next steps

1. **P0 — dynamic point-in-time alpha universe:** determine whether own-trend + relative-strength alpha survives when historical candidates include later failures and delistings.
2. **P0 audit — fixed vs dynamic dispersion identity:** no trading change; explain divergence through breadth, universe size, constituent concentration and volume selection.
3. **P1 — historical funding + Spot/Perp Router:** optimize implementation cost for an unchanged target exposure.
4. **P2 — risk allocation:** only after dynamic alpha validation, test covariance/risk contribution and downside/LPM estimators one module at a time.
5. **P3 — Hyperliquid execution hardening:** complete testnet reconciliation and operational controls.
6. **P4 — leverage:** reconsider 1.30–1.50 beta only after universe, funding and execution validation.

Detailed stopping rules: [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)

Research evolution: [`docs/RESEARCH_HISTORY.md`](docs/RESEARCH_HISTORY.md)

Migration scope: [`docs/MIGRATION_MANIFEST.md`](docs/MIGRATION_MANIFEST.md)

## Repository layout

```text
.
├── README.md
├── docs/
│   ├── pnl.svg
│   ├── RESEARCH_HISTORY.md
│   ├── NEXT_STEPS.md
│   └── MIGRATION_MANIFEST.md
├── research/
│   ├── core/
│   ├── pit_universe/
│   ├── results/
│   │   └── pit_disp_0015/
│   └── ...
└── execution/
    └── plan-b-bot/
```

## Research discipline

- completed information only;
- no lookahead;
- stated transaction costs included;
- preregister material experiments;
- rejected experiments remain rejected absent independent evidence;
- report full registered families rather than selecting PNL winners;
- preserve dead/delisted assets in historical eligibility;
- do not tune PIT-0015 after this result;
- optimize future validity, not maximum historical CAGR.

---

This repository is research software, not a representation that future returns will match backtests.
