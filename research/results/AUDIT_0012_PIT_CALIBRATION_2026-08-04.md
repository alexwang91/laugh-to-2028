# AUDIT-0012-PIT-CALIBRATION — 2026-08-04

Preregistered, no trading changes. The frozen PCA4 BRRK scenario engine generated 5,000 strictly prequential 20-day Student-t/Markov V1 paths at each monthly decision. Realized following-20-day terminal returns and BRRK-0011-corrected maximum drawdown magnitudes were evaluated inside their full predictive distributions.

44 forecasts had complete 20-day realizations.

## Terminal-return PIT

- mean PIT: 0.5149
- median: 0.4835
- PIT variance: 0.0761 versus Uniform reference 0.0833
- mean absolute distance from 0.5: 0.2341 versus Uniform reference 0.25
- bottom 10%: 2 / 44
- top 10%: 6 / 44
- central 40%–60%: 9 / 44
- KS statistic: 0.0944
- KS p-value: 0.7930

Interpretation: with this small sample there is no evidence that the terminal-return predictive distribution is materially miscalibrated. It is neither obviously too narrow nor systematically shifted to one side.

## Maximum-drawdown PIT

- mean PIT: 0.3852
- median: 0.3957
- PIT variance: 0.0879 versus Uniform reference 0.0833
- mean absolute distance from 0.5: 0.2728
- bottom 10%: 12 / 44
- top 10%: 1 / 44
- central 40%–60%: 8 / 44
- KS statistic: 0.2239
- KS p-value: 0.0203

Because the drawdown PIT is the predictive CDF of simulated maximum-drawdown magnitude evaluated at the realized magnitude, the strong concentration at low PIT values means realized drawdowns are frequently smaller than the model's simulated drawdown distribution. The path-risk model is therefore directionally conservative/overpredictive for maximum drawdown on this sample, not underprotective.

This is consistent with AUDIT-0010, which observed zero 95% drawdown-VaR exceedances in 44 forecasts.

## Decision

1. Do not increase Student-t tail thickness; terminal-return calibration does not justify it and drawdown forecasts are already conservative.
2. Do not add a conformal safety buffer; no undercoverage has been observed.
3. Do not immediately relax the 20% drawdown budget from these 44 observations; that would turn a calibration audit into PnL-driven risk-budget optimization.
4. Future risk research should separate terminal loss from path drawdown instead of assuming one scenario distribution must be equally calibrated for both functionals.
5. Continue prospective PIT/coverage collection. If drawdown overprediction persists in genuinely forward data, a separately preregistered path-risk recalibration (for example quantile mapping or downside/LPM-based path control) becomes justified.

The current implementation baseline remains BRRK-0011: frozen BRRK-0006 logic with corrected path-CDaR definition.
