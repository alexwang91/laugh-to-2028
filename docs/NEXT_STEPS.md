# Next Steps

当前原则：**机制验证、组合验证、工具身份验证和部署授权必须分开。已经失败的 alpha 组合不能通过同一窗口上的新阈值继续被救；一个 spot 资产也不能因为历史 PNL 更漂亮就被自动认定为合法替代品。**

## Completed research gates

### PIT-DISP-0015

Broad point-in-time dispersion contains real risk information, but its upside opportunity cost prevents promotion. Fixed-panel DISP-0014 is materially selection-sensitive.

Decision: `BRRK-0011` remains canonical baseline; no PIT-DISP-0015 tuning.

### PIT-ALPHA-0016 / AUDIT-0017 / PIT-ALPHA-0018

The dynamic cross-sectional rank contains information, and eligibility-based persistence reduces churn, but the broad portfolio remains unacceptable:

- PIT-ALPHA-0018 CAGR: **16.62%**;
- MDD: **-66.86%**;
- 2025 return: **-10.03%**;
- 2026 through Aug 2: **-11.06%**;
- 2025+ CAGR: **-13.11%**.

Decision: dynamic-alpha portfolio rejected; no threshold rescue on this window.

### FUNDING-DATA-0001 / FUNDING-CROSSVENUE-0002

Official Binance and Hyperliquid funding sources were validated. Binance can serve only as a sign/regime or stress proxy, not a Hyperliquid level point estimate.

### FUNDING-PNL-0003

Frozen BRRK held weights were charged native Hyperliquid funding without changing targets.

Common 2023-06-18 through 2026-07-31 window:

| Scenario | CAGR | MDD |
|---|---:|---:|
| Price-only | 65.37% | -33.72% |
| Hyperliquid all-perp | **44.08%** | **-37.04%** |

Decision: default all-perp implementation for gross≤1 long exposure is rejected.

### ROUTER-DATA-0004

Current Hyperliquid spot/perp metadata and L2 books were audited at fixed notionals.

- BTC: verified through the preregistered official BTC→UBTC UI remap;
- ETH: UETH exists but remains `candidate_wrapped_or_bridged`;
- SOL: USOL exists but remains `candidate_wrapped_or_bridged`;
- BNB: no deterministic direct-USDC spot candidate;
- XRP: no deterministic direct-USDC spot candidate.

Decision: BTC is the only target currently eligible for a strict spot-first shadow implementation.

### ROUTER-PNL-0005

Exploratory post-audit accounting applied zero funding only to currently verified spot assets while preserving the frozen BRRK price path and native perp funding for all other assets.

| Implementation | CAGR | MDD | Sharpe |
|---|---:|---:|---:|
| Hyperliquid all-perp | 44.08% | -37.04% | 1.046 |
| **Strict BTC-spot router accounting** | **56.20%** | **-34.95%** | **1.229** |
| Price-only upper bound | 65.37% | -33.72% | 1.355 |

This result is **not production-promotion evidence**. Historical spot fees, basis, spread, slippage and fills were not fabricated.

Mechanical counterfactual attribution shows:

- BTC + ETH spot: 57.74% CAGR;
- BTC + SOL spot: **63.06%**;
- BTC + ETH + SOL spot: **64.66%**.

These figures do not authorize UETH or USOL routing. They only identify where historical funding drag came from.

---

## Research stopping rule for dynamic alpha

The current alpha line stops here.

Do **not** add any of the following to rescue PIT-ALPHA-0018 on the same historical window:

- exit-rank threshold;
- minimum holding period;
- weekly/monthly rebalance schedule;
- higher listing-age or liquidity threshold;
- named winner universe;
- dispersion, funding, covariance, LPM or generic volatility gate;
- leverage;
- PNL-selected parameter family.

A future alpha experiment requires genuinely new evidence or a separately justified external mechanism.

---

## P0 — Unit identity / custody / redemption audit

This is now the primary implementation-research gate.

### Goal

Determine whether UETH and USOL can legitimately represent the frozen ETH and SOL economic exposures in a spot-first Hyperliquid router.

