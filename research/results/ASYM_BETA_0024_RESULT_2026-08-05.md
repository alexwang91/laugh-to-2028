# ASYM-BETA-0024 Result — Daily Overlay Cap Fixes Latency Partially, April Tail Remains

`ASYM-BETA-0024-DAILY-CAP` is the single structural change authorized by `AUDIT-0023-LATENCY`.

## Status

**LATENCY FIX VALIDATED / NOT YET SHADOW-QUALIFIED.**

The first valid run completed in GitHub Actions run `30958475344`. No alternate cadence, ratchet, threshold, semivol anchor, p_bad transformation or gross cap was tested.

## Frozen rule

- corrected `BRRK-0011` core remains monthly and unchanged;
- monthly approved extra is exactly the `ASYM-BETA-0022` rule;
- HMM parameters and raw-state conditional-risk distribution remain frozen within each 30-day interval;
- each completed day only updates the already-defined causal posterior, BTC trend and 30-day downside semivol;
- actual extra = `min(monthly approved extra, daily implied extra)`;
- the daily layer can never increase exposure above the monthly approved amount;
- existing `t -> t+1` execution and 0.05 L1 band remain unchanged.

## Validation

- BRRK held-weight reconstruction error: **4.9997e-11**;
- strict Router core reconstruction error: **$0.0000013**;
- reconstructed 0022 price-only final NAV error: **$0.00**;
- reconstructed 0022 strict-router final NAV error: **$0.00**;
- maximum held gross: **1.4228x**, below the 1.50 hard cap.

## Daily-cap behavior

Across 630 daily rows belonging to active monthly extra-beta intervals:

- daily cap binds on **339 days (53.81%)**;
- mean monthly approved extra on active days: **0.2850x**;
- mean realized daily extra after cap: **0.2420x**;
- mean reduction when binding: **0.0800x**;
- maximum reduction: **0.3345x**.

This fixes the stale-holding defect without materially increasing turnover.

## Price-only result

| Strategy | Final $10k | CAGR | MDD | Ann vol | Sharpe | Calmar | Turnover |
|---|---:|---:|---:|---:|---:|---:|---:|
| BRRK core | $62,247 | 65.17% | -33.72% | 44.21% | 1.353 | 1.933 | 91.23 |
| ASYM-BETA-0022 monthly | $83,262 | 78.89% | -40.86% | 53.79% | 1.346 | 1.931 | 108.97 |
| **ASYM-BETA-0024 daily cap** | **$82,389** | **78.37%** | **-39.95%** | **52.75%** | **1.357** | **1.962** | **109.25** |

Relative to 0022, daily cap gives up only about 0.52 percentage points of CAGR while improving MDD by about 0.91 percentage points, Sharpe from 1.346 to 1.357 and Calmar from 1.931 to 1.962.

Monthly capture versus BTC:

- upside capture: 0022 **127.60%** -> 0024 **125.44%**;
- downside capture: 0022 **85.71%** -> 0024 **83.38%**.

## Current strict Router + native Hyperliquid funding

Common funding window: 2023-06-18 through 2026-07-31.

| Scenario | Final $10k | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| BRRK core strict Router | $40,178 | 56.20% | -34.95% | 1.229 | 1.608 |
| ASYM-BETA-0022 monthly | $47,236 | 64.52% | -42.42% | 1.182 | 1.521 |
| **ASYM-BETA-0024 daily cap** | **$47,507** | **64.82%** | **-41.44%** | **1.199** | **1.564** |
| 0024 all-perp stress | $36,924 | 52.03% | -43.32% | 1.049 | 1.201 |

The daily cap is economically positive after native funding. It improves 0022 on **all four** funding-aware dimensions shown here: ending value/CAGR, MDD, Sharpe and Calmar.

The counterintuitive small CAGR increase versus 0022 after funding occurs because the daily cap removes some expensive perp exposure during periods where the gross extra was not sufficiently compensated by price return.

## Annual price-only returns

| Year | BRRK core | 0022 monthly | 0024 daily cap |
|---|---:|---:|---:|
| 2023 | 229.70% | 293.69% | **290.60%** |
| 2024 | 83.23% | 100.06% | **97.59%** |
| 2025 | 9.13% | 11.96% | **13.06%** |
| 2026 through Aug 2 | -5.57% | -5.57% | -5.57% |

## Known loss-window attribution

### April 2024

- BRRK strict core: **-19.87%**;
- 0022 monthly extra: **-25.88%**;
- 0024 daily cap: **-25.67%**.

Daily cap recovers only about **0.21 percentage points** versus 0022. This confirms the AUDIT-0023 conclusion that existing daily diagnostics did not identify the April reversal early enough.

### June 2024

- BRRK strict core: **-7.73%**;
- 0022 monthly extra: **-11.07%**;
- 0024 daily cap: **-10.04%**.

Daily cap recovers about **1.04 percentage points** versus 0022, validating the latency correction.

## Maximum drawdown

All three strict-router curves still peak on 2024-03-31 and trough on 2024-09-06:

- BRRK core: **-34.95%**;
- 0022 monthly: **-42.42%**;
- 0024 daily cap: **-41.44%**.

Therefore latency was real but not the dominant remaining tail problem. **April 2024 is now the primary unresolved failure episode.**

## Decision

1. Keep the daily-cap architecture as the better implementation of the 0022 extra-beta mechanism; it dominates monthly 0022 on funding-aware CAGR, MDD, Sharpe and Calmar.
2. Do not tune cadence, semivol window/anchor, p_bad, trend weights, 0.50 extra cap or 1.50 gross cap under 0024.
3. 0024 is still **not shadow-qualified** because the April left-tail remains too large relative to BRRK core.
4. The next work must return to **no-trading-change attribution** of April 2024 before adding any new risk control.
5. The first audit target should be decomposition of the already-frozen BTC trend score into its existing 20/60/120/240-day components and existing drawdown features. The question is whether long-horizon trend masked a short-horizon reversal; this is attribution, not permission to tune trend weights.
6. SOL-specific bull overweight remains a separate experiment after the general extra-beta risk architecture is stable.
