# CARRY-PNL-0031 — naive same-venue delta-neutral carry

Decision: **qualified for a separately preregistered portfolio-stack test** under the frozen gate. This is mechanism qualification on Binance historical data, not direct Hyperliquid implementation evidence.

## Frozen baseline

Five assets were always included: BTC, ETH, SOL, BNB and XRP. Each carried a +0.10 Binance spot leg and a -0.10 Binance USD-M perpetual leg, for gross 1.0 and net directional exposure 0.0 at each daily rebalance. No funding sign filter, asset selection, Top-K, basis threshold, leverage search or dynamic weighting was allowed.

The valid window is 2020-09-15 through 2026-07-30. Internal monthly-archive gaps in SOL and XRP perpetual daily bars were repaired only from exact official Binance daily 1d archives under the preregistered rule. No required leg gaps remained. Funding-event coverage was 100% across 10,725 active symbol-days, using 32,250 official recorded settlement events.

## Canonical net result

At 5 bps per absolute notional change, including gross=1 initial entry and daily notional-drift rebalancing:

- $10,000 -> **$11,719.83**
- CAGR **2.740%**
- max drawdown **-7.005%**
- annualized volatility **1.904%**
- Sharpe **1.428**
- Calmar **0.391**
- cumulative turnover **64.394**

Cost stress remained positive: 10 bps CAGR **2.178%**, Sharpe **1.138**; 20 bps CAGR **1.063%**, Sharpe **0.561**.

## Mechanism attribution

The return is genuinely funding-led rather than hidden directional beta:

- funding-only, no cost: CAGR **3.701%**, Sharpe **3.668**;
- spot-perp price-spread-only, no cost: CAGR **-0.381%**, Sharpe **-0.301**;
- cumulative additive recorded funding contribution: **+21.338%**;
- cumulative additive price-spread contribution: **-2.195%**.

Funding contribution by asset was approximately BTC +6.554%, ETH +7.302%, SOL +0.059%, BNB -0.252%, XRP +7.676%. BNB remained in the frozen five-asset baseline despite negative contribution; removing it after observing the result is not authorized.

## Diversification / crisis behavior

Versus canonical BRRK on common history:

- daily correlation **-0.098**;
- monthly correlation **0.472**;
- mean carry return on BRRK worst-decile days **+0.0097%**;
- compounded carry return across those worst-decile days **+1.303%**;
- mean carry return on the worst 20 BRRK days **+0.0185%**.

All four preregistered qualification gates passed: positive net economics, positive funding mechanism contribution, daily correlation below 0.50, and nonnegative mean return on BRRK worst-decile days.

## Important limitation before stacking

Daily close basis diagnostics contain large negative outliers, notably SOL around **-16.9%** and XRP around **-6.7%**. These do not invalidate the frozen 0031 result automatically, but they require a post-hoc source/attribution audit before the sleeve is combined with BRRK. That audit may verify timestamps, source files and PNL influence; it may not remove assets or retune the strategy based on the observed result.

Any eventual Hyperliquid deployment also requires a separate implementation study covering actual spot availability, collateral, perp funding, basis, fees, slippage and execution. Binance 0031 qualifies the carry mechanism; it does not prove Hyperliquid deployability.
