# DISP-0014-MEDIAN-RATIO-REPLICATION — 2026-08-04

External-formula transfer test. Parameters were fixed from the 2026 cryptocurrency-dispersion literature/reproduction description before the first run: 20-day cross-sectional cumulative-log-return dispersion, expanding historical median target, raw exposure `clip(target/current, 0.10, 1.00)`, and recursive smoothing `g_t=0.80*g_{t-1}+0.20*raw_t`. The gate scales the entire V1 exposure and sends removed exposure to cash. No parameter was selected from DISP-0013 PnL.

Evaluation: 2022-12-10 through 2026-08-02, fixed BTC/ETH/SOL/BNB/XRP proxy panel, 5 bps transaction cost, 0.05 L1 rebalance band, no lookahead.

## Result

| Strategy | CAGR | MaxDD | Ann vol | Sharpe | Calmar | Path CDaR95 | Avg gross | Upside capture | Downside capture |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | 61.255% | -37.635% | 44.454% | 1.295 | 1.628 | 36.550% | 0.795 | 106.05% | 80.33% |
| V1 + literature dispersion | 61.676% | **-35.107%** | **39.289%** | **1.417** | **1.757** | **33.989%** | 0.716 | 99.41% | **69.84%** |
| BRRK-0011 | 65.104% | -33.715% | 44.207% | 1.353 | 1.931 | 31.781% | 0.754 | 105.02% | 72.99% |
| BRRK-0011 + literature dispersion | **65.709%** | **-30.603%** | **39.010%** | **1.488** | **2.147** | **28.850%** | 0.675 | 98.45% | **62.40%** |

The externally specified formula therefore behaves primarily as a risk overlay, not an alpha enhancer. It gives up some upside capture but substantially improves drawdown, volatility, CVaR/CDaR and downside capture, with a modest positive CAGR change.

## Exposure behavior

- mean raw scale: 0.9222;
- mean smoothed scale: 0.9221;
- median smoothed scale: 0.9945;
- smoothed scale below 0.90 on ~22.60% of evaluation days;
- below 0.50 on ~2.25%;
- minimum smoothed scale 0.2261;
- on 2026-08-02 current scale was ~0.99992, i.e. no present dispersion de-risking.

## Annual behavior, BRRK

- 2023: 229.70% baseline vs 198.84% with literature dispersion — meaningful upside sacrifice;
- 2024: 83.23% vs 91.36% — improvement;
- 2025: 9.13% vs 16.81% — improvement;
- 2026 through Aug 2: -5.57% vs -5.55% — effectively unchanged.

From 2024 onward, the overlay raises CAGR from 27.85% to 33.48%, cuts MDD from -33.72% to -30.60%, and raises Sharpe from 0.799 to 0.965. From 2025 onward it raises CAGR from 1.91% to 6.39% while reducing MDD from -32.25% to -29.37%.

## Comparison with DISP-0013

The two experiments imply different economic mechanisms:
- DISP-0013 redirects extreme-dispersion alt exposure to BTC and is more aggressive: BRRK CAGR ~67.50%, MDD ~-33.72%, Calmar ~2.00. Its realized benefit is highly concentrated in late-2024 episodes.
- DISP-0014 scales total portfolio exposure into cash and is more defensive: BRRK CAGR ~65.71%, MDD ~-30.60%, Calmar ~2.15. Its risk improvement is broader across subperiods but sacrifices upside capture.

Do not combine or choose between them by the same historical PnL window. The next decisive research step is a survivorship-aware point-in-time universe test. Until that passes, BRRK-0011 remains the production research baseline and DISP-0014 is a strong shadow risk-overlay candidate.
