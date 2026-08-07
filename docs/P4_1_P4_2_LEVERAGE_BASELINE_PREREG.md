# P4.1 / P4.2 — Corrected 0–1 Baseline Freeze + LEVERAGE-0039 Preregistration

Date: 2026-08-07

Status: **BASELINE FROZEN / LEVERAGE STUDY PREREGISTERED / NO LEVERAGE SEARCH RUN**

## Scope

This change implements only the first two P4 governance dependencies from the canonical roadmap:

1. **P4.1 Preserve current 0–1 scaler**;
2. **P4.2 Preregister leverage study**.

It does **not** run a leverage search, change runtime target gross, authorize gross above 1, select an operating drawdown budget or authorize production.

## P4.1 frozen baseline

Machine-readable freeze:

`research/leverage_0039/P4_1_BASELINE_FREEZE.json`

Freeze ID:

`P4.1-BRRK0011-CORRECTED-0-1-V1`

The baseline is the current F13-corrected BRRK-0011 0–1 risk chain. Research authority is pinned to:

- `research/risk_metric_fix/corrected_risk.py`;
- the frozen regime/model configuration at `research/regime_kelly/config.py`;
- the product-owned P3.2 reproduction at `execution/plan-b-bot/beta_bot/target_math.py`;
- `research/results/BRRK_0011_CDAR_CORRECTION_2026-08-04.md`.

The corrected research selector evaluates path terminal CVaR95 and path CDaR95, where drawdown begins from decision-time wealth = 1, and selects scale only inside `[0, 1]` under the frozen 20% scenario tail-risk budget.

Frozen product/research parameters include:

- four target assets: BTC / ETH / SOL / BNB;
- XRP feature-only;
- 4 semantic regimes;
- 20-day forecast horizon;
- 600 minimum training days;
- 30-day refit interval;
- 5,000 scenarios;
- Student-t df = 5;
- frozen scenario CVaR/CDaR budget = 20%;
- current production gross cap = 1.0;
- operating risk budget remains **unfrozen**;
- catastrophic drawdown limit remains 70% and is **not** an operating target.

Historical corrected BRRK-0011 result reference, 2022-12-10 through 2026-08-02:

| Metric | Corrected BRRK-0011 |
|---|---:|
| CAGR | 65.104% |
| Max drawdown | -33.715% |
| Sharpe | 1.3532 |
| Calmar | 1.9310 |
| Realized path CDaR95 | 31.781% |
| Average gross | 0.75430 |

F27 R2 separately reports a calendar-span raw CAGR of `65.16609785339962%`. That is a different measurement/provenance convention and is preserved separately rather than silently reconciled with the 65.104% correction-result CAGR.

Historical result artifacts are not overwritten.

## Historical research-cap hint

`research/regime_kelly/config.py` contains:

```text
gross_cap          = 1.0
research_gross_cap = 1.30
```

Repository code search found no current consumer of `research_gross_cap`. P4 therefore treats 1.30 only as a historical **research-only ceiling hint**, not as evidence or authorization.

`LEVERAGE-0039` deliberately stops at 1.30. Studying a larger cap requires a new experiment ID and a new preregistration before execution.

## P4.2 preregistration

Machine-readable preregistration:

`research/leverage_0039/LEVERAGE-0039.json`

Status:

`PREREGISTERED_BEFORE_FIRST_RUN`

No leverage-search result exists in this PR.

### Only structural change

The first P4 study may change one thing only:

> generalize the **upper bound** of the same corrected CVaR/CDaR scale selector from 1.0 to a preregistered research cap.

Candidate caps:

```text
1.00, 1.10, 1.20, 1.30
```

The `1.00` candidate is a mandatory parity gate. If a generalized runner cannot reproduce the frozen <=1 baseline at cap 1.00, every >1 result is invalid.

The study may not change:

- V1 relative weights;
- HMM/regime features or semantic states;
- return-distribution model;
- Student-t family/df;
- scenario tail-risk budget;
- risk-off posterior logic;
- P3.3 rebalance semantics;
- P3.4 contribution semantics;
- asset universe;
- short policy.

## Operating risk budgets

Candidate operating maximum-drawdown budgets are preregistered as:

```text
35%, 40%, 45%, 50%
```

The lowest candidate is just above the corrected historical baseline MDD of 33.715%. The highest candidate remains materially below the 70% catastrophic termination boundary.

None of these values is a drawdown target. They are constraint candidates only.

The scenario CVaR95/CDaR95 budget remains frozen at **20%** in this experiment.

## Cost treatment

### Turnover / fee / slippage sensitivity

The preregistered matched-cost grid reuses the already-audited robustness levels:

```text
5, 10, 20, 50 bps per absolute weight change
```

