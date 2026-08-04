# DISP-0013-ALT-RELIABILITY — 2026-08-04

Preregistered before the first run. The only trading change is a cross-sectional-dispersion reliability overlay on the frozen V1 alt sleeve. Dispersion is the sample standard deviation of trailing 20-day log returns across ETH/SOL/BNB/XRP. Its empirical percentile is computed against strictly earlier observations only. The primary gate is inactive at or below the 90th percentile and then decays linearly from 1 to 0 between the 90th and 100th percentile. Removed ETH/SOL/BNB weight is transferred to BTC, so gross exposure is preserved before any BRRK scale.

The BRRK comparator is frozen BRRK-0006 authority logic with the BRRK-0011 corrected path-CDaR implementation. BRRK risk scale is still estimated from frozen V1; it is not reoptimized on the dispersion-adjusted portfolio.

Evaluation: 2022-12-10 through 2026-08-02, 5 bps per absolute weight change, 0.05 L1 rebalance band, no lookahead.

## Primary result

| Strategy | CAGR | MaxDD | Sharpe | Calmar | Path CDaR95 | Turnover | Upside capture | Downside capture |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V1 | 61.255% | -37.635% | 1.2950 | 1.6276 | 36.550% | 93.187 | 106.047% | 80.327% |
| V1 + dispersion | **63.598%** | -37.635% | **1.3286** | **1.6899** | 36.550% | **89.578** | **106.596%** | **77.999%** |
| BRRK-0011 | 65.104% | -33.715% | 1.3532 | 1.9310 | 31.781% | 91.228 | 105.021% | 72.993% |
| BRRK-0011 + dispersion | **67.503%** | -33.715% | **1.3870** | **2.0022** | 31.781% | **87.619** | **105.571%** | **70.665%** |

The primary overlay improves CAGR, Sharpe, Calmar and both upside/downside capture asymmetry without changing headline maximum drawdown. Turnover also falls.

## Activation diagnostics

- primary gate active on ~2.03% of evaluation days;
- gate below 0.5 on ~1.13% of days;
- mean gate 0.9897; median gate 1.0;
- mean V1 alt sleeve 23.02% versus 22.83% after the overlay;
- when active, mean alt-weight reduction was ~9.14 percentage points;
- on 2026-08-02, dispersion percentile was only ~9.20%, so the current gate was 1.0.

This is therefore a sparse state-dependent intervention, not a persistent de-risking rule.

## Preregistered threshold family

The 80% and 95% tail-start sensitivities were registered before results and are diagnostic only. They must not be used to select a PnL-optimal threshold.

| Tail start | V1 CAGR | V1 Calmar | BRRK CAGR | BRRK MaxDD | BRRK Sharpe | BRRK Calmar | Active days |
|---|---:|---:|---:|---:|---:|---:|---:|
| 80% | 66.657% | 1.7710 | 70.635% | -33.668% | 1.4358 | 2.0980 | 6.16% |
| **90% primary** | **63.598%** | **1.6899** | **67.503%** | **-33.715%** | **1.3870** | **2.0022** | **2.03%** |
| 95% | 62.928% | 1.6721 | 66.817% | -33.715% | 1.3769 | 1.9818 | 1.13% |

All three preregistered directions improve the corresponding baseline on CAGR/Sharpe/Calmar, which is supportive of the mechanism. The apparently strongest 80% result is not eligible for selection from this run.

## Subperiod structure

The improvement is not uniform across years.

For BRRK-0011 + primary dispersion:
- from 2023-01-01: CAGR 66.50% -> 68.96%;
- from 2024-01-01: CAGR 27.85% -> 30.40%, Sharpe 0.799 -> 0.847;
- from 2025-01-01: no change;
- from 2026-01-01: no change.

Calendar-year returns show the main difference in 2024:
- 2023: 229.70% -> 230.20%;
- 2024: **83.23% -> 92.83%**;
- 2025: unchanged at 9.13%;
- 2026 through Aug 2: unchanged at -5.57%.

This concentration means the next required step is event/activation attribution rather than immediate promotion.

## Research decision

1. Do not replace BRRK-0011 yet.
2. Retain DISP-0013 as a promising candidate because the full preregistered 80/90/95 family points in the same direction and the primary rule is sparse.
3. Perform a no-trading-change activation attribution audit to determine whether the improvement is diversified across episodes or dominated by one or two 2024 events.
4. Independently test the externally specified literature formula (expanding-median dispersion ratio, minimum exposure 0.10, recursive smoothing lambda=0.80) under a new experiment ID. Do not modify DISP-0013 after seeing this result.
5. A positive fixed-panel result remains provisional because the 2026 paper stresses point-in-time universe construction and survivorship sensitivity. A future dynamic-universe test is required before production promotion.