### Required evidence

1. authoritative issuer / protocol documentation for UETH and USOL;
2. exact underlying backing and economic identity;
3. mint, deposit, withdrawal and redemption mechanics;
4. custody / bridge / smart-contract / validator or guardian dependencies;
5. redemption fees, limits, latency and availability;
6. depeg, halt, bridge-failure and contract-upgrade failure modes;
7. Hyperliquid's official UI / API mapping, if any, from ETH/SOL exposure to the Unit representation;
8. deterministic treatment when the representation cannot be redeemed or traded;
9. any additional price tracking or basis risk relative to the intended underlying.

### Prohibited

- no promotion because the ticker resembles ETH/SOL;
- no promotion because ROUTER-PNL-0005 counterfactual CAGR is higher;
- no PNL-selected identity rule;
- no silent assumption that wrapped/bridged/custodied assets are equivalent to native assets.

Passing this gate authorizes only a later shadow-routing test, not production.

---

## P1 — Strict Spot/Perp forward shadow router

### Initial deterministic rule

```text
verified long spot capacity → spot
unverified / unavailable long exposure → perp
short exposure → perp
leverage above cash-backed spot capacity → perp
```

Until P0 changes classifications:

```text
BTC → spot candidate for shadow execution
ETH → perp
SOL → perp
BNB → perp
XRP → perp
```

### Required forward evidence

For every rebalance decision persist:

- research target weight and target notional;
- chosen instrument and exact reason;
- live spot/perp funding;
- mark/oracle/mid and spot-perp basis;
- best bid/ask and spread;
- L2 book depth and expected VWAP at target notional;
- maker/taker fee assumption actually used;
- order parameters;
- submitted / resting / cancelled / rejected / filled state;
- realized fill price and slippage;
- post-trade holdings and residual target error;
- fallback decision if spot is insufficient or unavailable.

No historical liquidity or basis series may be inferred from the single ROUTER-DATA-0004 snapshot.

---

## P2 — Hyperliquid execution hardening

Priorities:

1. derive size precision from live metadata;
2. read account, order and position state before and after every trade;
3. reconcile reversal close and reopen fills before submitting the second leg;
4. handle partial, resting, rejected and cancelled orders explicitly;
5. slice large deltas or use controlled TWAP;
6. persist idempotency keys, decisions, orders and fills;
7. simulate target-notional L2 VWAP and apply a deterministic slippage veto;
8. route by verified instrument, side and capacity;
9. add reduce-only emergency protection and a kill switch;
10. secure status / cron endpoints;
11. require explicit mainnet confirmation and hard leverage caps;
12. prove deterministic parity between research target JSON and actual orders.

No production promotion until reconciliation and failure-path tests pass on testnet / shadow.

---

## P3 — Forward shadow evidence

Continue accumulating without retuning trading targets:

- daily BRRK-0011 target;
- Hyperliquid hourly funding;
- spot/perp basis;
- mark/oracle premium;
- L2 book depth;
- expected and realized VWAP/slippage;
- fees;
- routing decision;
- order/fill outcome;
- position reconciliation;
- operational failure events.

Only forward evidence can authorize liquidity, basis or funding variables as active routing controls beyond the frozen deterministic rule.

---

## P4 — Leverage last

Do not reconsider gross 1.30–1.50 until:

- funding-aware implementation economics are validated;
- spot/perp routing is deterministic;
- spot identity/custody risks are understood;
- execution reconciliation is reliable;
- L2 slippage controls are implemented;
- kill switches and failure paths are tested;
- sufficient BRRK shadow evidence has accumulated.

## Canonical position

Until those gates are passed:

- `BRRK-0011` remains the directional research baseline;
- PIT dispersion remains diagnostic;
- dynamic alpha ranks remain research evidence, not target weights;
- all-perp default remains rejected;
- BTC-only strict spot routing is an **implementation/shadow candidate**, not production-ready;
- `56.20%` is a funding-only accounting result, not a deployable net-return claim;
- Plan B remains testnet/shadow;
- no increase in leverage is authorized.
