# ASYM-BETA-0021 Result — Absolute Tail-Budget Overlay Gate Rejected

`ASYM-BETA-0021` tested one preregistered structural change on top of corrected `BRRK-0011`: a uniform bull-only extra-beta sleeve capped at `+0.50` V1 scale, with the frozen BRRK core retaining absolute de-risking authority.

## Status

**REJECTED — structurally inert.**

The first valid run completed in GitHub Actions run `30956929530`. No parameter was changed after observing the result.

## Validation

The implementation passed both hard reconstruction gates:

- max absolute held-weight error versus persisted `BRRK0011_BASELINE`: **4.9997e-11**;
- max absolute strict-router equity error versus deterministic `ROUTER-PNL-0005` reconstruction: **$0.0000013**.

The earlier failed CI attempts were implementation/dependency diagnostics only: the first compared target weights against PIT-0015 persisted held weights; the second expected a 0005 daily artifact that had not been persisted to main. Neither changed the trading specification.

## Frozen extra-beta rule

```text
candidate extra = 0.50 * max(existing BTC trend_score, 0)
        ↓
* (1 - exact BRRK-0009 p_bad)
        ↓
limited by max(0, safe_total_scale - 1)
        ↓
safe_total_scale = largest total V1 scale <= 1.50
satisfying the existing 20-day CVaR95 <= 20%
and corrected CDaR95 <= 20%
```

Extra beta also had zero authority whenever the corrected BRRK core scale was below 1.0. No SOL or other asset-specific tilt was allowed.

## Result

Across **45** walk-forward decisions:

- extra-active decisions: **0 / 45**;
- mean extra scale: **0.0000**;
- maximum extra scale: **0.0000**;
- mean modeled safe total scale: **0.8313**;
- maximum realized total scale: **1.0000**;
- mean `p_bad`: **0.2913**;
- HMM convergence rate: **100%**.

Therefore `ASYM-BETA-0021` is exactly equal to the frozen BRRK baseline.

### Price-only

| Strategy | Final $10k | CAGR | MDD | Sharpe | Calmar | Avg gross | Max gross |
|---|---:|---:|---:|---:|---:|---:|---:|
| BRRK-0011 core | $62,247 | 65.17% | -33.72% | 1.353 | 1.933 | 0.7543 | 1.0000 |
| ASYM-BETA-0021 | $62,247 | 65.17% | -33.72% | 1.353 | 1.933 | 0.7543 | 1.0000 |

### Current strict Router + native Hyperliquid funding

Common funding window: 2023-06-18 through 2026-07-31.

| Scenario | Final $10k | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| BRRK core, BTC spot + other core perps | $40,178 | 56.20% | -34.95% | 1.229 | 1.608 |
| ASYM-BETA-0021 strict router | $40,178 | 56.20% | -34.95% | 1.229 | 1.608 |
| ASYM-BETA-0021 all-perp stress | $31,228 | 44.08% | -37.04% | 1.046 | 1.190 |

## Interpretation

This result does **not** reject higher bull-market exposure.

It rejects a specific permission structure: using the old **absolute** 20% CVaR/CDaR scenario budget as the gate for exposure above 1x. In many positive-trend periods the scenario engine estimates a safe absolute scale below 1 even while the successful BRRK authority structure deliberately keeps the non-RISK_OFF core at full exposure. Reusing that absolute budget for the overlay therefore makes the overlay impossible by construction.

This is consistent with the earlier BRRK lesson: the risk model works when its authority is narrow. It should not be allowed to re-underwrite the already accepted core while deciding whether a separate extra-beta sleeve is permissible.

## Stopping rule

Do **not** tune the 20% budget, the `0.50` cap, `p_bad`, trend weights, PCA/state model or gross cap under experiment ID 0021.

The only justified continuation is a separately preregistered experiment in which downside risk controls the **incremental overlay risk**, while `BRRK-0011` remains frozen and outside that new risk model's authority.
