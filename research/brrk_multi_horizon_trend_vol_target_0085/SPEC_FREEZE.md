# BRRK Multi-Horizon Trend Vol-Target 0085 — SPEC_FREEZE

Research ID: `BRRK-MULTI-HORIZON-TREND-VOL-TARGET-0085`

Lifecycle: `PROSPECTIVE_FIVE_GATE_LIFECYCLE_V1`

Registry representation: `governance_mode=PROGRAM_GOVERNED_V1`; explicit five-gate adoption is governed by this SPEC_FREEZE and the merged prospective lifecycle contract. This is a schema-compatibility representation only and does not change the frozen science.

Gate: `SPEC_FREEZE` = OWNER-FIRST + DESIGN + PREREGISTRATION

Status: `FROZEN_NOT_BUILT_NOT_RUN`

## OWNER-FIRST

### Question

Does one simple, preregistered BTC/ETH/SOL multi-horizon long/cash trend sleeve with volatility targeting produce robust positive standalone economic value after realistic and stressed costs on the frozen DEVELOPMENT history, without leverage, shorting, result-informed parameter search, or post-result rescue?

### Why this study exists

The prior 0074 trend line ended `INVALID_EXECUTION`, so it did not answer the scientific question. 0085 is a new prospective study under the newly merged common runner and five-gate lifecycle. It does not reuse 0074 lifecycle credit, attempt budget, result, or execution state.

### Economic mechanism

Crypto trend persistence may arise from slow capital flows, reflexive momentum and delayed positioning adjustment. A long/cash sleeve may participate when medium/long trend is positive and move toward cash when trend breaks. Volatility targeting is intended only to normalize risk across assets and time, not to create leverage.

## DESIGN

### Universe

Exactly:

- BTC
- ETH
- SOL

No BNB, XRP, additional assets, cross-sectional selection, shorting or options.

### Decision frequency and timing

- Daily UTC decisions.
- Signal at close of session `t` may affect returns only from `t` to `t+1` onward.
- No intraday information.
- No lookahead, centered windows or future-filled missing observations.

### Candidate budget

Exactly **one** scientific candidate. No grid, parameter sweep, winner selection or alternate horizon family is permitted under 0085.

### Frozen signal

For each asset at decision session `t`, compute trailing simple log-return signs over exactly:

- 20 sessions
- 60 sessions
- 120 sessions
- 240 sessions

Each horizon contributes `1` when its trailing log return is strictly positive and `0` otherwise. The asset is trend-active only when at least **3 of 4** horizons are positive.

No magnitude weighting, threshold optimization, moving-average substitution, breakout substitution or asset-specific horizon change is permitted.

### Frozen volatility estimate

For each asset, use the trailing **20-session realized volatility** of daily log returns, annualized by `sqrt(365)`, using only observations available at decision time `t`.

A row requires all four trend horizons and the 20-session volatility estimate to be defined. Non-finite or non-positive volatility fails that asset row closed to zero target weight.

### Frozen portfolio construction

1. For every trend-active asset, set raw risk weight to `1 / vol20`.
2. Normalize active raw risk weights to sum to 1.0. If no asset is active, risky gross is 0 and cash is 1.
3. Compute trailing portfolio volatility from the same available information and scale risky gross toward an annualized portfolio volatility target of exactly **25%**.
4. Gross exposure is capped at exactly **1.0** and floored at 0.0. No leverage is allowed.
5. Unused weight remains cash.
6. Rebalance at the next-session boundary using the frozen target.

Implementation must define the portfolio-volatility calculation mechanically before any controlled history read. If a purely mechanical ambiguity is discovered during BUILD, the fix must choose one deterministic interpretation without inspecting controlled values and must be documented as an implementation clarification, not a new scientific parameter.

### Costs

One-way turnover cost panels:

- primary: 10 bps
- stress: 20 bps
- severe stress: 30 bps

Costs apply to absolute portfolio weight turnover at each rebalance. No funding or borrow cost applies because the candidate is long/cash with gross <= 1.0. Cash accrual must use the already-governed frozen cash-rate mechanism if available under the controlled manifest; otherwise cash return is fixed to zero and this fact must be bound before RUN.

### Benchmarks

Report, on the exact same support:

1. equal-weight BTC/ETH/SOL buy-and-hold;
2. BTC buy-and-hold;
3. canonical BRRK target/equity reference where a frozen exact identity is available without source substitution.

