# BRRK-CRYPTO-MULTI-HORIZON-TREND-0074 — DESIGN

Status: STAGE 2 / PROSPECTIVE DESIGN

## Research question

Can a deliberately simple BTC/ETH/SOL multi-horizon directional trend benchmark produce robust positive net economic value after lagged volatility targeting, bounded exposure, realistic and stressed costs, and preregistered drawdown/tail/turnover/concentration/robustness tests?

0074 is a benchmark study, not a model-complexity search. A positive result must come from simple auditable trend persistence rather than window mining, model selection, or final-period Sharpe maximization.

## Immutable lineage

- Program roadmap: `research/governance/CRYPTO_MULTI_STRATEGY_RESEARCH_PROGRAM_0071_0082.md`.
- 0073 immutable closeout merge: `da62a1ef2258eb27f5a4cede2415c567f19d3e76`.
- 0074 OWNER-FIRST merge: `2af445a26e2a1d08b38a1cc9f6c853b29c828cde`.
- Initial universe remains exactly BTC, ETH and SOL.
- Evidence remains DEVELOPMENT history, never independent OOS by description alone.

No 0070/0071/0072/0073 observed result may be used to choose a 0074 signal formula, horizon, cost, volatility target, cap, threshold, source, or terminal gate.

## Candidate-family ceiling

Exactly three selectable trend families are allowed. No fourth family may be introduced under this ID.

1. `PAST_RETURN_SIGN_TREND`
   - Uses only lagged cumulative return information over the prospectively frozen fast/medium/slow horizon family.
   - Direction is determined by the frozen sign/aggregation rule.

2. `MOVING_AVERAGE_SPREAD_TREND`
   - Uses only lagged price moving-average relationships over prospectively frozen fast/medium/slow settings.
   - No adaptive smoothing or final-history optimized weighting is allowed.

3. `BREAKOUT_TREND_NORMALIZED_BY_LAGGED_VOL_OR_ATR`
   - Uses only lagged breakout state and the prospectively frozen volatility/ATR normalization.
   - No breakout threshold search after historical exposure is allowed.

Each candidate must use the same eligible asset set, chronology, cost framework, portfolio accounting, volatility-targeting framework and robustness suite. Candidate accounting remains exactly three even if one candidate later has insufficient support.

## Horizon-family design

The economic horizon family is exactly `FAST / MEDIUM / SLOW`.

Stage 3 PREREGISTRATION must freeze one exact lookback definition for each horizon family and the exact within-candidate horizon-combination rule before any controlled historical content read. The rule must be deterministic and cannot use observed final performance for weighting.

Dozens of adjacent lookbacks, rolling window searches, or post-result horizon replacement are forbidden.

## Direction and exposure domain

- Trend exposures are signed directional exposures: long, flat, or short are permitted only through the exact instrument/accounting implementation prospectively frozen in Stage 3.
- Gross exposure is bounded by an absolute cap frozen in Stage 3; unbounded leverage is forbidden.
- Volatility targeting uses lagged information only and cannot use same-bar realized return information to size that same bar.
- The executable exposure formed at decision time `t` may first affect return from the next prospectively frozen execution interval.
- If a short implementation requires derivative funding, borrow, or other holding costs, those costs must be included in the frozen economic accounting. They may not be omitted because they are inconvenient or adverse.

## Point-in-time and anti-lookahead contract

For every asset and every timestamp:

1. asset eligibility must be known at decision time;
2. signal inputs must be timestamped and available before the decision cutoff;
3. horizon calculations use only observations strictly available under the frozen chronology;
4. volatility/ATR estimators are lagged;
5. exposure is formed after signal and risk-state availability;
6. turnover is computed from executable prior exposure to new executable exposure;
7. costs are applied before portfolio NAV update under the frozen accounting order;
8. no later delisting, venue survival, future liquidity, revised metadata, or future return may change historical eligibility or signal state.

## Ordered economic calculation

Stage 3 must bind exact formulas while preserving this order:

1. validate exact source/data identities and point-in-time eligibility;
2. construct lagged fast/medium/slow trend inputs;
3. form each of the exactly three candidate signals under its frozen rule;
4. combine horizon information using the prospectively frozen non-performance-weighted rule;
5. estimate lagged realized volatility or ATR where required;
6. apply volatility target and absolute exposure cap;
7. apply executable timing and rebalance cadence;
8. compute turnover from prior executable exposure;
9. apply `C0` theoretical, `C1` realistic and `C2` stressed costs under exact frozen numerical assumptions;
10. compute per-asset and portfolio returns/NAV;
11. compute return, CAGR/annualized return, volatility, Sharpe, Sortino, MDD, Calmar, tail-loss, turnover, cost-drag, gross/net exposure and concentration metrics;
12. evaluate whipsaw, trend-crash, gap and high-volatility stress behavior under prospectively frozen definitions;
13. evaluate fast/medium/slow neighborhood robustness without replacing the primary frozen settings;
14. perform leave-one-asset and leave-one-regime-out diagnostics where support permits;
15. apply frozen bootstrap/DSR/PBO and trial accounting where mathematically admissible;
16. persist every candidate and terminal gate, not only the representative candidate;
17. classify `PASS`, `FAIL`, `INCONCLUSIVE_INSUFFICIENT_SUPPORT`, or `INVALID_EXECUTION` under frozen rules.

Raw Sharpe alone can never establish PASS.

## Cost and implementation families

Stage 3 must freeze exact numerical values and accounting for:

- entry/exit and rebalance fees;
- bid/ask spread and slippage;
- derivative funding or borrow cost if required by the chosen short implementation;
- rebalance cadence;
- volatility-target turnover interaction;
- stressed cost multipliers or equivalent C2 stress;
- missing-price, stale-price, gap and instrument-unavailable handling.

`C0` may be reported but cannot by itself satisfy PASS.

## Robustness, concentration and capacity families

The preregistered suite must include, where mathematically supported:

- candidate/trial accounting exactly equal to the complete tested set;
- serial-dependence-aware bootstrap or lower-confidence-bound analysis;
- Deflated Sharpe Ratio using the declared trial count;
- CSCV/PBO if the candidate-return matrix is sufficient;
- horizon-neighborhood stability;
- leave-one-asset robustness;
- leave-one-regime robustness;
- whipsaw and trend-crash stress;
- gap/high-volatility stress;
- contribution concentration by asset and period;
- turnover and conservative implementation-capacity diagnostics.

Exact block lengths, replicate counts, seeds, thresholds and terminal gates belong only to Stage 3 PREREGISTRATION.

## Data-readiness requirement before irreversible execution

0074 must not repeat the execution-readiness failure mode where identities exist but decision-critical payloads are not actually staged for the controlled attempt.

Before Stage 7 can PASS, the controlled boundary must prove, without opening scientific values, that every Stage-8-authorized payload required by the frozen candidate set is durably staged, hash-bound, nonexpired where applicable, and offline-readable under the Stage-8 zero-source-network-fetch budget. Identity-only existence without staged controlled payload availability is insufficient for Stage-8 readiness.

Stage 7 itself remains zero-result and may inspect only identity, metadata, durability and execution-plane absence. Stage 8 still requires durable remote `RUN_ATTEMPT.marker` before the first controlled content read.

## Terminal meaning

- `PASS`: valid exactly-once execution and at least one of the three preregistered candidates passes every required net economic, C1/C2, risk, turnover, concentration and statistical robustness gate.
- `FAIL`: valid execution with sufficient support, but no candidate passes all frozen gates.
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`: a prospectively defined support or mathematical sufficiency condition prevents a decision.
- `INVALID_EXECUTION`: identity, chronology, lookahead, read-budget, candidate-count, accounting, persistence or exactly-once drift invalidates the attempt.

No outcome grants production, signature, or order-submission authority.

## Stage-2 execution accounting

- controlled scientific/history reads: `0`;
- scientific engine calls: `0`;
- scientific source-network fetches: `0`;
- controlled attempt: `0/1`;
- production authorization: `false`;
- signature authorization: `false`;
- order-submission authorization: `false`.

## Exact next stage

Only after this DESIGN merges may Stage 3 PREREGISTRATION freeze the exact data/source identities, signal formulas, fast/medium/slow lookbacks, horizon aggregation, instrument implementation, volatility target, exposure cap, rebalance timing, costs, stress magnitudes, support minima, bootstrap/DSR/PBO settings, seeds, candidate gates and terminal numerical thresholds. No controlled 0074 scientific/history content may be read in Stage 2 or Stage 3.
