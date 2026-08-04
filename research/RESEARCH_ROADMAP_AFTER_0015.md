# Crypto Regime/Rotation Research Roadmap — after PIT-DISP-0015

Date: 2026-08-04

This is a stopping-rule document, not a strategy. Its purpose is to limit degrees of freedom and prevent serial backtest optimization.

## Current baseline

**BRRK-0011** = frozen V1 alpha + frozen PCA4 BRRK-0006 Risk-Off authority structure + mathematically corrected path-CDaR definition.

Common window 2022-12-10 through 2026-08-02: CAGR 65.10%, MaxDD -33.72%, Sharpe 1.353, Calmar 1.931.

No experimental overlay is promoted over BRRK-0011.

## Evidence hierarchy after PIT-DISP-0015

### Tier A — canonical baseline

- **BRRK-0011** remains baseline.
- AUDIT-0010/0012: terminal-return scenarios are reasonably calibrated; maximum-drawdown scenarios are conservative on the available 44 realized forecasts.
- No heavier tail or conformal safety buffer is justified by the observed calibration record.

### Tier B — valid risk mechanism, not promoted

**PIT-DISP-0015**:

- true point-in-time, dead-pool-inclusive historical Binance USDT universe;
- 652 candidates, 646 with rows, zero fetch errors;
- 159 currently inactive/non-TRADING symbols historically eligible;
- dynamic broad-market dispersion improves BRRK MDD, CDaR, volatility, downside capture, Sharpe and Calmar;
- but reduces CAGR from 65.10% to 60.81% and upside capture from 105.02% to 95.92%;
- status: broad-market risk diagnostic / shadow overlay only.

### Tier C — selection-sensitive fixed-panel diagnostic

**DISP-0014**:

- fixed-panel BRRK result remains historically strong: CAGR 65.71%, MaxDD -30.60%, Sharpe 1.488, Calmar 2.147;
- however fixed-panel and dynamic PIT scales correlate only about 0.064;
- the fixed BTC/ETH/SOL/BNB/XRP panel is not a reliable proxy for broad historical dispersion;
- status: downgraded, not production eligible.

### Tier D — event-concentrated diagnostic

**DISP-0013**:

- fixed-panel BRRK CAGR around 67.50%, Calmar around 2.00;
- only about2% of days active;
- about97% of positive episode contribution came from the top three episodes, concentrated in late Nov/early Dec 2024;
- status: shadow only.

## Gate 1 — PIT-DISP-0015: resolved

Frozen rules were executed without post-result change:

- historical ordinary spot-USDT candidates including later inactive/BREAK symbols;
- 240 consecutive completed daily observations;
- completed-day quote volume >= $25m;
- minimum cross-section 5;
- 20-day cumulative-log-return cross-sectional dispersion;
- prior expanding-median target;
- exposure floor 0.10;
- smoothing lambda 0.80;
- entire V1 exposure scaled to cash;
- 0.05 L1 band, 5bps cost, t signal held over t+1.

Decision:

1. Broad dispersion risk compression survives dead-pool inclusion.
2. The growth/risk trade-off is insufficient for production promotion.
3. Fixed-panel DISP-0014 is materially selection-sensitive and downgraded.
4. No PIT-0015 parameter may be tuned on this window.
5. Exact daily outputs are now persisted under `research/results/pit_disp_0015/`.

## Gate 2 — dynamic point-in-time alpha universe: current highest priority

Purpose: remove the remaining fixed-winner bias from the **alpha engine**.

The first test must be registered before PnL and use:

- historical daily rows to determine point-in-time existence;
- later dead/delisted coins retained until data/trading availability ends;
- lagged/completed liquidity and age screens;
- no present-day market cap, rank or survival filters;
- own absolute trend >0 before relative-strength ranking;
- BTC regime as risk-on/risk-off authority;
- gross <=1 in the primary run;
- explicit transaction costs, rebalance band and t→t+1 execution;
- full preregistered Top-N family rather than selecting the best N;
- random-ranking placebo and equal-weight eligible-universe benchmarks;
- contribution concentration and inactive-asset attribution.

Primary question:

> Does V1 own-trend + relative-strength still select durable winners when today's surviving majors are not hard-coded?

Promotion requires:

- meaningful outperformance over placebo;
- no dependence on one ex-post winner;
- reasonable 2024+ and 2025+ behavior;
- survival after dead-pool inclusion and realistic costs;
- no post-result movement of age, liquidity or Top-N rules.

## Gate 2A — dispersion signal-identity audit

No trading changes. Run in parallel with dynamic-alpha engineering.

Explain fixed vs dynamic scale divergence through:

- universe size and breadth;
- top-contributor concentration;
- volume-selection effects;
- BTC inclusion/exclusion;
- sector/group contributions;
- inactive-symbol contribution;
- high-dispersion episode overlap;
- fixed-panel false-positive and false-negative risk reductions.

This audit may explain signal identity but may not search for a formula that restores fixed-panel PnL.

## Gate 3 — funding history and Spot/Perp Router

Can proceed after or alongside Gate2 data engineering, but cannot become an alpha claim.

Required:

- accessible historical funding archive;
- spot/perp implementation comparison for unchanged target exposure;
- funding, basis, fees and slippage attributed separately;
- leverage-overlay carry isolated from base gross<=1 exposure;
- hedge and negative-funding-long cases reported separately.

## Gate 4 — downside-risk estimator / risk allocation

Only after dynamic alpha is controlled.

Candidate first experiment:

- preserve accepted alpha and regime gate;
- replace, not stack, the risk estimator with a fixed lower-partial-moment objective;
- no broad hyperparameter search;
- report downside capture, expected shortfall, CDaR, turnover, upside opportunity cost and calibration.

PIT-0015 demonstrates why upside opportunity cost must be a first-class risk metric.

## Gate 5 — execution hardening

Prospective Hyperliquid data and engineering should cover:

- L2 book depth and target-notional VWAP;
- spread and directional slippage;
- funding, premium, open interest and volume;
- partial fills and reconciliation;
- idempotency and audit logs;
- emergency reduce-only controls;
- testnet end-to-end parity with research targets.

One snapshot cannot define execution thresholds.

## Explicitly stopped research lines

- manual last-drop/bottom recovery jumps;
- CUSUM threshold tuning on the same sample;
- HMM state/factor selection by realized PnL;
- persistent semantic-state anchoring;
- generic volatility gates stacked on V1;
- tuning PIT-DISP-0015 after its valid result;
- combining dispersion variants to recover historical CAGR;
- hard-coding HYPE or another current winner before dynamic-alpha testing;
- deep RL before simple survivor-free baselines are beaten;
- leverage expansion before universe, funding and execution validation.

## Promotion philosophy

A module is promoted only when it satisfies:

**mechanism + preregistration + no-lookahead + transaction costs + subperiod robustness + model/universe uncertainty + implementation audit + controlled upside opportunity cost.**

Higher historical CAGR alone is insufficient.
