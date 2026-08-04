# Crypto Regime/Rotation Research Roadmap — after PIT-DISP-0015

Date: 2026-08-04

This roadmap is a stopping-rule document, not a strategy. Its purpose is to limit degrees of freedom and prevent serial backtest optimization.

## Current production-research baseline

**BRRK-0011** = frozen V1 alpha + frozen PCA4 BRRK-0006 Risk-Off authority structure + mathematically corrected path-CDaR definition.

Common-window baseline (2022-12-10 through 2026-08-02): CAGR 65.10%, MaxDD -33.72%, Sharpe 1.353, Calmar 1.931. No experimental overlay is promoted over BRRK-0011 yet.

## Evidence hierarchy

### Tier A — baseline / implementation corrections

- BRRK-0011: baseline.
- AUDIT-0010/0012: terminal-return scenario distribution is reasonably calibrated; maximum-drawdown scenarios are conservative on the 44 realized 20-day forecasts.
- No heavier tails or conformal safety buffer are justified by the observed calibration record.

### Tier B — strong shadow risk-overlay candidate

**DISP-0014** (external literature formula):
- scales total exposure to cash using 20-day cross-sectional dispersion versus its prior expanding median;
- fixed externally specified 0.10 floor and 0.80 recursive smoothing;
- fixed-panel BRRK result: CAGR 65.71%, MaxDD -30.60%, Sharpe 1.488, Calmar 2.147;
- interpretation: risk compression rather than alpha creation; gives up upside capture.

It is **not eligible for production promotion until PIT-DISP-0015 validates the signal on a dynamic, survivorship-aware universe**.

### Tier C — promising but weak/event-concentrated candidate

**DISP-0013** (extreme-dispersion alt-to-BTC reliability gate):
- fixed-panel BRRK result: CAGR 67.50%, MaxDD -33.72%, Calmar 2.002;
- only ~2% of days active;
- activation attribution shows ~97% of positive episode contribution came from the top three episodes, concentrated in late Nov / early Dec 2024.

Keep shadow-only. Do not select the 80% sensitivity or combine 0013 with 0014 on the same historical window.

## Gate 1 — PIT-DISP-0015 (highest priority)

Objective: validate the dispersion risk signal itself with a point-in-time, dead-pool-inclusive Binance USDT universe.

Frozen before first model run:
- historical ordinary spot-USDT candidates including later inactive/BREAK symbols;
- last 240 calendar daily rows must be complete;
- completed-day quote volume >= $25m;
- minimum cross-section 5;
- dispersion = cross-sectional sample std of trailing 20-day cumulative log return;
- prior expanding-median target;
- exposure floor 0.10;
- recursive smoothing lambda 0.80;
- entire V1 exposure scaled to cash;
- 0.05 L1 band and 5bps transaction cost;
- signal at t held over t+1.

Decision:
1. Compare dynamic-universe overlay against BRRK-0011 baseline.
2. Compare it against fixed-panel DISP-0014.
3. No parameter may be changed after the first valid model report.
4. If dynamic-universe risk-adjusted improvement largely disappears, downgrade DISP-0014 and treat the fixed-panel result as potentially selection-driven.
5. If it survives with materially better drawdown/Sharpe/Calmar and reasonable activation behavior, DISP-0014/0015 becomes eligible for prospective shadow promotion.

## Gate 2 — dynamic alpha universe

Only after Gate 1 is resolved.

Purpose: remove the remaining fixed-winner bias from the **alpha** engine, not merely the dispersion-risk signal.

Rules must be registered before PnL:
- point-in-time eligible universe from historical daily rows;
- dead/delisted coins remain historically eligible until data/trading availability ends;
- liquidity and age screens must use only lagged/completed information;
- no present-day market-cap or survival filter;
- avoid PnL-driven top-N selection: either use an externally specified N or report a small preregistered family in full;
- include a random-ranking / placebo benchmark so a ranking model must beat noise, not merely cash/BTC.

Primary question: does the V1 relative-strength/trend mechanism still select durable winners when today's surviving majors are not hard-coded?

## Gate 3 — downside-risk estimator (LPM)

Only after the universe problem is controlled.

Motivation: 2026 crypto portfolio evidence supports lower-partial-moment risk objectives under heavy tails and downside asymmetry. Existing PIT audit shows terminal returns are already reasonably calibrated while path drawdown is conservative, so this should be a **risk-estimator replacement test**, not an additional safety gate.

Preferred first experiment:
- preserve V1 alpha and the accepted regime gate;
- replace symmetric/path-risk penalty with a fixed lower-partial-moment objective;
- do not use Sortino cross-validation or broad parameter search in the first experiment;
- report downside capture, expected shortfall, CDaR, turnover, upside capture and calibration, not CAGR alone.

## Gate 4 — derivatives / execution state

Can develop in parallel because it does not need to change alpha.

Prospective Hyperliquid data already includes/should include:
- L2 book depth and target-notional VWAP;
- spread and directional slippage;
- funding;
- mark/oracle premium;
- open interest and volume;
- fill/reconciliation data once shadow execution begins.

Use cases:
- execution veto/slicing based on current target-notional liquidity;
- empirical Slippage-at-Risk / expected tail slippage;
- funding cost control for exposure above 1.0;
- liquidity-state monitoring.

Do **not** use one snapshot to choose thresholds. Recent 2026 microstructure evidence favors a state-first L2 design and shows event/cascade early-warning variables are not universal.

## Explicitly stopped research lines

- manual 'last drop / bottom' recovery jumps;
- CUSUM re-entry threshold tuning on the same sample;
- HMM state-count/factor-count selection by realized PnL;
- persistent semantic-state anchoring;
- adding more generic volatility gates to V1;
- combining DISP-0013 and DISP-0014 before independent PIT validation;
- deep-RL portfolio optimization before simple, survivor-free baselines are beaten.

## Promotion philosophy

A new module is promoted only when it satisfies **mechanism + pre-registration + no-lookahead + transaction costs + subperiod robustness + model/universe uncertainty + implementation audit**. A higher historical CAGR alone is insufficient.
