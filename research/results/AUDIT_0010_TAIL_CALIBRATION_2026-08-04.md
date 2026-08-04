# AUDIT-0010-TAIL-CALIBRATION — 2026-08-04

Preregistered before the run. This audit changed no target weights and introduced no trading rule.

## Purpose

Test the prequential calibration of the frozen PCA4 BRRK 20-day scenario engine before adding conformal or downside-risk calibration. Each eligible monthly decision produced 5,000 Markov/Student-t 20-day V1 paths using information available through that decision date only. The following 20 realized daily V1 returns were then compared with forecast terminal-loss and path-drawdown tails.

44 decision forecasts had a complete subsequent 20-day realization.

## VaR95 coverage

| Forecast | Exceedances | N | Realized exceedance rate | Target | Wilson 95% CI |
|---|---:|---:|---:|---:|---:|
| Terminal loss VaR95 | 0 | 44 | 0.0% | 5% | 0.0%–8.03% |
| Correct path drawdown VaR95 | 0 | 44 | 0.0% | 5% | 0.0%–8.03% |
| Legacy path drawdown VaR95 | 0 | 44 | 0.0% | 5% | 0.0%–8.03% |

Mean realized-minus-forecast error:
- terminal loss VaR95: -20.28 percentage points;
- correct path drawdown VaR95: -12.64 percentage points;
- legacy path drawdown VaR95: -12.23 percentage points.

The 90th percentile of realized-minus-forecast error also remained negative for both terminal loss and path drawdown.

Interpretation: there is no evidence of risk undercoverage in this sample. A conformal *safety buffer* is therefore not justified by the observed prequential coverage. With only 44 forecasts, zero exceedances is not proof of stable overcoverage; the Wilson upper confidence limit still includes roughly 8%.

## Path-drawdown implementation issue discovered during the audit

The legacy BRRK path-tail function calculates running peaks beginning with the first simulated day's NAV. Mathematically, a forecast path starts at decision-time wealth=1, so wealth=1 must be included as the initial peak. The legacy definition therefore omits an immediate day-1 drawdown if the first simulated return is negative.

Across the 44 calibration forecasts:
- mean legacy predicted CDaR95: 24.31%;
- mean mathematically corrected predicted CDaR95: 24.74%;
- mean correction: +0.434 percentage points;
- maximum correction: +0.718 percentage points.

The error is modest but real, and CDaR enters the 0005/0006 scenario risk-budget calculation. It must therefore be corrected in a separately registered implementation-correction experiment before deployment. Existing frozen historical 0006 results remain preserved and are not silently overwritten.

## Decision

1. Do not add conformal buffers at this stage; the model is not exhibiting tail-risk undercoverage.
2. Do not infer that the model can safely be made more aggressive from only 44 forecasts. That would be a new optimization and requires a separate preregistered hypothesis.
3. Correct the path-drawdown definition and rerun 0006 with all other inputs unchanged.
4. Continue reporting tail calibration prospectively; additional realized forecasts will make coverage inference more informative over time.
