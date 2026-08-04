# Crypto Regime/Rotation Research Roadmap — after PIT-ALPHA-0016

Date: 2026-08-04

This is a stopping-rule document, not a strategy. It limits degrees of freedom and prevents serial backtest optimization.

## Current canonical baseline

**BRRK-0011** = frozen fixed-V1 alpha + frozen PCA4 BRRK-0006 Risk-Off authority structure + corrected path-CDaR definition.

Common BRRK window 2022-12-10 through 2026-08-02:

- CAGR 65.10%;
- MDD -33.72%;
- Sharpe 1.353;
- Calmar 1.931.

No PIT module is promoted over BRRK-0011.

## Current evidence hierarchy

### Tier A — canonical portfolio baseline

- BRRK-0011.
- Calibration audits show no observed terminal-tail undercoverage and conservative path-drawdown forecasts.

### Tier B — validated mechanisms, rejected portfolio implementations

**PIT-DISP-0015**:

- broad historical dispersion contains real risk information;
- reduces MDD、CDaR、volatility and downside capture;
- lowers CAGR and upside capture;
- not promoted.

**PIT-ALPHA-0016 ranking**:

- beats 98/100 random-priority placebo seeds on terminal NAV and Calmar;
- diversified contribution, largest positive contributor share13.14%；
- includes152 currently inactive/non-TRADING historical candidates；
- cross-sectional trend ranking is validated.

**PIT-ALPHA-0016 portfolio**:

- CAGR12.25%；
- MDD-69.12%；
- turnover349.62；
- negative2025+ subperiod；
- nearly eliminated at20bps；
- rejected.

### Tier C — fixed-panel or event-concentrated diagnostics

- DISP-0014: selection-sensitive fixed-panel diagnostic.
- DISP-0013: event-concentrated alt-to-BTC diagnostic.

## Gate 1 — PIT-DISP-0015: resolved

Decision:

1. Broad risk mechanism survives dead-pool inclusion.
2. Growth/opportunity-cost trade-off fails promotion.
3. Fixed-panel0014 downgraded.
4. No tuning of0015.

## Gate 2 — PIT-ALPHA-0016: resolved

Frozen primary specification:

- historical ordinary Binance USDT universe;
- 240 consecutive completed daily observations;
- completed-day quote volume >=$25m;
- own trend>0 and relative trend>0;
- rank=`(0.5 own +0.5 relative)/rv30`;
- Top-2 primary;
- gross<=1;
- 50%BTC core/50%alt sleeve;
- universal35% alt cap;
- 0.05 band and5bps;
- 100 fixed-random-priority placebo seeds.

Decision:

1. Ranking mechanism is real and not explained by random eligibility selection.
2. Contribution is not dominated by one ex-post winner.
3. Daily broad-universe Top-2 portfolio fails risk, turnover, cost and persistence requirements.
4. BRRK-0011 remains baseline.
5. No0016 parameter may be tuned.
6. Any lower-turnover redesign requires a new experiment ID after attribution.

## Gate 3 — PIT-ALPHA attribution audit: current highest priority

No trading changes are allowed.

Required decomposition:

- daily/monthly eligible-universe churn;
- score/rank turnover;
- actual held-name turnover;
- holding-period and re-entry distributions;
- transaction cost by gross-beta change versus name replacement;
- contribution by asset、trade、listing cohort、liquidity cohort；
- worst tail-loss trades and drawdown episodes；
- rank persistence and post-entry decay；
- overlap with fixed V1 holdings；
- decomposition of2024 success and2025 failure；
- inactive-symbol selection and exit timing；
- capacity proxy using historical quote volume and target weights。

Primary question:

> Why does a rank that beats98% of placebos still generate only12.25%CAGR、-69%MDD and extreme turnover?

The audit must produce causal diagnostics, not an optimized threshold.

## Gate 4 — new low-turnover design, conditional on attribution

Only one structurally justified hypothesis should be registered first.

Potential hypotheses, not yet authorized experiments:

- monthly universe/rank refresh with daily BTC beta;
- persistence confirmation before new-name entry;
- hold-until-rank-exit rather than continuous Top-N replacement;
- separate universe refresh cadence from exposure cadence;
- uniform turnover budget/hysteresis;
- restrict name switching while preserving risk-off exit authority.

A broad parameter grid is prohibited. The next experiment must be selected from attribution evidence, not historical PNL.

## Gate 5 — dispersion signal-identity audit

Secondary no-trading-change audit:

- explain fixed/dynamic scale correlation0.064；
- universe breadth and concentration；
- volume-selection effects；
- sector/group and inactive-asset contribution；
- false-positive/false-negative risk episodes。

It cannot search for a formula that restores fixed-panel CAGR.

## Gate 6 — funding history and Spot/Perp Router

Required:

- accessible historical funding archive；
- spot/perp comparison for unchanged target exposure；
- separate funding、basis、fees and slippage；
- isolate gross>1 carry；
- report hedge/short and negative-funding-long cases separately。

This is an implementation module, not an alpha claim.

## Gate 7 — execution hardening

Hyperliquid testnet/shadow work should cover:

- metadata precision；
- target-notional L2 VWAP and Slippage-at-Risk；
- partial fills and reconciliation；
- order slicing；
- idempotency and audit logs；
- emergency reduce-only controls；
- endpoint authorization；
- deterministic parity with research targets。

## Gate 8 — risk allocation and leverage last

Do not add covariance、LPM、generic volatility gates or leverage to rescue0016.

Only after alpha economics、funding and execution are controlled may the project test:

- covariance/marginal risk contribution；
- downside/LPM estimators；
- normal beta cap around1.30；
- strong-trend hard maximum1.50。

## Explicitly stopped research lines

- manual bottom/recovery jumps；
- CUSUM threshold tuning；
- HMM factor/state selection by PNL；
- semantic-state anchoring；
- stacking generic volatility gates；
- tuning PIT-DISP-0015；
- tuning PIT-ALPHA-0016 Top-N、liquidity、age、rank weights、BTC core or caps；
- hard-coding HYPE or another current winner；
- combining modules to recover historical CAGR before attribution；
- deep RL before simple survivor-free economics work；
- leverage expansion before validation。

## Promotion philosophy

A module is promoted only when it satisfies:

**mechanism + preregistration + no-lookahead + realistic cost + subperiod persistence + model/universe uncertainty + implementation audit + controlled upside opportunity cost + acceptable turnover.**

Mechanism validation alone is not portfolio validation. Higher historical CAGR alone is insufficient.
