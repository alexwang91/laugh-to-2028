# ROUTER-PNL-0005 Result — Strict Verified-Spot Accounting

`ROUTER-PNL-0005` is an **exploratory post-audit accounting diagnostic**, not preregistered router-promotion evidence. It was computed after `ROUTER-DATA-0004` had established the current spot classifications.

## Frozen accounting rule

- keep the exact BRRK price-return path and original backtest trading-cost assumption;
- derive spot eligibility only from the durable `ROUTER-DATA-0004` classification;
- route only `verified_exact` or `verified_official_ui_remap` assets to zero-funding spot treatment;
- retain native Hyperliquid perp funding for every other target;
- do not change targets, weights, signals, leverage or select a funding threshold.

Current strict routing classification:

```text
BTC -> spot accounting
ETH -> perp
SOL -> perp
BNB -> perp
XRP -> perp
```

Historical spot fees, basis and slippage are **not included** because no valid historical series has yet been established. This experiment isolates the funding component only.

## Validation

GitHub Actions run `30954274000` completed successfully.

The code first reconstructed the persisted `HYPERLIQUID_ALL_PERP_NATIVE` daily curve from block-level funding attribution. Maximum absolute equity reconstruction error was only **$0.0000015**, validating the accounting path before changing instrument treatment.

Artifact: `router-pnl-0005-results` (`8910374698`).

## Main result

Common Hyperliquid window: 2023-06-18 through 2026-07-31, 1,140 daily observations.

| Scenario | Final $10k | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|---:|
| Price-only upper bound | $47,998 | 65.37% | -33.72% | 1.355 | 1.939 |
| Hyperliquid all-perp | $31,228 | 44.08% | -37.04% | 1.046 | 1.190 |
| **Strict verified spot: BTC only** | **$40,178** | **56.20%** | **-34.95%** | **1.229** | **1.608** |

Moving only the currently verified BTC exposure from perp funding treatment to spot recovers about **12.13 percentage points of CAGR** versus the all-perp implementation, while leaving all directional targets unchanged.

## Mechanical counterfactual attribution

These scenarios are **not routing approvals**. They show how much funding drag is associated with each candidate asset if a later identity/availability audit were to authorize spot treatment.

| Spot-treated assets | CAGR | MDD | Sharpe | Status |
|---|---:|---:|---:|---|
| BTC only | 56.20% | -34.95% | 1.229 | Current strict verified case |
| BTC + ETH | 57.74% | -34.69% | 1.250 | Counterfactual only |
| BTC + SOL | 63.06% | -34.23% | 1.324 | Counterfactual only |
| BTC + ETH + SOL | 64.66% | -33.98% | 1.346 | Counterfactual only |
| All spot | 65.37% | -33.72% | 1.355 | Theoretical zero-funding ceiling |

The economic priority is therefore clear: **SOL identity and executable spot routing matter much more than ETH** for this frozen BRRK history.

## Funding attribution context

Native Hyperliquid additive funding contribution over the same common window was approximately:

- BTC: **-25.19%**
- SOL: **-13.40%**
- ETH: **-3.05%**
- BNB: **-1.33%**
- XRP: **0.00%**

This explains why BTC spot treatment produces the first large recovery and why a valid SOL spot implementation is the next highest-value router question.

## Decision

1. The all-perp implementation remains rejected as the default architecture.
2. BTC-only strict spot routing materially improves funding economics and is the correct first shadow implementation candidate.
3. `56.20%` is **not yet a deployable net CAGR** because historical spot fees, basis, spread and slippage are not included.
4. UETH and USOL must not be silently upgraded from candidate-only status based on this PNL attribution.
5. The next research priority is a dedicated Unit identity/custody/withdrawal audit for UETH and USOL, followed by forward shadow execution evidence.