- 5 bps = frozen historical continuity;
- 10 bps = mandatory primary robustness case;
- 20 bps = mandatory adverse implementation-cost case;
- 50 bps = extreme diagnostic stress.

Candidate and <=1 baseline always use the same cost assumption.

### Funding

Funding is **cost only**, never a signal or threshold.

Mandatory panels include:

1. Hyperliquid native all-perp common window, 2023-06-18 through 2026-07-31;
2. Binance full-history proxy, 2022-12-10 through 2026-07-31, used only as a sign/regime stress proxy and never as a Hyperliquid funding-level estimate.

The accounting method follows `FUNDING-PNL-0003` frozen-holdings attribution. `ROUTER-PNL-0005` strict verified-spot accounting may be reported diagnostically, but its zero-funding spot treatment is not deployable net PnL because historical spot fee/basis/slippage evidence is incomplete.

Missing native funding cannot be filled with zero or silently replaced with Binance levels.

F23 remains separate: no funding-aware position filter or funding threshold is permitted in `LEVERAGE-0039`.

## Historical stress suite

Preregistered windows:

- 2021-05-01 to 2021-07-31 — spring crash;
- 2021-11-01 to 2022-03-31 — November/bear transition;
- 2022-05-01 to 2022-12-31 — severe drawdown;
- 2024-03-01 to 2024-05-15 — exact prior AUDIT-0025 April masking window;
- calendar 2025 — full multi-peak/deleveraging year, with the three largest non-overlapping baseline drawdowns reported mechanically;
- 2026-01-01 to 2026-08-02 — recent frozen-end window.

Where full BRRK is not legally eligible under its frozen minimum-training rule, 2021/early-2022 evaluation is explicitly a conservative **pre-BRRK stress proxy**, not full-BRRK OOS performance.

## Synthetic stress suite

Mandatory one-day uniform target-asset gaps:

```text
-10%, -20%, -30%, -40%, -50%
```

Also required:

- ALT_CRASH: BTC -25%, ETH -35%, SOL -50%, BNB -40%;
- BTC_LED_CRASH: BTC -40%, ETH -25%, SOL -30%, BNB -25%;
- 1.5x / 2x / 3x volatility multipliers on worst realized 20-day blocks.

No favorable same-day rebalance is assumed inside a one-day gap.

## Liquidation-distance gate

Promotion requires a venue-specific liquidation-distance model based on a snapshotted/hash-pinned Hyperliquid margin/leverage-tier input before the first leverage-search run.

If that model/evidence is missing, promotion fails closed.

Every mandatory historical and synthetic stress must avoid modeled liquidation, and the reported minimum adverse-move distance to liquidation must exceed the largest applicable preregistered one-day gap stress for that position mix.

Research survival is not production authorization.

## Robustness gate

Preregistered start dates:

```text
2022-12-10
2023-03-01
2023-06-01
2024-01-01
```

Stationary block bootstrap:

```text
mean blocks: 7d / 21d / 63d
resamples: 10,000
```

Required thresholds:

- terminal outperformance probability >= 80% for every block length;
- 5% annualized return-difference quantile >= -1.0 pp;
- no registered start-date CAGR underperformance worse than -2.0 pp.

## Promotion / failure

A >1 candidate can advance only if all preregistered gates pass, including:

- cap=1 exact baseline parity;
- higher matched-cost compounded wealth at both 5 and 10 bps;
- not dominated by <=1 baseline at 20 bps;
- selected operating MDD budget respected;
- 70% catastrophe boundary respected;
- corrected scenario CVaR95/CDaR95 <=20% at every leverage decision;
- all historical/synthetic stress gates pass;
- liquidation-distance gate passes;
- robustness gates pass;
- Hyperliquid native funding economics are reported;
- no new alpha / F23 / 0038 / short / XRP / P5 logic.

Failure of any hard gate preserves the <=1 baseline.

## Deployment cap remains separate

Even if research selects a cap above 1, live deployment is not authorized by this experiment.

If a research cap is later promoted, the deployment cap must be the **next lower preregistered cap grid point**, never above 1.20 under `LEVERAGE-0039`, and must receive a separately versioned decision and production authorization.

Examples:

- research 1.10 -> deployment cap remains 1.00;
- research 1.20 -> deployment candidate cap at most 1.10;
- research 1.30 -> deployment candidate cap at most 1.20.

## Explicit exclusions

This PR and experiment do not authorize:

- running the leverage study before preregistration is merged;
- gross search above 1.30;
- production gross above 1.0;
- P3.2/P3.3/P3.4 changes;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response logic;
- shorts or XRP target exposure;
- P5 exit intelligence;
- historical-result overwrite;
- production trading authorization.

`production_authorized_components` remains empty.
