# ASYM-BETA-0022 Result — Downside-Semivol Extra Beta Works, Tail Cost Too High

`ASYM-BETA-0022-SEMIVOL` is the separately preregistered continuation after rejected `ASYM-BETA-0021`. It freezes corrected `BRRK-0011` and gives downside risk authority only over a new bull-only extra-beta sleeve.

## Status

**MECHANISM VALIDATED / NOT QUALIFIED FOR SHADOW YET.**

The first valid run completed in GitHub Actions run `30957522673`. No alternative downside window, volatility anchor, extra cap or gross cap was tested after seeing the result.

## Frozen rule

```text
BRRK-0011 core unchanged
        +
0.50 * max(existing BTC trend_score, 0)
        * (1 - exact BRRK-0009 p_bad)
        * min(1, 0.45 / BTC downside_semivol30)
        = extra beta
```

Extra beta is forced to zero whenever corrected BRRK core scale is below 1.0. Frozen V1 relative asset weights are scaled uniformly. No SOL or other asset-specific tilt is used.

Downside semivolatility is the annualized square-root lower partial moment about zero over the latest 30 completed BTC daily log returns:

`sqrt(mean(min(r,0)^2))*sqrt(365)`.

The 45% annualized anchor is inherited from the old positive-side total-volatility scaler; it was not selected from the 0022 PNL.

## Validation

- max absolute held-weight error versus persisted `BRRK0011_BASELINE`: **4.9997e-11**;
- max absolute strict-core equity error versus deterministic `ROUTER-PNL-0005`: **$0.0000013**;
- maximum final held gross: **1.4228x**, below the 1.50 hard cap;
- HMM convergence: **100%**;
- unit tests and workflow: passed.

## Exposure behavior

Across 45 walk-forward decisions:

- extra active: **21 / 45 decisions (46.67%)**;
- mean extra across all decisions: **+0.1330x**;
- mean extra when active: **+0.2850x**;
- maximum extra: **+0.4228x**;
- mean BTC downside semivol30: **28.50% annualized**;
- mean downside scaler: **0.9868**;
- downside scaler below 1 on only **8.89%** of decisions;
- mean `p_bad`: **0.2913**.

The semivol structure therefore solves the 0021 inertness problem, but the inherited 45% anchor is rarely binding when applied to downside semivolatility.

## Price-only result

| Strategy | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar | Avg gross | Max gross |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BRRK-0011 core | $62,247 | 65.17% | -33.72% | 44.21% | 1.353 | 1.933 | 0.754x | 1.000x |
| **ASYM-BETA-0022** | **$83,262** | **78.89%** | **-40.86%** | 53.79% | 1.346 | 1.931 | 0.889x | **1.423x** |

Monthly capture versus BTC:

- upside capture: **105.02% -> 127.60%**;
- downside capture: **72.99% -> 85.71%**.

This confirms the intended payoff change: materially more bull participation, but also materially more left-tail participation. Sharpe is essentially unchanged/slightly lower and Calmar is almost exactly unchanged.

## Current strict Router + native Hyperliquid funding

Common funding window: 2023-06-18 through 2026-07-31.

| Scenario | Final $10k | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| BRRK core strict Router | $40,178 | 56.20% | -34.95% | 1.229 | 1.608 |
| **ASYM-BETA-0022 strict Router** | **$47,236** | **64.52%** | **-42.42%** | 1.182 | 1.521 |
| ASYM-BETA-0022 all-perp stress | $36,713 | 51.75% | -44.28% | 1.035 | 1.169 |

The extra-beta mechanism remains economically positive after native Hyperliquid funding: strict-router CAGR gains about **8.32 percentage points** versus the BRRK strict core. However, the drawdown worsens by about **7.47 percentage points**, and both Sharpe and Calmar deteriorate.

## Annual price-only returns

| Year | BRRK core | ASYM-BETA-0022 |
|---|---:|---:|
| 2023 | 229.70% | **293.69%** |
| 2024 | 83.23% | **100.06%** |
| 2025 | 9.13% | **11.96%** |
| 2026 through Aug 2 | -5.57% | -5.57% |

The overlay adds upside in the intended positive regimes and remains off during the 2026 risk-off period.

## Dominant drawdown attribution

The maximum strict-router drawdown for both core and 0022 runs from the **2024-03-31 peak to the 2024-09-06 trough**.

The incremental damage is concentrated early in that drawdown:

| Month | BRRK strict core | 0022 strict Router | Incremental difference |
|---|---:|---:|---:|
| 2024-04 | -19.87% | **-25.88%** | **-6.01pp** |
| 2024-05 | +9.85% | +9.20% | -0.65pp |
| 2024-06 | -7.73% | **-11.07%** | **-3.35pp** |
| 2024-07 | +1.50% | +1.39% | -0.12pp |
| 2024-08 | -13.81% | -13.81% | 0.00pp |
| 2024-09 | same after extra was already off | same | ~0 |

Relevant monthly decisions:

- 2024-03-03: trend 0.968, `p_bad` 0.277, downside semivol 11.3%, extra **+0.350x**;
- 2024-04-02: trend 0.703, `p_bad` ~0, downside semivol 54.4%, scaler 0.828, extra **+0.291x**;
- 2024-06-01: trend 0.693, `p_bad` ~0, downside semivol 22.8%, scaler 1.0, extra **+0.346x**;
- 2024-07-01 onward: the extra sleeve was already largely/fully disabled before the later part of the drawdown.

This points to **intra-refit latency** as a plausible dominant conversion defect: the extra sleeve is sized only at the 30-day BRRK refit dates, so a downside-risk measure can become stale during a fast reversal even though the core model's slow cadence remains acceptable.

## Decision

1. Bull-only extra beta is a real mechanism: it materially increases upside and remains positive after native funding.
2. The 0022 implementation is **not** a shadow candidate yet because the left-tail deterioration is too large and risk-adjusted metrics worsen.
3. Do not tune the 30-day window, 45% anchor, 0.50 extra cap, 1.50 gross cap, p_bad or trend definition under 0022.
4. The next authorized work is a **no-trading-change latency attribution audit**. It should test whether daily evolution of already-defined downside semivol/p_bad/trend information would have warned during the dominant April/June 2024 loss windows before the next monthly refit.
5. Only that attribution may authorize one new structure. SOL-specific overweight remains a separate research question and is not inferred from 0022.
