# BRRK-0011-CDAR-CORRECTION — 2026-08-04

Preregistered implementation correction. The only change versus legacy frozen BRRK-0006 is the mathematically correct path-drawdown definition: simulated wealth begins at decision-time NAV=1, so NAV=1 is included as the initial running peak before the first simulated daily return.

No alpha rule, HMM specification, state count, PCA factor count, scenario count, horizon, Student-t df, risk budget, rebalance band, cost, seed policy, or final-scale formula was changed.

## Result

Window: 2022-12-10 through 2026-08-02.

| Model | CAGR | MaxDD | Sharpe | Calmar | Realized path CDaR95 | Turnover | Avg gross | Upside capture | Downside capture |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Corrected 0011** | **65.104%** | **-33.715%** | **1.3532** | **1.9310** | 31.781% | 91.228 | 0.75430 | 105.021% | 72.993% |
| Legacy frozen 0006 | 65.132% | -33.715% | 1.3535 | 1.9318 | 31.742% | 91.231 | 0.75443 | 105.043% | 72.997% |
| V1 | 61.255% | -37.635% | 1.2950 | 1.6276 | 36.550% | 93.187 | 0.79482 | 106.047% | 80.327% |

$10,000 final value:
- corrected 0011: $62,247.38
- legacy 0006: $62,286.62

The correction therefore has negligible economic impact on the headline result.

## Decision-level impact

Across 45 monthly decisions:
- final-scale changes >1bp: 2 decisions;
- final-scale changes >1 percentage point: 1 decision;
- mean absolute final-scale change: 0.0394 percentage points;
- maximum absolute final-scale change: 1.7265 percentage points;
- mean signed change: -0.0394 percentage points.

The largest material change occurred around 2026-03-23, where corrected final scale was ~97.47% versus legacy ~99.19%. Most decisions were exactly or effectively unchanged.

At 2026-07-21 the corrected and legacy final scales were identical (~0.9601% of V1). Corrected full-scale scenario CDaR95 was ~16.33%, below the frozen 20% risk budget, while the meta allocator still selected zero because expected log growth favored no V1 exposure under the inferred Risk-Off state.

## Interpretation

The legacy path-drawdown definition was mathematically incorrect, but the error was small enough that it did not create the BRRK-0006 performance advantage. Correcting it reduces CAGR by only ~0.03 percentage points/year and leaves drawdown, capture and risk-adjusted metrics essentially unchanged.

## Engineering decision

The corrected path-drawdown definition is the implementation baseline from this point forward. Legacy 0006 historical results remain preserved for auditability, but daily/shadow/live signal generation should use the corrected `choose_scale_corrected` implementation before deployment.