The candidate does not need to beat every benchmark in CAGR to qualify as a distinct sleeve. Benchmark comparisons are diagnostics plus the explicit gates below.

## PREREGISTRATION

### Evidence tier

`RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS`.

0085 may answer whether the fixed trend sleeve is supported on the governed development history. It cannot establish independent OOS validity or production authority. A later forward-only validation must be separately frozen.

### Controlled-source boundary

SPEC_FREEZE reads no controlled scientific payload values. ARM must bind exact artifact/blob identities and read budgets before RUN. No source substitution is allowed after ARM.

The existing governance-visible historical identities may be referenced by identity only. Payload reads must occur only in RUN through a currently qualified `CONTROLLED_RESEARCH_RUNNER_V1`, after durable `RUN_ATTEMPT.marker`.

### Primary metrics

At each cost panel report:

- CAGR
- annualized volatility
- Sharpe, with the frozen cash rule as risk-free reference when available and otherwise zero
- maximum drawdown
- Calmar
- terminal wealth multiple
- average risky gross exposure
- annualized turnover
- cost drag
- percentage of sessions with zero risky gross
- asset-level average exposure

### Robustness diagnostics

Using the primary 10 bps path:

- split the eligible history into exactly four contiguous, near-equal chronological blocks and report each block CAGR;
- report the worst block CAGR;
- report monthly-return concentration as the share of total positive log growth contributed by the best five calendar months, when total positive log growth is positive;
- report candidate return correlation with canonical BRRK where common support exists;
- report candidate return correlation with equal-weight BTC/ETH/SOL buy-and-hold.

No resampling or multiple-testing correction is required because 0085 has exactly one frozen candidate and no model selection. If a later study introduces variants, it requires a new research ID and its own multiplicity control.

### Frozen PASS gates

0085 classifies `PASS_TREND_SLEEVE_DEVELOPMENT_SUPPORT` only if all of the following hold on valid common support:

1. execution is valid under the qualified common runner;
2. minimum eligible support is **730 daily sessions**;
3. primary 10 bps CAGR is strictly positive;
4. primary 10 bps Sharpe is at least **0.80**;
5. primary 10 bps Calmar is at least **1.00**;
6. primary maximum drawdown magnitude is at most **35%**;
7. 20 bps stress Sharpe is at least **0.65**;
8. 30 bps severe-stress CAGR remains strictly positive;
9. at least **3 of 4** chronological blocks have strictly positive CAGR;
10. candidate terminal wealth at 10 bps is at least **85%** of equal-weight BTC/ETH/SOL buy-and-hold terminal wealth on the same support;
11. candidate maximum drawdown magnitude at 10 bps is at least **5 percentage points smaller** than equal-weight BTC/ETH/SOL buy-and-hold, unless the benchmark maximum drawdown magnitude itself is below 20%, in which case this gate becomes candidate MDD <= benchmark MDD;
12. gross exposure never exceeds 1.0 and no short exposure occurs;
13. no controlled source is read more than its ARM-bound budget, scientific engine invocation count is exactly 1, and scientific source-network fetches are 0.

### Terminal classifications

Exactly one:

- `PASS_TREND_SLEEVE_DEVELOPMENT_SUPPORT`
- `FAIL_NO_ROBUST_TREND_SLEEVE_VALUE`
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`
- `INVALID_EXECUTION`

`INCONCLUSIVE_INSUFFICIENT_SUPPORT` is allowed only when execution is valid but the frozen minimum support or a required benchmark/common-support measurement cannot be formed from the ARM-bound sources. It cannot be used to hide a failed economic gate.

### Attempt and follow-up rules

- Stage-equivalent RUN attempt budget: exactly `1/1`.
- No controlled payload read before durable marker.
- Scientific engine: exactly `1/1`.
- Scientific source-network fetches: `0`.
- Same-ID rerun, retune, rescue, horizon change, threshold change, volatility-target change, cost-panel change, universe change, benchmark substitution or history extension after attempt consumption is forbidden.
- PASS may qualify a Trend sleeve for later independent forward validation and multi-sleeve consideration only. It grants no production authority.
- FAIL closes this exact trend hypothesis. A materially new trend mechanism requires a new research ID.
- INVALID_EXECUTION caused by the common runner stops new scientific attempts until runner repair and requalification; it does not authorize a replacement-ID retry chain.

## Production boundary

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`
