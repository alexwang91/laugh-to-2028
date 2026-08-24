# 0076 Stage2 DESIGN — single prospective cross-sectional momentum long/short baseline

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-LS-0076`

Status: `DESIGN_FROZEN_ROUTE_SELECTION / ZERO_CONTROLLED_HISTORY`

## 1. Upstream state and route choice

0084 is immutable `INVALID_EXECUTION` and produced no admissible scientific factor result. 0076 inherits exactly zero validated factors and zero lifecycle credit.

Under merged routing resolution #395, DESIGN selects exactly one allowed prospective route:

`SEPARATELY_JUSTIFIED_BASELINE_FAMILY -> CROSS_SECTIONAL_MOMENTUM_SINGLE_BASELINE`

The alternative `NO_UPSTREAM_VALIDATED_FACTOR -> INCONCLUSIVE_INSUFFICIENT_SUPPORT` route is not selected and cannot be substituted later under this research ID.

This route choice uses no 0075/0084 scientific payload or result. It is justified prospectively by the generic economic hypothesis that relative return persistence can reflect slow information diffusion, heterogeneous attention and delayed portfolio rebalancing across tradable crypto assets. This is an independently posed baseline mechanism, not an inherited 0075/0084 factor claim.

## 2. Candidate and trial ceiling

- Exactly one scientific candidate family is allowed: cross-sectional price momentum.
- Total selectable route/candidate budget remains exactly `1`.
- No reversal, value, carry, funding, basis, liquidity, network, volatility, residual-momentum, composite or ensemble alternative may enter 0076.
- No parameter grid, model family search, factor weighting search or post-result replacement is allowed.
- Stage3 must freeze one exact parameterization before any controlled history; that parameterization is not a candidate search because no competing parameterization may be evaluated.

## 3. Signal architecture

Stage3 must instantiate exactly one causal price-momentum score from lagged point-in-time closes:

- score is a trailing return ending strictly before the executable decision return begins;
- decision-session close may not leak into a same-session executable return;
- no future constituent membership, future delisting knowledge or future liquidity status may affect the score;
- no outcome-aware winsorization, residualization or sign flip is permitted;
- ranking is cross-sectional on the contemporaneously eligible universe only.

Stage3 must numerically freeze the single lookback, any skip interval, rebalance cadence, minimum-history requirement, missing/stale treatment and tie rule. No alternate window may later be evaluated.

## 4. Universe and portfolio architecture

Stage3 must freeze a point-in-time tradable crypto universe and exact source identities before controlled history. Stablecoins, wrapped duplicates and assets not executable under the frozen venue/data contract must fail eligibility prospectively.

The portfolio architecture is fixed in class:

1. rank eligible assets by the single momentum score;
2. create one long basket from the highest-ranked tail and one short basket from the lowest-ranked tail;
3. use deterministic equal weights within each leg before neutrality adjustment;
4. target zero net dollar exposure;
5. enforce a prospectively frozen lagged market-beta residual tolerance using only information available before execution;
6. enforce per-asset and concentration caps;
7. prohibit leverage beyond the preregistered gross cap;
8. if the eligible cross-section cannot support both tails and neutrality constraints, the rebalance is undefined/fail-closed rather than rescued with a different universe or cut.

Stage3 must numerically freeze basket cuts, gross cap, beta estimator/lookback/tolerance, cap rules and rebalance timing.

## 5. Economic accounting

The exactly-once scientific execution must calculate ordered executable PnL and persist both gross and net evidence. Stage3 must freeze:

- execution-price convention and information lag;
- fees, spread/slippage and turnover accounting;
- short borrow availability treatment and borrow financing cost;
- realistic `C1` and stressed `C2` implementation scenarios plus declared sensitivity multipliers;
- turnover, NAV, CAGR, volatility, Sharpe, Sortino, drawdown, Calmar and tail metrics;
- residual beta, gross/net exposure, capacity/concentration, cost break-even and stressed borrow-unavailable diagnostics.

C0 theoretical economics alone can never PASS.

## 6. Statistical and robustness architecture

Candidate count is one, so there is no hidden multi-factor selection step. Stage3 must still freeze dependence-aware inference and robustness before history, including:

- deterministic block/bootstrap method, replicate count and seed;
- PSR/DSR treatment appropriate to one declared candidate;
- PBO only if mathematically supported by the realized return matrix, otherwise preregistered `NOT_EVALUATED` semantics;
- year/regime/asset/theme leave-out rules;
- concentration and cost-break-even gates;
- minimum support rules for tradable cross-sections and short availability.

## 7. Terminal classifications

Stage3 must freeze exact numerical gates, but meanings are already fixed:

- `PASS`: the one frozen baseline completes valid exactly-once execution and satisfies all realistic/stressed economics, neutrality, support, robustness, concentration and cost gates.
- `FAIL`: execution is valid and adequately supported, but the one baseline fails one or more frozen economic/robustness gates.
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`: only for prospectively defined insufficient support or mathematically undefined required inference, never for disappointing performance.
- `INVALID_EXECUTION`: identity/hash/read-count/lookahead/universe/candidate-count/neutrality/cost/borrow/persistence/exactly-once drift.

No result-informed rescue, alternate momentum window, reversal fallback, new factor, source substitution, history extension, rerun, retune or recomputation is allowed after scientific exposure.

## 8. Implementation-completeness requirement

Because 0084 failed after marker durability due an incomplete frozen execution interface, 0076 adds an explicit pre-attempt design requirement: Stage4 and Stage5 must demonstrate, using synthetic/nonhistorical fixtures only, a complete end-to-end payload-to-portfolio-to-statistics-to-terminal-classification execution path. Stage7 cannot PASS if Stage8 would still require a new scientific harness or adapter.

## 9. Current irreversible budgets

- attempt: `0/1`
- controlled scientific-history reads: `0`
- scientific engine: `0/1`
- scientific source-network fetches: `0`
- scientific values exposed: `false`
- production/signature/order authority: `false`

## 10. Exact next step

After this Stage2 DESIGN merges, create a separate Stage3 PREREGISTRATION branch. Freeze one and only one numerical realization of this baseline plus exact data/source identities, support rules, accounting formulas, statistical gates and execution budgets before any controlled history.
