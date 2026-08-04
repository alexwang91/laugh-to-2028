# PIT-DISP-0015-DYNAMIC-UNIVERSE — Validated Result

Date: 2026-08-04

Status: **VALID RUN / PARTIAL MECHANISM VALIDATION / NO PRODUCTION PROMOTION**

This was the first successful execution of the frozen survivorship-aware dynamic-universe dispersion experiment. No preregistered universe, liquidity, history, signal, smoothing, cost, rebalance or risk parameter was changed after observing results.

## Data integrity

- Historical ordinary Binance spot-USDT candidates discovered: **652**.
- Symbols with historical rows: **646**.
- API calls: **1,120**.
- Fetch errors: **0**.
- Daily panel: 2020-08-11 through 2026-08-02.
- Evaluation: 2022-12-10 through 2026-08-02, 1,332 daily observations.
- Mean eligible dynamic-universe size: **30.62**.
- Median: **27**; maximum: **143**.
- Two evaluation dates had only four eligible assets; dispersion was undefined and the frozen rule correctly defaulted to scale 1.0 on those dates.
- **159 currently inactive/non-TRADING symbols were historically eligible**, including MATIC, FTM, EOS, WAVES, RNDR, BTT, XMR, LRC, OM and others.

This confirms that the test genuinely includes later inactive/delisted assets and is not a current-survivor reconstruction.

## Common-window metrics

| Strategy | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar | Path CDaR95 | Upside capture | Downside capture |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 baseline | $57,116 | 61.255% | -37.635% | 44.454% | 1.295 | 1.628 | 36.550% | 106.05% | 80.33% |
| V1 + fixed-panel DISP-0014 | $57,663 | 61.676% | -35.107% | 39.289% | 1.417 | 1.757 | 33.989% | 99.41% | 69.84% |
| V1 + dynamic PIT-DISP-0015 | $52,831 | 57.843% | -33.208% | 39.881% | 1.342 | 1.742 | 32.301% | 96.93% | 71.90% |
| **BRRK-0011 baseline** | **$62,247** | **65.104%** | **-33.715%** | 44.207% | **1.353** | **1.931** | 31.781% | **105.02%** | 72.99% |
| BRRK + fixed-panel DISP-0014 | $63,084 | 65.709% | -30.603% | 39.010% | 1.488 | 2.147 | 28.850% | 98.45% | 62.40% |
| **BRRK + dynamic PIT-DISP-0015** | **$56,543** | **60.809%** | **-30.398%** | 39.691% | **1.393** | **2.000** | **28.078%** | 95.92% | **65.71%** |

## What survived

Against BRRK-0011, the dynamic-universe overlay:

- improves MDD by **3.32 percentage points**;
- improves path CDaR95 by **3.70 percentage points**;
- lowers annualized volatility by **4.52 percentage points**;
- improves downside capture from **72.99% to 65.71%**;
- raises Sharpe from **1.353 to 1.393**;
- raises Calmar from **1.931 to 2.000**;
- lowers turnover from **91.23 to 87.25**.

Therefore broad point-in-time cross-sectional dispersion retains a real **risk-compression mechanism**. The effect is not eliminated by dead-pool inclusion.

## What failed

The dynamic overlay also:

- lowers CAGR from **65.10% to 60.81%** versus BRRK-0011;
- finishes about **$5,704 lower per $10,000 initial capital**;
- gives up roughly **9.10 percentage points of upside capture**;
- materially underperforms the fixed-panel DISP-0014 result on CAGR, Sharpe, Calmar and downside capture.

The dynamic and fixed-panel smoothed exposure scales have only **0.064 correlation** over the evaluation window. Their mean absolute scale difference is **0.122**, and the dynamic scale is below the fixed-panel scale on about **69.1%** of days.

This is the decisive finding: today's fixed BTC/ETH/SOL/BNB/XRP panel is **not a reliable proxy for broad historical market dispersion**. The attractive fixed-panel 0014 result is materially selection-sensitive.

## Subperiod behavior

For BRRK + dynamic PIT-DISP-0015:

- 2024 onward: CAGR 25.77% vs 27.85% baseline; MDD improves from -33.72% to -30.40%; Sharpe is only slightly higher, 0.806 vs 0.799.
- 2025 onward: CAGR 1.35% vs 1.91%; MDD improves from -32.25% to -28.43%, but Sharpe and Calmar are lower.
- 2026 through Aug 2: return -5.68% vs -5.57%; drawdown is lower, but risk-adjusted return is not improved.

Risk reduction persists, but post-2024 risk-adjusted improvement is not consistently strong enough for promotion.

## Exposure behavior and attribution

- Mean dynamic smoothed scale: **0.8981**.
- Median: **0.9417**.
- Scale below 0.90: **38.29%** of evaluation days.
- Scale below 0.50: **1.13%**.
- Minimum scale: **0.3285**.
- 37 contiguous episodes had scale below 0.90, covering 510 days.

Additive daily-return attribution shows both protection and opportunity cost across multiple episodes rather than one single event.

Largest protective episodes included:

- 2023-02-19 to 2023-03-12: about **+4.07pp** versus baseline;
- 2025-10-09 to 2025-11-01: **+2.99pp**;
- 2025-02-03 to 2025-03-04: **+2.73pp**;
- 2024-08-18 to 2024-09-06: **+2.41pp**.

Largest opportunity-cost episodes included:

- 2024-02-25 to 2024-04-10: about **-7.95pp**;
- 2025-04-13 to 2025-05-10: **-6.97pp**;
- 2023-11-27 to 2023-12-09: **-3.54pp**;
- 2023-12-19 to 2024-01-17: **-2.06pp**.

The overlay de-risks genuine selloffs, but also cuts exposure during several strong continuation rallies. That is the central economic trade-off.

## Decision

1. **BRRK-0011 remains the canonical research baseline.**
2. **DISP-0014 is downgraded** from strongest shadow candidate to a selection-sensitive fixed-panel diagnostic. It is not production eligible.
3. **PIT-DISP-0015 is retained as a broad-market risk diagnostic / shadow overlay**, not promoted as the default portfolio.
4. No threshold, liquidity floor, history requirement, horizon, minimum exposure or smoothing parameter may be tuned on this window.
5. The next major experiment is the already planned **point-in-time dynamic alpha universe**. The alpha layer must now face the same dead-pool test that the dispersion layer has completed.
6. A no-trading-change audit should separately study why fixed-panel and dynamic dispersion timing diverge, including universe-size, volume-selection and constituent-concentration effects.

## Current snapshot — 2026-08-02

- Dynamic eligible universe: **10 assets**.
- Dynamic dispersion: **0.24757**.
- Prior expanding median: **0.23409**.
- Raw dynamic scale: **0.94557**.
- Smoothed dynamic scale: **0.71791**.
- Fixed-panel scale: **0.99992**.
- BRRK final scale: **0.00960**.

The large current difference between broad-universe and fixed-panel scales is consistent with the low historical correlation between the two signals. It is a research diagnostic, not a standalone trading instruction.
