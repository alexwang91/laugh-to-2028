# BRRK Multi-Horizon Trend Vol-Target 0085 — BUILD

Gate: `BUILD` = IMPLEMENTATION + NONHISTORICAL QUALIFICATION.

Status: `IMPLEMENTED_SYNTHETIC_QUALIFICATION_PENDING_CI`.

This gate performs zero controlled scientific/history payload reads and consumes zero controlled attempt budget.

## Mechanical implementation clarification

SPEC_FREEZE required BUILD to resolve portfolio-volatility mechanics before controlled history. The deterministic interpretation is now frozen:

1. For each decision date, compute each asset's daily log-return series using closes available through that date.
2. For trend-active assets, form inverse-vol raw weights from trailing 20-session annualized asset log-return volatility and normalize them to sum to 1.
3. Using those normalized active weights as fixed coefficients, compute the trailing 20-session weighted portfolio log-return series from the same 20 return observations available at the decision date.
4. Annualize the sample standard deviation of that 20-session weighted series by `sqrt(365)`.
5. Risky gross scaler is `min(1.0, 0.25 / portfolio_vol20)` when portfolio volatility is finite and positive; otherwise risky gross is zero.
6. Final asset weights are normalized inverse-vol weights multiplied by that scaler. No asset weight may be negative and total risky gross may not exceed 1.0.

This selects no scientific parameter and inspects no controlled value. It only removes an implementation ambiguity explicitly delegated to BUILD by SPEC_FREEZE.

## Frozen execution interface

The common runner calls `TrendVolTargetEngine.execute(context)` exactly once. `context.sources` must contain these UTF-8 JSON objects:

- `btc_daily.json`
- `eth_daily.json`
- `sol_daily.json`

Each required object is a JSON array of records `{ "date": "YYYY-MM-DD", "close": positive finite number }`, strictly increasing with no duplicate dates.

Optional ARM-bound inputs are:

- `cash_daily.json`: JSON array `{ "date": "YYYY-MM-DD", "return": finite decimal return }`;
- `canonical_brrk_daily.json`: JSON array `{ "date": "YYYY-MM-DD", "return": finite decimal return }`.

If `cash_daily.json` is absent at ARM, cash return is exactly zero. If `canonical_brrk_daily.json` is absent, canonical-BRRK correlation is reported unavailable and cannot itself invalidate an otherwise formable study. ARM must freeze the exact presence/absence and identities before RUN. Unknown source filenames fail closed.

## Causal timing

A target computed with session `t` close is applied only to `t -> t+1` asset return. Turnover cost is charged when the next-session target is established. The implementation does not future-fill missing closes.

## Qualification scope

Synthetic/nonhistorical tests must cover:

- exact 3-of-4 signal activation and inactivity;
- 20-session inverse-vol allocation;
- the frozen portfolio-volatility clarification and 25% target;
- gross cap <= 1 and no shorts;
- t-close to next-session timing;
- 10/20/30 bps turnover cost monotonicity;
- empty-active-set cash behavior;
- duplicate/out-of-order dates, non-finite/invalid prices and unknown execution-interface objects failing closed;
- support below 730 returning `INCONCLUSIVE_INSUFFICIENT_SUPPORT` only when execution is valid;
- deterministic repeated execution on identical synthetic context;
- output JSON containing all preregistered primary metrics, robustness diagnostics, benchmark metrics, gate booleans and exactly one allowed terminal classification.

BUILD may prove mechanics only. It cannot claim scientific PASS/FAIL on controlled history.

## What did not change

- No 0085 controlled payload value was read.
- Attempt remains `0/1`; controlled payload reads remain `0`; scientific engine budget remains unconsumed; scientific source-network fetches remain `0`.
- The single BTC/ETH/SOL candidate, 20/60/120/240 horizons, 3-of-4 threshold, vol20 estimator, 25% target, gross cap 1.0, 10/20/30 bps costs, benchmarks, support floor and all PASS gates remain unchanged.
- No result-informed rescue, parameter search, alternate implementation winner selection or source substitution occurred.
- 0074 remains immutable `INVALID_EXECUTION`; 0076 remains sealed at the pre-marker read-boundary incident; 0072/0073 remain closed/paused and 0083 remains immutable FAIL.
- `CONTROLLED_RESEARCH_RUNNER_V1` ordering and failure semantics are unchanged.
- Production/signature/order/withdrawal/transfer authority remains false.

## Next gate

After exact-head mandatory CI proves this BUILD terminal green and the PR merges cleanly, 0085 may enter `ARM` only. ARM must bind exact controlled object identities, declared hashes/sizes, source/read budgets, optional cash/canonical presence, exact runner qualification identity and zero-result metadata-only preflight. No controlled payload may be opened during ARM.
