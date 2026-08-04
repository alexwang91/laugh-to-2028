# 0006 Robustness + Cycle Reentry — 2026-08-04

## Frozen 0006 robustness audit

AUDIT-0006-ROBUSTNESS-01 was preregistered before the run. BRRK-0006 parameters were not changed.

### Cost stress

| Cost bps | CAGR | MaxDD | Sharpe | Calmar |
|---:|---:|---:|---:|---:|
| 5 | 65.13% | -33.72% | 1.354 | 1.932 |
| 10 | 63.07% | -34.23% | 1.325 | 1.843 |
| 20 | 59.03% | -35.24% | 1.268 | 1.675 |
| 50 | 47.47% | -38.18% | 1.096 | 1.244 |

### Overlay execution delay stress

| Delay | CAGR | MaxDD | Sharpe | Calmar |
|---:|---:|---:|---:|---:|
| 0d | 65.13% | -33.72% | 1.354 | 1.932 |
| 1d | 65.43% | -33.72% | 1.358 | 1.941 |
| 3d | 64.66% | -33.72% | 1.347 | 1.918 |
| 7d | 59.15% | -33.72% | 1.272 | 1.754 |

### Start-date stability versus V1

0006 remained ahead of V1 in CAGR and Calmar for all preregistered starts: 2022-12-10, 2023-03-01, 2023-06-01, and 2024-01-01.

### Stationary block bootstrap versus V1

- mean block 7d: terminal outperformance probability 87.32%; 5% annualized return-difference quantile -0.94pp.
- mean block 21d: 87.08%; 5% quantile -0.68pp.
- mean block 63d: 89.40%; 5% quantile -0.32pp.

Interpretation: evidence is encouraging but does not establish 95% statistical dominance; the lower tail still includes modest underperformance.

## CYCLE-0001-CAPITULATION-REENTRY

This experiment was preregistered with standardized one-sided CUSUM k=0.5/h=5, 60d volatility normalization, and a 20d EMA recovery confirmation. Recovery was allowed only to release 0006 suppression back to frozen V1; it could not force exposure above V1.

### Common-window result, 2022-12-10 to 2026-08-02

| Model | CAGR | MaxDD | Sharpe | Calmar | CDaR95 |
|---|---:|---:|---:|---:|---:|
| CYCLE-0001 | 62.42% | -36.18% | 1.314 | 1.725 | 35.46% |
| BRRK-0006 | 65.13% | -33.72% | 1.354 | 1.932 | 31.74% |
| V1 | 61.25% | -37.63% | 1.295 | 1.628 | 36.55% |

Decision: CYCLE-0001 does not replace 0006. The detector is retained as a diagnostic only; thresholds are not tuned after this result.

### Historical detector timing

2018 cycle:
- capitulation arms: 2018-11-16 and 2018-11-20
- recovery release: 2019-05-11

2022 cycle:
- capitulation arms: 2022-06-13 and 2022-11-09
- recovery release: 2023-01-13

The detector identifies the broad crash/recovery order but releases too slowly to improve 0006.

### Current cycle diagnostic

At 2026-08-02 the detector state is CAPITULATION_ARMED, not RECOVERY_RELEASED. It therefore does not provide evidence that the hypothesized final capitulation has completed.

## Automated signal generation

A deterministic Daily 0006 Signal workflow now exists. It uses only completed UTC daily candles, fits the current 0006 decision point, and emits `latest_0006_signal.json` with posterior state probabilities, frozen V1 weights, final 0006 scale, target weights, rebalance band, and the cycle detector as a non-trading diagnostic.

First automated signal run used completed candle 2026-08-03:
- P(RISK_OFF): 99.9971%
- meta scale: 0
- final 0006 scale: 0.00291%
- frozen V1 BTC weight: 38.86%
- resulting research target gross exposure: approximately 0.00113%
- cycle diagnostic: CAPITULATION_ARMED

The workflow is scheduled at 01:10 UTC daily. GitHub scheduled workflows execute from the default branch, so the schedule becomes active after this workflow is merged into the repository default branch. The current output is research/shadow signal generation only; an execution adapter must still enforce account-state, leverage, funding/cost, order-fill and kill-switch checks before live orders.
